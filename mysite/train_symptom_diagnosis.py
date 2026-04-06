from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, TensorDataset

from diagnosis.model import CharHybridDiagnosisModel
from diagnosis.pipeline import (
    build_char_vocab,
    build_weakly_labeled_dataset,
    default_artifact_dir,
    encode_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the symptom-to-disease diagnosis module.")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=160)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--max-vocab-size", type=int, default=4096)
    parser.add_argument("--min-char-freq", type=int, default=2)
    parser.add_argument("--min-label-samples", type=int, default=200)
    parser.add_argument("--min-vote-share", type=float, default=0.5)
    parser.add_argument("--max-symptom-hints", type=int, default=6)
    parser.add_argument("--embed-dim", type=int, default=128)
    parser.add_argument("--rnn-hidden-size", type=int, default=128)
    parser.add_argument("--cnn-channels", type=int, default=96)
    parser.add_argument("--dropout", type=float, default=0.35)
    parser.add_argument("--learning-rate", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--label-smoothing", type=float, default=0.0)
    parser.add_argument("--inference-temperature", type=float, default=1.0)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--output-dir", type=str, default=str(default_artifact_dir()))
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_arrays(frame, vocab: dict[str, int], max_length: int) -> tuple[np.ndarray, np.ndarray]:
    features = np.asarray(
        [encode_text(text, vocab, max_length=max_length) for text in frame["model_text"]],
        dtype=np.int64,
    )
    labels = frame["label_id"].to_numpy(dtype=np.int64)
    return features, labels


def make_loader(
    inputs: np.ndarray,
    labels: np.ndarray,
    batch_size: int,
    shuffle: bool = False,
) -> DataLoader:
    dataset = TensorDataset(torch.tensor(inputs, dtype=torch.long), torch.tensor(labels, dtype=torch.long))
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=0)


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    top_k: int,
) -> dict[str, float]:
    model.eval()
    loss_sum = 0.0
    total = 0
    top_k_hits = 0
    y_true: list[int] = []
    y_pred: list[int] = []

    with torch.no_grad():
        for batch_inputs, batch_labels in loader:
            batch_inputs = batch_inputs.to(device)
            batch_labels = batch_labels.to(device)

            logits = model(batch_inputs)
            loss = criterion(logits, batch_labels)
            loss_sum += loss.item() * batch_labels.size(0)
            total += batch_labels.size(0)

            predictions = logits.argmax(dim=1)
            top_indices = torch.topk(logits, k=min(top_k, logits.size(1)), dim=1).indices
            top_k_hits += top_indices.eq(batch_labels.unsqueeze(1)).any(dim=1).sum().item()

            y_true.extend(batch_labels.cpu().tolist())
            y_pred.extend(predictions.cpu().tolist())

    return {
        "loss": loss_sum / max(total, 1),
        "accuracy": accuracy_score(y_true, y_pred),
        "top_k_accuracy": top_k_hits / max(total, 1),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)

    print("========== 1. Build weakly labeled diagnosis dataset ==========")
    build_result = build_weakly_labeled_dataset(
        min_vote_share=args.min_vote_share,
        min_label_samples=args.min_label_samples,
        max_symptom_hints=args.max_symptom_hints,
    )
    frame = build_result.frame.copy()

    if args.max_samples and args.max_samples < len(frame):
        frame, _ = train_test_split(
            frame,
            train_size=args.max_samples,
            stratify=frame["label"],
            random_state=args.seed,
        )
        frame = frame.reset_index(drop=True)

    label_counts = frame["label"].value_counts()
    labels = label_counts.index.tolist()
    label_to_index = {label: index for index, label in enumerate(labels)}
    frame["label_id"] = frame["label"].map(label_to_index)

    print(f"Samples: {len(frame)}")
    print(f"Labels: {len(labels)}")
    print(f"Top labels: {label_counts.head(10).to_dict()}")

    print("========== 2. Build character vocabulary ==========")
    vocab = build_char_vocab(
        frame["model_text"],
        min_freq=args.min_char_freq,
        max_size=args.max_vocab_size,
    )
    print(f"Vocab size: {len(vocab)}")

    train_frame, temp_frame = train_test_split(
        frame,
        test_size=0.2,
        stratify=frame["label_id"],
        random_state=args.seed,
    )
    val_frame, test_frame = train_test_split(
        temp_frame,
        test_size=0.5,
        stratify=temp_frame["label_id"],
        random_state=args.seed,
    )

    X_train, y_train = build_arrays(train_frame, vocab, args.max_length)
    X_val, y_val = build_arrays(val_frame, vocab, args.max_length)
    X_test, y_test = build_arrays(test_frame, vocab, args.max_length)

    train_loader = make_loader(X_train, y_train, batch_size=args.batch_size, shuffle=True)
    val_loader = make_loader(X_val, y_val, batch_size=args.batch_size)
    test_loader = make_loader(X_test, y_test, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"========== 3. Train diagnosis model on {device} ==========")
    model = CharHybridDiagnosisModel(
        vocab_size=len(vocab),
        num_classes=len(labels),
        embed_dim=args.embed_dim,
        rnn_hidden_size=args.rnn_hidden_size,
        cnn_channels=args.cnn_channels,
        dropout=args.dropout,
    ).to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=args.label_smoothing)
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.6, patience=1)

    best_state = None
    best_epoch = 0
    best_macro_f1 = -1.0
    early_stop_counter = 0
    history: list[dict[str, float | int]] = []

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()
        model.train()
        train_loss_sum = 0.0
        train_total = 0

        for batch_inputs, batch_labels in train_loader:
            batch_inputs = batch_inputs.to(device)
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(batch_inputs)
            loss = criterion(logits, batch_labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_sum += loss.item() * batch_labels.size(0)
            train_total += batch_labels.size(0)

        train_loss = train_loss_sum / max(train_total, 1)
        val_metrics = evaluate(model, val_loader, criterion, device, args.top_k)
        scheduler.step(val_metrics["loss"])

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_top_k_accuracy": val_metrics["top_k_accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
            "learning_rate": optimizer.param_groups[0]["lr"],
            "seconds": round(time.time() - epoch_start, 2),
        }
        history.append(epoch_record)

        print(
            "Epoch "
            f"{epoch:02d} | "
            f"train_loss={train_loss:.4f} | "
            f"val_loss={val_metrics['loss']:.4f} | "
            f"val_acc={val_metrics['accuracy']:.4%} | "
            f"val_top{args.top_k}={val_metrics['top_k_accuracy']:.4%} | "
            f"val_macro_f1={val_metrics['macro_f1']:.4%} | "
            f"lr={optimizer.param_groups[0]['lr']:.6f}"
        )

        if val_metrics["macro_f1"] > best_macro_f1:
            best_macro_f1 = val_metrics["macro_f1"]
            best_epoch = epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            early_stop_counter = 0
            print("  New best checkpoint saved.")
        else:
            early_stop_counter += 1
            if early_stop_counter >= args.patience:
                print(f"  Early stopping triggered after {args.patience} unimproved epochs.")
                break

    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint.")

    model.load_state_dict(best_state)
    test_metrics = evaluate(model, test_loader, criterion, device, args.top_k)
    print("========== 4. Final test metrics ==========")
    print(
        f"Top-1 Accuracy: {test_metrics['accuracy']:.4%}\n"
        f"Top-{args.top_k} Accuracy: {test_metrics['top_k_accuracy']:.4%}\n"
        f"Macro F1: {test_metrics['macro_f1']:.4%}"
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "symptom_diagnosis_model.pt"
    metrics_path = output_dir / "symptom_diagnosis_metrics.json"
    labels_path = output_dir / "symptom_diagnosis_label_counts.csv"

    checkpoint = {
        "config": {
            "max_length": args.max_length,
            "embed_dim": args.embed_dim,
            "rnn_hidden_size": args.rnn_hidden_size,
            "cnn_channels": args.cnn_channels,
            "dropout": args.dropout,
            "kernel_sizes": [2, 3, 4, 5],
            "max_symptom_hints": args.max_symptom_hints,
            "min_vote_share": args.min_vote_share,
            "min_label_samples": args.min_label_samples,
            "label_smoothing": args.label_smoothing,
            "inference_temperature": args.inference_temperature,
            "top_k": args.top_k,
        },
        "state_dict": best_state,
        "vocab": vocab,
        "labels": labels,
        "symptom_terms": build_result.symptom_terms,
        "dataset_summary": build_result.summary,
        "test_metrics": test_metrics,
        "best_epoch": best_epoch,
    }
    torch.save(checkpoint, checkpoint_path)

    metrics_payload = {
        "dataset_summary": build_result.summary,
        "sample_count": int(len(frame)),
        "label_count": int(len(labels)),
        "best_epoch": int(best_epoch),
        "best_val_macro_f1": float(best_macro_f1),
        "test_metrics": {key: float(value) for key, value in test_metrics.items()},
        "history": history,
    }
    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, ensure_ascii=False, indent=2)

    label_counts.rename_axis("label").reset_index(name="count").to_csv(labels_path, index=False, encoding="utf-8-sig")
    print(f"Checkpoint saved to: {checkpoint_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"Label counts saved to: {labels_path}")


if __name__ == "__main__":
    main()
