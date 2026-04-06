from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"

DEFAULT_EXCLUDED_LABELS = {
    "维生素B",
    "分娩",
    "温热",
    "水过多",
    "肿胀",
    "阴虚",
    "阳虚",
    "肾虚",
    "阴虚火旺",
    "内热",
    "风寒",
    "内分泌失调",
    "妇科炎症",
    "妇科疾病",
    "皮肤病",
    "肿瘤",
    "癌症",
    "心脏病",
    "肝病",
    "性病",
    "神经衰弱",
    "人工流产",
    "早产",
    "疤痕",
    "自然流产",
    "过敏性皮肤病",
}

DEFAULT_LABEL_ALIASES = {
    "上呼吸道感染": "感冒",
    "呼吸道感染": "感冒",
    "普通感冒": "感冒",
    "急性上呼吸道感染": "感冒",
    "内痔": "痔疮",
    "外痔": "痔疮",
    "混合痔": "痔疮",
    "痔核": "痔疮",
    "早孕反应": "早孕",
    "妊娠反应": "早孕",
}

_SPACE_RE = re.compile(r"\s+")
_QUESTION_CLEAN_RE = re.compile(r"[^0-9a-zA-Z\u4e00-\u9fff，。！？、；：,.!?%℃+\-/（）() ]")
_CLAUSE_SPLIT_RE = re.compile(r"[。；;！？?!\n]")
_POSITIVE_CUES = (
    "考虑",
    "可能",
    "诊断",
    "提示",
    "属于",
    "是",
    "为",
    "患有",
    "得了",
    "符合",
    "引起",
    "导致",
    "出现",
)
_NEGATIVE_CUES = (
    "服用",
    "口服",
    "使用",
    "应用",
    "补充",
    "注射",
    "治疗",
    "检查",
    "复查",
    "手术",
    "药",
    "药物",
)


@dataclass
class DatasetBuildResult:
    frame: pd.DataFrame
    summary: dict[str, int | float]
    disease_terms: list[str]
    symptom_terms: list[str]


class LexiconMatcher:
    def __init__(self, terms: Iterable[str]) -> None:
        cleaned_terms = sorted(
            {str(term).strip() for term in terms if str(term).strip()},
            key=len,
            reverse=True,
        )
        self.terms = [term for term in cleaned_terms if len(term) >= 2]
        self.by_first_char: dict[str, list[str]] = defaultdict(list)
        for term in self.terms:
            self.by_first_char[term[0]].append(term)
        for key in list(self.by_first_char.keys()):
            self.by_first_char[key].sort(key=len, reverse=True)

    def extract_matches(self, text: str) -> list[str]:
        source = str(text)
        found: list[str] = []
        seen: set[str] = set()
        for ch in dict.fromkeys(source):
            for term in self.by_first_char.get(ch, []):
                if term not in seen and term in source:
                    found.append(term)
                    seen.add(term)
        found.sort(key=lambda term: (source.find(term), -len(term), term))
        return found


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def site_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_dataset_dir() -> Path:
    return site_root() / "dataset"


def default_disease_dict_path() -> Path:
    return workspace_root() / "Cut" / "dict" / "disease.txt"


def default_symptom_dict_path() -> Path:
    return workspace_root() / "Cut" / "dict" / "symptom.txt"


def default_artifact_dir() -> Path:
    return site_root() / "diagnosis_artifacts"


