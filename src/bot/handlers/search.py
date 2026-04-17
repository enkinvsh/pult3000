import asyncio
import logging
import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot import playback_mode as pm
from src.bot.handlers.controls import CONTROL_BUTTONS
from src.bot.keyboards import search_results_keyboard
from src.bot.playback_mode import PlaybackMode
from src.bot.status import render_pinned, send_new_status
from src.browser_player import BrowserPlayer
from src.music_search import MusicSearcher, SearchResult
from src.queue import queue

logger = logging.getLogger(__name__)

router = Router(name="search")

_PREFIXES = re.compile(
    r"^\s*(включи|поставь|играй|найди|play|search)\s+",
    re.IGNORECASE,
)

_PER_PAGE = 5
_cached_results: list[SearchResult] = []


def extract_query(text: str, allow_raw: bool = False) -> str | None:
    text = text.strip()
    match = _PREFIXES.match(text)
    if match:
        query = text[match.end() :].strip()
        return query if query else None
    if allow_raw and text:
        return text
    return None


def _page_items(page: int) -> list[tuple[str, str]]:
    start = page * _PER_PAGE
    end = start + _PER_PAGE
    return [(r.video_id, r.display) for r in _cached_results[start:end]]


async def _play_single(player: BrowserPlayer, bot, chat_id: int, video_id: str) -> None:
    queue.clear()
    await player.play_video(video_id)
    await asyncio.sleep(3)
    info = await player.get_player_info()
    if not await render_pinned(bot, info):
        await send_new_status(bot, chat_id, info)


def setup(player: BrowserPlayer, searcher: MusicSearcher) -> Router:

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        if message.text in CONTROL_BUTTONS:
            return
        query = extract_query(message.text, allow_raw=True)
        if not query:
            return

        try:
            await message.delete()
        except Exception as e:
            logger.debug("Could not delete search message: %s", e)

        if pm.current == PlaybackMode.ARTIST:
            results = searcher.search_artist_tracks(query, limit=20)
        else:
            results = searcher.search(query, limit=20)[:20]

        if not results:
            await message.answer("🔍 Ничего не нашёл")
            return

        if len(results) == 1:
            await _play_single(
                player, message.bot, message.chat.id, results[0].video_id
            )
            return

        _cached_results.clear()
        _cached_results.extend(results)
        page = 0
        items = _page_items(page)
        await message.answer(
            "🔍 Выбери трек:",
            reply_markup=search_results_keyboard(
                items, page=page, per_page=_PER_PAGE, total=len(_cached_results)
            ),
        )

    @router.callback_query(F.data.startswith("page:"))
    async def on_page(cb: CallbackQuery) -> None:
        page = int(cb.data.split(":", 1)[1])
        items = _page_items(page)
        if not items:
            await cb.answer("Нет результатов")
            return
        await cb.answer()
        try:
            await cb.message.edit_reply_markup(
                reply_markup=search_results_keyboard(
                    items, page=page, per_page=_PER_PAGE, total=len(_cached_results)
                ),
            )
        except Exception as e:
            logger.debug("Could not edit pagination markup: %s", e)

    @router.callback_query(F.data.startswith("play:"))
    async def on_play_result(cb: CallbackQuery) -> None:
        video_id = cb.data.split(":", 1)[1]
        await cb.answer("▶️")
        try:
            await cb.message.delete()
        except Exception as e:
            logger.debug("Could not delete search result message: %s", e)

        await _play_single(player, cb.message.bot, cb.message.chat.id, video_id)

    return router
