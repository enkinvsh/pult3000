import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot import track_poller as tp
from src.bot.keyboards import player_keyboard
from src.kaset import KasetController

logger = logging.getLogger(__name__)

router = Router(name="controls")

_SPACER = "\u2007" * 35


def _format_now_playing(info: dict | None) -> str:
    if not info or not info.get("currentTrack"):
        return f"{_SPACER}\n⏸ —\n🔊 —"
    track = info["currentTrack"]
    status = "▶️" if info.get("isPlaying") else "⏸"
    artist = track.get("artist") or "—"
    name = track.get("name") or "—"
    vol = info.get("volume", "—")
    return f"{_SPACER}\n{status} {artist} — {name}\n🔊 {vol}%"


async def _update_and_track(
    cb: CallbackQuery, kaset: KasetController, delay: float = 0.5
) -> None:
    if delay:
        await asyncio.sleep(delay)
    info = await kaset.get_player_info()
    text = _format_now_playing(info)
    try:
        await cb.message.edit_text(text, reply_markup=player_keyboard())
        if tp.instance:
            tp.instance.track_message(cb.message.chat.id, cb.message.message_id)
            tp.instance._last_video_id = (
                info.get("currentTrack", {}).get("videoId") if info else None
            )
            tp.instance._last_is_playing = info.get("isPlaying") if info else None
    except Exception:
        pass


def setup(kaset: KasetController) -> Router:

    @router.callback_query(F.data == "playpause")
    async def on_playpause(cb: CallbackQuery) -> None:
        await kaset.playpause()
        await cb.answer("⏯")
        await _update_and_track(cb, kaset)

    @router.callback_query(F.data == "next")
    async def on_next(cb: CallbackQuery) -> None:
        await kaset.next_track()
        await cb.answer("⏭")
        await _update_and_track(cb, kaset, delay=1.0)

    @router.callback_query(F.data == "prev")
    async def on_prev(cb: CallbackQuery) -> None:
        await kaset.previous_track()
        await cb.answer("⏮")
        await _update_and_track(cb, kaset, delay=1.0)

    @router.callback_query(F.data == "shuffle")
    async def on_shuffle(cb: CallbackQuery) -> None:
        await kaset.toggle_shuffle()
        await cb.answer("🔀")

    @router.callback_query(F.data == "like")
    async def on_like(cb: CallbackQuery) -> None:
        await kaset.like_track()
        await cb.answer("❤️")

    @router.callback_query(F.data == "vol_up")
    async def on_vol_up(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        current = info.get("volume", 50) if info else 50
        new_vol = min(100, current + 10)
        await kaset.set_volume(new_vol)
        await cb.answer(f"🔊 {new_vol}%")
        await _update_and_track(cb, kaset, delay=0.3)

    @router.callback_query(F.data == "vol_down")
    async def on_vol_down(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        current = info.get("volume", 50) if info else 50
        new_vol = max(15, current - 10)
        await kaset.set_volume(new_vol)
        await cb.answer(f"🔉 {new_vol}%")
        await _update_and_track(cb, kaset, delay=0.3)

    @router.callback_query(F.data.startswith("vol_set:"))
    async def on_vol_set(cb: CallbackQuery) -> None:
        level = int(cb.data.split(":")[1])
        await kaset.set_volume(level)
        await cb.answer(f"🔊 {level}%")
        await _update_and_track(cb, kaset, delay=0.3)

    @router.callback_query(F.data == "vol_mute")
    async def on_vol_mute(cb: CallbackQuery) -> None:
        await kaset.toggle_mute()
        await cb.answer("🔇")
        await _update_and_track(cb, kaset, delay=0.3)

    @router.callback_query(F.data == "info")
    async def on_info(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        text = _format_now_playing(info)
        try:
            await cb.message.edit_text(text, reply_markup=player_keyboard())
        except Exception:
            pass
        await cb.answer()

    return router
