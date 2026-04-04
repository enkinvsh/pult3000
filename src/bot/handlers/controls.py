import asyncio
import logging

from aiogram import F, Router
from aiogram.types import Message

from src.bot.status import format_now_playing, sync_poller
from src.kaset import KasetController

logger = logging.getLogger(__name__)

router = Router(name="controls")

CONTROL_BUTTONS = {
    "⏮",
    "⏯",
    "⏭",
    "🔀",
    "❤️",
    "🔇",
    "ℹ️",
    "15%",
    "25%",
    "50%",
    "75%",
    "100%",
}


async def _update_pinned(
    message: Message, kaset: KasetController, delay: float = 0.0
) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    if delay:
        await asyncio.sleep(delay)
    from src.bot import track_poller as tp

    if not (tp.instance and tp.instance._active_message_id):
        return
    info = await kaset.get_player_info()
    text = format_now_playing(info)
    try:
        await message.bot.edit_message_text(
            text,
            chat_id=tp.instance._active_chat_id,
            message_id=tp.instance._active_message_id,
        )
    except Exception:
        pass


def setup(kaset: KasetController) -> Router:

    @router.message(F.text == "⏯")
    async def on_playpause(message: Message) -> None:
        await kaset.playpause()
        await _update_pinned(message, kaset, delay=0.3)

    @router.message(F.text == "⏭")
    async def on_next(message: Message) -> None:
        await kaset.next_track()
        await _update_pinned(message, kaset, delay=1.0)

    @router.message(F.text == "⏮")
    async def on_prev(message: Message) -> None:
        await kaset.previous_track()
        await _update_pinned(message, kaset, delay=1.0)

    @router.message(F.text == "🔀")
    async def on_shuffle(message: Message) -> None:
        await kaset.toggle_shuffle()
        await _update_pinned(message, kaset)

    @router.message(F.text == "❤️")
    async def on_like(message: Message) -> None:
        await kaset.like_track()
        await _update_pinned(message, kaset)

    @router.message(F.text == "🔇")
    async def on_mute(message: Message) -> None:
        await kaset.toggle_mute()
        await _update_pinned(message, kaset, delay=0.3)

    @router.message(F.text == "ℹ️")
    async def on_info(message: Message) -> None:
        await _update_pinned(message, kaset)

    @router.message(F.text.in_({"15%", "25%", "50%", "75%", "100%"}))
    async def on_vol_set(message: Message) -> None:
        level = int(message.text.replace("%", ""))
        await kaset.set_volume(level)
        await _update_pinned(message, kaset, delay=0.3)

    return router
