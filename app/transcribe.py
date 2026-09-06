"""
faster-whisper によるローカル音声文字起こし。
"""

from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel

MODEL_SIZE = "small"

DEVICE = "cpu"
COMPUTE_TYPE = "int8"


@lru_cache(maxsize=1)
def _get_model() -> WhisperModel:
    return WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )


def transcribe_audio(
    file_path: str,
    language: str = "ja",
) -> str:

    if not Path(file_path).exists():
        raise FileNotFoundError(
            f"音声ファイルが見つかりません: {file_path}"
        )

    model = _get_model()

    segments, _info = model.transcribe(
        file_path,
        language=language,
        vad_filter=True,
    )

    full_text = "".join(
        segment.text
        for segment in segments
    )

    return full_text.strip()
