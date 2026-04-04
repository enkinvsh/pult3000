from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot import track_poller as tp
from src.bot.handlers.controls import _format_now_playing
from src.bot.keyboards import player_keyboard
from src.kaset import KasetController

router = Router(name="commands")


def _sync_poller(info: dict | None, chat_id: int, message_id: int) -> None:
    if tp.instance:
        tp.instance.track_message(chat_id, message_id)
        tp.instance._last_video_id = (
            info.get("currentTrack", {}).get("videoId") if info else None
        )
        tp.instance._last_is_playing = info.get("isPlaying") if info else None


def setup(kaset: KasetController) -> Router:

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        info = await kaset.get_player_info()
        text = _format_now_playing(info)
        msg = await message.answer(text, reply_markup=player_keyboard())
        _sync_poller(info, msg.chat.id, msg.message_id)

    @router.message(Command("remote"))
    async def cmd_remote(message: Message) -> None:
        info = await kaset.get_player_info()
        text = _format_now_playing(info)
        msg = await message.answer(text, reply_markup=player_keyboard())
        _sync_poller(info, msg.chat.id, msg.message_id)

    return router
