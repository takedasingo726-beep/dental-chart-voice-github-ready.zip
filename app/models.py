"""
カルテ下書きのデータ構造定義。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractedMedication(BaseModel):
    category: str = Field(
        ...,
        description="薬剤カテゴリ（例: 抗血栓薬）",
    )

    mentioned_as: str = Field(
        ...,
        description="会話中で実際に言及された表現",
    )


class ExtractedSymptom(BaseModel):
    normalized: str = Field(
        ...,
        description="正規化された症状名",
    )

    mentioned_as: str = Field(
        ...,
        description="会話中で実際に言及された表現",
    )


class KarteDraft(BaseModel):
    generated_at: datetime = Field(
        default_factory=datetime.now
    )

    chief_complaint: Optional[str] = Field(
        None,
        description="主訴（推定）。",
    )

    symptoms: List[ExtractedSymptom] = Field(
        default_factory=list
    )

    current_medications: List[
        ExtractedMedication
    ] = Field(
        default_factory=list
    )

    allergy_mentions: List[str] = Field(
        default_factory=list,
        description="アレルギーに関する言及（要人手確認）",
    )

    other_notes: List[str] = Field(
        default_factory=list,
        description="その他、抽出ロジックが拾った気になる発言",
    )

    raw_transcript: str = Field(
        ...,
        description="文字起こし全文（原文保持・監査用）",
    )

    needs_manual_review: bool = Field(
        default=True,
        description="歯科医師の確認・修正が必須であることを明示するフラグ。",
    )
