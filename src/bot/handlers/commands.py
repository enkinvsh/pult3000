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

    @router.message(Command("testosa"))
    async def cmd_testosa(message: Message) -> None:
        import asyncio

        proc = await asyncio.create_subprocess_exec(
            "osascript",
            "-e",
            'tell application "Kaset" to get player info',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
            await message.answer(f"OK: {stdout.decode()[:200]}")
        except asyncio.TimeoutError:
            proc.kill()
            await message.answer("TIMEOUT: osascript hung")

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
