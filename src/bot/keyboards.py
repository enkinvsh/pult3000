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
                InlineKeyboardButton(text="🔇", callback_data="vol_mute"),
                InlineKeyboardButton(text="ℹ️", callback_data="info"),
            ],
            [
                InlineKeyboardButton(text="15%", callback_data="vol_set:15"),
                InlineKeyboardButton(text="25%", callback_data="vol_set:25"),
                InlineKeyboardButton(text="50%", callback_data="vol_set:50"),
                InlineKeyboardButton(text="75%", callback_data="vol_set:75"),
                InlineKeyboardButton(text="100%", callback_data="vol_set:100"),
            ],
        ]
    )


def search_results_keyboard(
    results: list[tuple[str, str]],
    page: int = 0,
    per_page: int = 5,
    total: int = 0,
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=display, callback_data=f"play:{vid}")]
        for vid, display in results
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"page:{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"page:{page + 1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
