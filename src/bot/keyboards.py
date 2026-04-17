from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⏮"),
                KeyboardButton(text="⏯"),
                KeyboardButton(text="⏭"),
            ],
            [
                KeyboardButton(text="🔀"),
                KeyboardButton(text="❤️"),
                KeyboardButton(text="📻"),
            ],
            [
                KeyboardButton(text="15%"),
                KeyboardButton(text="25%"),
                KeyboardButton(text="50%"),
                KeyboardButton(text="75%"),
                KeyboardButton(text="100%"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def search_results_keyboard(
    results: list[tuple[str, str]],
    page: int = 0,
    per_page: int = 5,
    total: int = 0,
    page_prefix: str = "page",
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=display, callback_data=f"play:{vid}")]
        for vid, display in results
    ]
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="◀️", callback_data=f"{page_prefix}:{page - 1}")
        )
    if (page + 1) * per_page < total:
        nav.append(
            InlineKeyboardButton(text="▶️", callback_data=f"{page_prefix}:{page + 1}")
        )
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
