"""Handlers for text-based music search and playback."""

import logging
import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import player_keyboard, search_results_keyboard
from src.kaset import KasetController
from src.music_search import MusicSearcher

logger = logging.getLogger(__name__)

router = Router(name="search")

_PREFIXES = re.compile(
    r"^\s*(включи|поставь|играй|найди|play|search)\s+",
    re.IGNORECASE,
)


def extract_query(text: str, allow_raw: bool = False) -> str | None:
    text = text.strip()
    match = _PREFIXES.match(text)
    if match:
        query = text[match.end() :].strip()
        return query if query else None
    if allow_raw and text:
        return text
    return None


def setup(kaset: KasetController, searcher: MusicSearcher) -> Router:

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        query = extract_query(message.text, allow_raw=True)
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

    @router.callback_query(F.data.startswith("play:"))
    async def on_play_result(cb: CallbackQuery) -> None:
        video_id = cb.data.split(":", 1)[1]
        await kaset.play_video(video_id)
        await cb.message.edit_text(
            f"▶️ Запускаю...",
            reply_markup=player_keyboard(),
        )
        await cb.answer()

    return router
