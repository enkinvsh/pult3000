import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot.status import render_pinned
from src.browser_player import BrowserPlayer
from src.queue import queue

logger = logging.getLogger(__name__)

router = Router(name="controls")

CONTROL_BUTTONS = {
    "⏮",
    "⏯",
    "⏭",
    "🔀",
    "❤️",
    "📻",
    "15%",
    "25%",
    "50%",
    "75%",
    "100%",
}


async def _update_pinned(
    message: Message, player: BrowserPlayer, delay: float = 0.0
) -> None:
    try:
        await message.delete()
    except Exception as e:
        logger.debug("Could not delete control message: %s", e)

    if delay:
        await asyncio.sleep(delay)

    info = await player.get_player_info()
    await render_pinned(message.bot, info)


def setup(player: BrowserPlayer) -> Router:

    @router.message(F.text == "⏯")
    async def on_playpause(message: Message) -> None:
        await player.playpause()
        await _update_pinned(message, player, delay=0.3)

    @router.message(F.text == "⏭")
    async def on_next(message: Message) -> None:
        if queue.is_active():
            track = queue.next()
            if track:
                await player.play_video(track.video_id)
                await _update_pinned(message, player, delay=2.0)
                return
        await player.next_track()
        await _update_pinned(message, player, delay=1.0)

    @router.message(F.text == "⏮")
    async def on_prev(message: Message) -> None:
        if queue.is_active():
            track = queue.prev()
            if track:
                await player.play_video(track.video_id)
                await _update_pinned(message, player, delay=2.0)
                return
        await player.previous_track()
        await _update_pinned(message, player, delay=1.0)

    @router.message(F.text == "🔀")
    async def on_shuffle(message: Message) -> None:
        await player.toggle_shuffle()
        await _update_pinned(message, player, delay=0.3)

    @router.message(F.text == "❤️")
    async def on_like(message: Message) -> None:
        await player.like_track()
        await _update_pinned(message, player, delay=0.3)

    @router.message(F.text.in_({"15%", "25%", "50%", "75%", "100%"}))
    async def on_volume(message: Message) -> None:
        level = int(message.text.rstrip("%"))
        await player.set_volume(level)
        try:
            await message.delete()
        except Exception as e:
            logger.debug("Could not delete volume message: %s", e)
        info = await player.get_player_info()
        await render_pinned(message.bot, info)

    @router.callback_query(F.data.startswith("vol:"))
    async def on_vol_bump(cb: CallbackQuery) -> None:
        try:
            delta = int(cb.data.split(":", 1)[1])
        except ValueError:
            await cb.answer()
            return
        new_level = await player.bump_volume(delta)
        await cb.answer(f"🔊 {new_level}%")
        info = await player.get_player_info()
        await render_pinned(cb.message.bot, info)

    @router.callback_query(F.data == "toggle:like")
    async def on_toggle_like(cb: CallbackQuery) -> None:
        await player.like_track()
        await cb.answer("❤️")
        await asyncio.sleep(0.3)
        info = await player.get_player_info()
        await render_pinned(cb.message.bot, info)

    return router
