import asyncio
import logging
import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot import playback_mode as pm
from src.bot.handlers.controls import CONTROL_BUTTONS
from src.bot.keyboards import search_results_keyboard
from src.bot.status import format_now_playing, sync_poller
from src.bot.playback_mode import PlaybackMode
from src.kaset import KasetController
from src.music_search import MusicSearcher, SearchResult

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


def setup(kaset: KasetController, searcher: MusicSearcher) -> Router:

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        if message.text in CONTROL_BUTTONS:
            return
        query = extract_query(message.text, allow_raw=True)
        if not query:
            return

        try:
            await message.delete()
        except Exception:
            pass

        if pm.current == PlaybackMode.ARTIST:
            results = searcher.search_artist_tracks(query, limit=20)
        else:
            results = searcher.search(query, limit=20)[:20]
        if not results:
            await message.answer("🔍 Ничего не нашёл")
            return

        if len(results) == 1:
            await kaset.play_video(results[0].video_id)
            await asyncio.sleep(3)
            from src.bot import track_poller as tp

            info = await kaset.get_player_info()
            text = format_now_playing(info)
            if tp.instance and tp.instance._active_message_id:
                try:
                    await message.bot.edit_message_text(
                        text,
                        chat_id=tp.instance._active_chat_id,
                        message_id=tp.instance._active_message_id,
                    )
                    return
                except Exception:
                    pass
            msg = await message.answer(text)
            sync_poller(info, msg.chat.id, msg.message_id)
        else:
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
        except Exception:
            pass

    @router.callback_query(F.data.startswith("play:"))
    async def on_play_result(cb: CallbackQuery) -> None:
        video_id = cb.data.split(":", 1)[1]
        await cb.answer("▶️")
        try:
            await cb.message.delete()
        except Exception:
            pass
        await kaset.play_video(video_id)
        await asyncio.sleep(3)
        from src.bot import track_poller as tp

        info = await kaset.get_player_info()
        text = format_now_playing(info)
        if tp.instance and tp.instance._active_message_id:
            try:
                await cb.message.bot.edit_message_text(
                    text,
                    chat_id=tp.instance._active_chat_id,
                    message_id=tp.instance._active_message_id,
                )
            except Exception:
                pass

    return router
