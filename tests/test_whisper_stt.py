from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.whisper_stt import WhisperSTT


class TestWhisperSTT:
    @patch("src.whisper_stt.WhisperModel")
    def test_transcribe_returns_text(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model

        segment = MagicMock()
        segment.text = " включи Metallica Nothing Else Matters"
        mock_model.transcribe.return_value = ([segment], MagicMock())

        stt = WhisperSTT(model_size="tiny")
        text = stt.transcribe(Path("/tmp/test.ogg"))

        assert text == "включи Metallica Nothing Else Matters"
        mock_model.transcribe.assert_called_once()

    @patch("src.whisper_stt.WhisperModel")
    def test_transcribe_strips_whitespace(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model

        seg1 = MagicMock()
        seg1.text = " привет "
        seg2 = MagicMock()
        seg2.text = " мир "
        mock_model.transcribe.return_value = ([seg1, seg2], MagicMock())

        stt = WhisperSTT(model_size="tiny")
        text = stt.transcribe(Path("/tmp/test.ogg"))
        assert text == "привет мир"

    @patch("src.whisper_stt.WhisperModel")
    def test_transcribe_returns_empty_on_error(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_model.transcribe.side_effect = RuntimeError("boom")

        stt = WhisperSTT(model_size="tiny")
        text = stt.transcribe(Path("/tmp/test.ogg"))
        assert text == ""