def read_lexicon(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def normalize_label_name(label: str) -> str:
    normalized = str(label).strip().replace(" ", "")
    normalized = normalized.replace("（", "(").replace("）", ")")
    return normalized


def canonicalize_label(label: str, label_aliases: Mapping[str, str] | None = None) -> str:
    alias_map = label_aliases or DEFAULT_LABEL_ALIASES
    normalized = normalize_label_name(label)
    seen: set[str] = set()
    while normalized in alias_map and normalized not in seen:
        seen.add(normalized)
        normalized = normalize_label_name(alias_map[normalized])
    return normalized


def normalize_question_text(text: str) -> str:
    normalized = str(text).replace("\u3000", " ").replace("\xa0", " ")
    normalized = normalized.replace("\r", " ").replace("\n", " ").lower().strip()
    normalized = re.sub(r"\d+(?:\.\d+)?", "0", normalized)
    normalized = _QUESTION_CLEAN_RE.sub(" ", normalized)
    return _SPACE_RE.sub(" ", normalized).strip()


def augment_with_symptoms(text: str, symptom_matcher: LexiconMatcher, max_hints: int = 6) -> tuple[str, list[str]]:
    matched_symptoms = symptom_matcher.extract_matches(text)[:max_hints]
    if not matched_symptoms:
        return text, []
    suffix = " 症状提示 " + " ".join(matched_symptoms)
    return f"{text}{suffix}".strip(), matched_symptoms


def _score_disease_in_clause(clause: str, disease_name: str, clause_rank: int) -> float:
    start = clause.find(disease_name)
    if start < 0:
        return -1.0
    window = clause[max(0, start - 8): start + len(disease_name) + 8]
    score = len(disease_name) * 0.05
    if any(cue in window for cue in _POSITIVE_CUES):
        score += 2.0
    if start <= 18:
        score += 0.6
    if any(cue in window for cue in _NEGATIVE_CUES):
        score -= 1.2
    score += max(0.0, 0.45 - clause_rank * 0.15)
    return score


def extract_primary_disease(answer_text: str, disease_matcher: LexiconMatcher) -> str | None:
    text = str(answer_text).strip()
    clauses = [clause.strip() for clause in _CLAUSE_SPLIT_RE.split(text) if clause.strip()]
    best_name = None
    best_score = float("-inf")

    for clause_rank, clause in enumerate(clauses[:3]):
        matches = disease_matcher.extract_matches(clause)
        for disease_name in matches:
            score = _score_disease_in_clause(clause, disease_name, clause_rank)
            if score > best_score:
                best_name = disease_name
                best_score = score

    if best_name:
        return best_name

    fallback_matches = disease_matcher.extract_matches(text)
    return fallback_matches[0] if fallback_matches else None


def build_weakly_labeled_dataset(
    dataset_dir: Path | None = None,
    disease_dict_path: Path | None = None,
    symptom_dict_path: Path | None = None,
    min_vote_share: float = 0.5,
    min_label_samples: int = 100,
    max_symptom_hints: int = 6,
    excluded_labels: Iterable[str] | None = None,
    label_aliases: Mapping[str, str] | None = None,
) -> DatasetBuildResult:
    dataset_dir = dataset_dir or default_dataset_dir()
    disease_dict_path = disease_dict_path or default_disease_dict_path()
    symptom_dict_path = symptom_dict_path or default_symptom_dict_path()

    question_df = pd.read_csv(dataset_dir / "question.csv")
    answer_df = pd.read_csv(dataset_dir / "answer.csv")
    merged_df = answer_df.merge(question_df, on="question_id", how="inner", suffixes=("_answer", "_question"))

    excluded_label_set = {normalize_label_name(label) for label in (excluded_labels or DEFAULT_EXCLUDED_LABELS)}
    canonical_label_aliases = {
        normalize_label_name(source): normalize_label_name(target)
        for source, target in (label_aliases or DEFAULT_LABEL_ALIASES).items()
    }
    disease_terms = read_lexicon(disease_dict_path)
    symptom_terms = read_lexicon(symptom_dict_path)
    disease_matcher = LexiconMatcher(disease_terms)
    symptom_matcher = LexiconMatcher(symptom_terms)

    question_votes: dict[int, Counter[str]] = defaultdict(Counter)
    question_texts: dict[int, str] = {}
    skipped_excluded_labels = 0
    merged_answer_labels = 0

    for row in merged_df.itertuples(index=False):
        raw_label = extract_primary_disease(row.content_answer, disease_matcher)
        if not raw_label:
            continue
        label = canonicalize_label(raw_label, canonical_label_aliases)
        if label != normalize_label_name(raw_label):
            merged_answer_labels += 1
        if label in excluded_label_set:
            skipped_excluded_labels += 1
            continue
        question_votes[row.question_id][label] += 1
        question_texts[row.question_id] = str(row.content_question)

    rows: list[dict[str, object]] = []
    filtered_by_vote = 0
    for question_id, votes in question_votes.items():
        label, vote_count = votes.most_common(1)[0]
        total_votes = sum(votes.values())
        vote_share = vote_count / total_votes if total_votes else 0.0
        if vote_share < min_vote_share:
            filtered_by_vote += 1
            continue

        normalized_question = normalize_question_text(question_texts[question_id])
        if not normalized_question:
            continue

        model_text, matched_symptoms = augment_with_symptoms(
            normalized_question,
            symptom_matcher=symptom_matcher,
            max_hints=max_symptom_hints,
        )

        rows.append(
            {
                "question_id": question_id,
                "label": label,
                "vote_count": vote_count,
                "vote_share": vote_share,
                "question_text": normalized_question,
                "model_text": model_text,
                "matched_symptoms": "|".join(matched_symptoms),
            }
        )

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("No diagnosis samples were built from the current dataset.")

    raw_label_count = int(frame["label"].nunique())
    label_counts = frame["label"].value_counts()
    valid_labels = label_counts[label_counts >= min_label_samples].index
    frame = frame[frame["label"].isin(valid_labels)].copy()
    frame = frame.sort_values(["label", "question_id"]).reset_index(drop=True)
    filtered_by_label_frequency = int(len(rows) - len(frame))

    summary = {
        "question_count": int(len(question_df)),
        "answer_count": int(len(answer_df)),
        "merged_answer_count": int(len(merged_df)),
        "raw_voted_question_count": int(len(question_votes)),
        "vote_filtered_question_count": int(filtered_by_vote),
        "excluded_answer_label_count": int(skipped_excluded_labels),
        "merged_answer_label_count": int(merged_answer_labels),
        "raw_label_count": raw_label_count,
        "label_frequency_filtered_count": filtered_by_label_frequency,
        "training_sample_count": int(len(frame)),
        "label_count": int(frame["label"].nunique()),
    }
    return DatasetBuildResult(
        frame=frame,
        summary=summary,
        disease_terms=disease_terms,
        symptom_terms=symptom_terms,
    )


def build_char_vocab(texts: Iterable[str], min_freq: int = 2, max_size: int = 4096) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(str(text))

    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for char, count in counter.most_common():
        if count < min_freq or len(vocab) >= max_size:
            break
        if char not in vocab:
            vocab[char] = len(vocab)
    return vocab


def encode_text(text: str, vocab: dict[str, int], max_length: int) -> list[int]:
    unk_id = vocab[UNK_TOKEN]
    pad_id = vocab[PAD_TOKEN]
    tokens = [vocab.get(char, unk_id) for char in str(text)[:max_length]]
    if len(tokens) < max_length:
        tokens.extend([pad_id] * (max_length - len(tokens)))
    return tokens


def prepare_inference_text(raw_text: str, symptom_terms: Iterable[str], max_symptom_hints: int = 6) -> tuple[str, list[str]]:
    normalized_text = normalize_question_text(raw_text)
    symptom_matcher = LexiconMatcher(symptom_terms)
    return augment_with_symptoms(normalized_text, symptom_matcher, max_hints=max_symptom_hints)
