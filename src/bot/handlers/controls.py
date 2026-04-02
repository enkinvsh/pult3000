"""Handlers for media control buttons."""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.keyboards import player_keyboard, volume_keyboard
from src.kaset import KasetController

logger = logging.getLogger(__name__)

router = Router(name="controls")


def setup(kaset: KasetController) -> Router:

    @router.callback_query(F.data == "playpause")
    async def on_playpause(cb: CallbackQuery) -> None:
        await kaset.playpause()
        await cb.answer("⏯")

    @router.callback_query(F.data == "next")
    async def on_next(cb: CallbackQuery) -> None:
        await kaset.next_track()
        await cb.answer("⏭")

    @router.callback_query(F.data == "prev")
    async def on_prev(cb: CallbackQuery) -> None:
        await kaset.previous_track()
        await cb.answer("⏮")

    @router.callback_query(F.data == "shuffle")
    async def on_shuffle(cb: CallbackQuery) -> None:
        await kaset.toggle_shuffle()
        await cb.answer("🔀")

    @router.callback_query(F.data == "like")
    async def on_like(cb: CallbackQuery) -> None:
        await kaset.like_track()
        await cb.answer("❤️")

    @router.callback_query(F.data == "vol")
    async def on_vol(cb: CallbackQuery) -> None:
        await cb.message.edit_reply_markup(reply_markup=volume_keyboard())
        await cb.answer()

    @router.callback_query(F.data == "vol_back")
    async def on_vol_back(cb: CallbackQuery) -> None:
        await cb.message.edit_reply_markup(reply_markup=player_keyboard())
        await cb.answer()

    @router.callback_query(F.data == "vol_up")
    async def on_vol_up(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        current = info.get("volume", 50) if info else 50
        new_vol = min(100, current + 10)
        await kaset.set_volume(new_vol)
        await cb.answer(f"🔊 {new_vol}%")

    @router.callback_query(F.data == "vol_down")
    async def on_vol_down(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        current = info.get("volume", 50) if info else 50
        new_vol = max(0, current - 10)
        await kaset.set_volume(new_vol)
        await cb.answer(f"🔉 {new_vol}%")

    @router.callback_query(F.data == "vol_mute")
    async def on_vol_mute(cb: CallbackQuery) -> None:
        await kaset.toggle_mute()
        await cb.answer("🔇")

    @router.callback_query(F.data == "info")
    async def on_info(cb: CallbackQuery) -> None:
        info = await kaset.get_player_info()
        if not info or not info.get("currentTrack"):
            await cb.answer("Ничего не играет", show_alert=True)
            return
        track = info["currentTrack"]
        status = "▶️" if info.get("isPlaying") else "⏸"
        text = (
            f"{status} {track.get('artist', '?')} — {track.get('name', '?')}\n"
            f"💿 {track.get('album', '?')}\n"
            f"🔊 {info.get('volume', '?')}%"
        )
        await cb.answer(text, show_alert=True)

    return router
