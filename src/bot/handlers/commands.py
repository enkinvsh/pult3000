from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot import playback_mode as pm
from src.bot.keyboards import reply_keyboard
from src.bot.playback_mode import PlaybackMode
from src.bot.status import format_now_playing, sync_poller
from src.browser_player import BrowserPlayer

router = Router(name="commands")


def setup(player: BrowserPlayer) -> Router:
    async def show_remote(message: Message) -> None:
        await message.answer("🎵", reply_markup=reply_keyboard())
        info = await player.get_player_info()
        msg = await message.answer(format_now_playing(info))
        sync_poller(info, msg.chat.id, msg.message_id)

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        await show_remote(message)

    @router.message(Command("remote"))
    async def cmd_remote(message: Message) -> None:
        await show_remote(message)

    @router.message(Command("mode"))
    async def cmd_mode(message: Message) -> None:
        pm.current = (
            PlaybackMode.ARTIST
            if pm.current == PlaybackMode.RADIO
            else PlaybackMode.RADIO
        )

        if pm.current == PlaybackMode.ARTIST:
            label, desc = "🎤 Артист", "Треки выбранного артиста"
        else:
            label, desc = "📻 Радио", "Похожие по жанру"
        await message.answer(f"{label}\n{desc}")

    return router
