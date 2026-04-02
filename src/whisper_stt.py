"""Speech-to-text via faster-whisper (local Whisper inference)."""

import logging
from pathlib import Path

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class WhisperSTT:
    def __init__(self, model_size: str = "base") -> None:
        logger.info("Loading Whisper model: %s", model_size)
        self._model = WhisperModel(model_size, compute_type="int8")

    def transcribe(self, audio_path: Path) -> str:
        try:
            segments, _ = self._model.transcribe(
                str(audio_path),
                language="ru",
                vad_filter=True,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            logger.info("Transcribed: %s", text)
            return text
        except Exception as e:
            logger.error("Whisper transcription failed: %s", e)
            return ""
