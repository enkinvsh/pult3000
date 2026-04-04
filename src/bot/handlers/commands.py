from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot import playback_mode as pm
from src.bot.keyboards import reply_keyboard
from src.bot.status import format_now_playing, sync_poller
from src.bot.playback_mode import PlaybackMode
from src.kaset import KasetController

router = Router(name="commands")


def setup(kaset: KasetController) -> Router:

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        await message.answer("🎵", reply_markup=reply_keyboard())
        info = await kaset.get_player_info()
        text = format_now_playing(info)
        msg = await message.answer(text)
        sync_poller(info, msg.chat.id, msg.message_id)

    @router.message(Command("remote"))
    async def cmd_remote(message: Message) -> None:
        await message.answer("🎵", reply_markup=reply_keyboard())
        info = await kaset.get_player_info()
        text = format_now_playing(info)
        msg = await message.answer(text)
        sync_poller(info, msg.chat.id, msg.message_id)

    @router.message(Command("mode"))
    async def cmd_mode(message: Message) -> None:
        if pm.current == PlaybackMode.RADIO:
            pm.current = PlaybackMode.ARTIST
        else:
            pm.current = PlaybackMode.RADIO

        label = "🎤 Артист" if pm.current == PlaybackMode.ARTIST else "📻 Радио"
        desc = (
            "Треки выбранного артиста"
            if pm.current == PlaybackMode.ARTIST
            else "Похожие по жанру"
        )
        await message.answer(f"{label}\n{desc}")

    return router
