from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src import history
from src.bot import playback_mode as pm
from src.bot.keyboards import reply_keyboard, search_results_keyboard
from src.bot.playback_mode import PlaybackMode
from src.bot.status import render_pinned, send_new_status
from src.browser_player import BrowserPlayer

router = Router(name="commands")


def setup(player: BrowserPlayer) -> Router:
    async def show_remote(message: Message) -> None:
        await message.answer("🎵", reply_markup=reply_keyboard())
        info = await player.get_player_info()
        await send_new_status(message.bot, message.chat.id, info)

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        await show_remote(message)

    @router.message(Command("remote"))
    async def cmd_remote(message: Message) -> None:
        await show_remote(message)

    @router.message(Command("now"))
    async def cmd_now(message: Message) -> None:
        info = await player.get_player_info()
        updated = await render_pinned(message.bot, info)
        if not updated:
            await send_new_status(message.bot, message.chat.id, info)
        try:
            await message.delete()
        except Exception:
            pass

    @router.message(Command("last"))
    async def cmd_last(message: Message) -> None:
        items = history.recent(limit=15)
        if not items:
            await message.answer("📜 История пуста")
            return
        kb_items = [
            (i["videoId"], f"{i.get('artist', '—')} — {i.get('title', '—')}")
            for i in items
        ]
        await message.answer(
            "📜 Недавние треки:",
            reply_markup=search_results_keyboard(
                kb_items, page=0, per_page=len(kb_items), total=len(kb_items)
            ),
        )

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
