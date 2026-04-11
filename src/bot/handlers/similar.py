"""Similar tracks handler — YouTube Music radio recommendations."""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import search_results_keyboard
from src.kaset import KasetController
from src.music_search import MusicSearcher, SearchResult

logger = logging.getLogger(__name__)

router = Router(name="similar")

_PER_PAGE = 5
_cached_similar: list[SearchResult] = []


def _page_items(page: int) -> list[tuple[str, str]]:
    start = page * _PER_PAGE
    end = start + _PER_PAGE
    return [(r.video_id, r.display) for r in _cached_similar[start:end]]


def setup(kaset: KasetController, searcher: MusicSearcher) -> Router:

    @router.message(F.text == "📻")
    async def on_similar(message: Message) -> None:
        try:
            await message.delete()
        except Exception:
            pass

        info = await kaset.get_player_info()
        if not info or not info.get("currentTrack"):
            await message.answer("📻 Сейчас ничего не играет")
            return

        video_id = info["currentTrack"].get("videoId")
        if not video_id:
            await message.answer("📻 Не могу определить трек")
            return

        results = searcher.get_similar(video_id, limit=20)
        if not results:
            await message.answer("📻 Не нашёл похожих треков")
            return

        _cached_similar.clear()
        _cached_similar.extend(results)
        page = 0
        items = _page_items(page)
        track = info["currentTrack"]
        title = f"📻 Похожее на: {track.get('artist', '?')} — {track.get('name', '?')}"
        await message.answer(
            title,
            reply_markup=search_results_keyboard(
                items,
                page=page,
                per_page=_PER_PAGE,
                total=len(_cached_similar),
                page_prefix="sp",
            ),
        )

    @router.callback_query(F.data.startswith("sp:"))
    async def on_sim_page(cb: CallbackQuery) -> None:
        page = int(cb.data.split(":", 1)[1])
        items = _page_items(page)
        if not items:
            await cb.answer("Нет результатов")
            return
        await cb.answer()
        try:
            await cb.message.edit_reply_markup(
                reply_markup=search_results_keyboard(
                    items,
                    page=page,
                    per_page=_PER_PAGE,
                    total=len(_cached_similar),
                    page_prefix="sp",
                ),
            )
        except Exception:
            pass

    return router
