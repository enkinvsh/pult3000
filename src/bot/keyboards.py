"""Inline keyboard layouts for the music remote."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def player_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏮", callback_data="prev"),
                InlineKeyboardButton(text="⏯", callback_data="playpause"),
                InlineKeyboardButton(text="⏭", callback_data="next"),
            ],
            [
                InlineKeyboardButton(text="🔀", callback_data="shuffle"),
                InlineKeyboardButton(text="❤️", callback_data="like"),
                InlineKeyboardButton(text="🔊", callback_data="vol"),
                InlineKeyboardButton(text="ℹ️", callback_data="info"),
            ],
        ]
    )


def volume_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔉 −10", callback_data="vol_down"),
                InlineKeyboardButton(text="🔊 +10", callback_data="vol_up"),
            ],
            [
                InlineKeyboardButton(text="🔇 Mute", callback_data="vol_mute"),
                InlineKeyboardButton(text="◀️ Назад", callback_data="vol_back"),
            ],
        ]
    )


def search_results_keyboard(results: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=display, callback_data=f"play:{vid}")]
        for vid, display in results
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
