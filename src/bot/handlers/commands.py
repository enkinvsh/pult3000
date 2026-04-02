"""Command handlers (/start, /remote)."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards import player_keyboard

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "🎵 Kaset Remote\n\n"
        "Кнопки — управление плеером\n"
        "Текст — поиск и включение песни\n"
        "Голосовое — то же самое голосом\n\n"
        "/remote — показать пульт",
        reply_markup=player_keyboard(),
    )


@router.message(Command("remote"))
async def cmd_remote(message: Message) -> None:
    await message.answer("🎛", reply_markup=player_keyboard())
