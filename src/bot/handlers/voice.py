"""Handler for voice messages — Whisper STT → search & play."""

import logging
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.types import Message

from src.bot.handlers.search import extract_query
from src.bot.keyboards import player_keyboard, search_results_keyboard
from src.kaset import KasetController
from src.music_search import MusicSearcher
from src.whisper_stt import WhisperSTT

logger = logging.getLogger(__name__)

router = Router(name="voice")


def setup(
    kaset: KasetController,
    searcher: MusicSearcher,
    whisper: WhisperSTT,
    bot_token: str,
) -> Router:

    @router.message(F.voice)
    async def on_voice(message: Message) -> None:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            file = await message.bot.get_file(message.voice.file_id)
            await message.bot.download_file(file.file_path, tmp_path)

            text = whisper.transcribe(tmp_path)
            if not text:
                await message.answer("🎤 Не удалось распознать")
                return

            await message.answer(f"🎤 «{text}»")

            query = extract_query(text, allow_raw=True)
            if not query:
                return

            results = searcher.search(query, limit=5)
            if not results:
                await message.answer("🔍 Ничего не нашёл")
                return

            if len(results) == 1:
                await kaset.play_video(results[0].video_id)
                await message.answer(
                    f"▶️ {results[0].display}",
                    reply_markup=player_keyboard(),
                )
            else:
                items = [(r.video_id, r.display) for r in results]
                await message.answer(
                    "🔍 Выбери трек:",
                    reply_markup=search_results_keyboard(items),
                )
        finally:
            tmp_path.unlink(missing_ok=True)

    return router
