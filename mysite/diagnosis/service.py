import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import torch
import torch.nn.functional as F

from .model import CharHybridDiagnosisModel
from .pipeline import LexiconMatcher, augment_with_symptoms, default_artifact_dir, encode_text, normalize_question_text

DEFAULT_CHECKPOINT_PATH = default_artifact_dir() / "symptom_diagnosis_model.pt"


class SymptomDiagnosisService:
    def __init__(self, checkpoint_path=None, device=None):
        self.checkpoint_path = Path(checkpoint_path or DEFAULT_CHECKPOINT_PATH)
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Diagnosis checkpoint not found: {self.checkpoint_path}. "
                "Run `python train_symptom_diagnosis.py` first."
            )

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)

        self.config = checkpoint["config"]
        self.vocab = checkpoint["vocab"]
        self.labels = checkpoint["labels"]
        self.symptom_terms = checkpoint["symptom_terms"]
        self.symptom_matcher = LexiconMatcher(self.symptom_terms)

        self.model = CharHybridDiagnosisModel(
            vocab_size=len(self.vocab),
            num_classes=len(self.labels),
            embed_dim=self.config["embed_dim"],
            rnn_hidden_size=self.config["rnn_hidden_size"],
            cnn_channels=self.config["cnn_channels"],
            dropout=self.config["dropout"],
            kernel_sizes=tuple(self.config["kernel_sizes"]),
        ).to(self.device)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()

    def predict(self, raw_text, top_k=3):
        normalized_text = normalize_question_text(raw_text)
        if not normalized_text:
            raise ValueError("Empty symptom description.")

        model_text, matched_symptoms = augment_with_symptoms(
            normalized_text,
            symptom_matcher=self.symptom_matcher,
            max_hints=self.config["max_symptom_hints"],
        )
        input_ids = torch.tensor(
            [encode_text(model_text, self.vocab, self.config["max_length"])],
            dtype=torch.long,
            device=self.device,
        )

        with torch.no_grad():
            logits = self.model(input_ids)
            temperature = float(self.config.get("inference_temperature", 1.0))
            if temperature > 0 and temperature != 1.0:
                logits = logits / temperature
            probabilities = F.softmax(logits, dim=-1).squeeze(0)

        top_k = min(top_k, len(self.labels))
        scores, indices = torch.topk(probabilities, k=top_k)
        predictions = []
        for score, index in zip(scores.tolist(), indices.tolist()):
            predictions.append(
                {
                    "disease": self.labels[index],
                    "probability": round(score * 100, 2),
                }
            )

        return {
            "normalized_text": model_text,
            "matched_symptoms": matched_symptoms,
            "predictions": predictions,
        }


@lru_cache(maxsize=1)
def load_diagnosis_service(checkpoint_path=None):
    target_path = Path(checkpoint_path) if checkpoint_path else DEFAULT_CHECKPOINT_PATH
    return SymptomDiagnosisService(checkpoint_path=target_path)
