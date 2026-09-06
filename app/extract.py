"""
文字起こしテキストから、カルテ下書きに必要な情報を抽出する。
"""

import json
import re
from pathlib import Path
from typing import List

from app.models import (
    ExtractedMedication,
    ExtractedSymptom,
    KarteDraft,
)

DICT_DIR = Path(__file__).parent / "dictionaries"

ALLERGY_PATTERNS = [
    r"アレルギー",
    r"アレルギ[ーｰ]?体質",
    r"[はガガ蕁麻疹]が出た",
    r"蕁麻疹",
    r"ラテックス",
    r"金属アレルギー",
]

CHIEF_COMPLAINT_PATTERNS = [
    r"[^。、\n]*(痛い|痛む|しみる|腫れ|気になる|取れた|外れた)[^。、\n]*[。、]?",
]


def _load_dict(filename: str) -> dict:
    with open(DICT_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def extract_symptoms(text: str) -> List[ExtractedSymptom]:
    data = _load_dict("symptoms.json")

    found: List[ExtractedSymptom] = []
    seen_normalized = set()

    for entry in data["entries"]:
        for synonym in entry["synonyms"]:
            if synonym in text:
                if entry["normalized"] not in seen_normalized:
                    found.append(
                        ExtractedSymptom(
                            normalized=entry["normalized"],
                            mentioned_as=synonym,
                        )
                    )
                    seen_normalized.add(entry["normalized"])
                break

    return found


def extract_medications(
    text: str,
) -> List[ExtractedMedication]:
    data = _load_dict("medications.json")

    found: List[ExtractedMedication] = []
    seen_categories = set()

    for entry in data["entries"]:
        for keyword in entry["keywords"]:
            if keyword in text:
                if entry["category"] not in seen_categories:
                    found.append(
                        ExtractedMedication(
                            category=entry["category"],
                            mentioned_as=keyword,
                        )
                    )
                    seen_categories.add(entry["category"])
                break

    return found


def extract_allergy_mentions(text: str) -> List[str]:
    mentions = []

    for pattern in ALLERGY_PATTERNS:
        for match in re.finditer(pattern, text):
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 15)

            snippet = text[start:end]

            if snippet not in mentions:
                mentions.append(snippet)

    return mentions


def guess_chief_complaint(
    text: str,
) -> str | None:
    """
    会話の中から主訴らしき一文を推定する。
    """

    for pattern in CHIEF_COMPLAINT_PATTERNS:
        match = re.search(pattern, text)

        if match:
            return match.group(0).strip()

    return None


def extract_with_llm(
    text: str,
) -> dict | None:
    """
    ローカルLLMを使った高精度抽出の拡張ポイント。
    """

    return None


def build_karte_draft(
    raw_transcript: str,
) -> KarteDraft:

    symptoms = extract_symptoms(raw_transcript)

    medications = extract_medications(
        raw_transcript
    )

    allergy_mentions = extract_allergy_mentions(
        raw_transcript
    )

    chief_complaint = guess_chief_complaint(
        raw_transcript
    )

    other_notes = []

    if not symptoms:
        other_notes.append(
            "症状に関するキーワードが検出されませんでした。"
            "手動で確認してください。"
        )

    if not medications:
        other_notes.append(
            "服薬に関する言及が検出されませんでした"
            "（未確認/服薬なしの可能性）。"
        )

    return KarteDraft(
        chief_complaint=chief_complaint,
        symptoms=symptoms,
        current_medications=medications,
        allergy_mentions=allergy_mentions,
        other_notes=other_notes,
        raw_transcript=raw_transcript,
    )
