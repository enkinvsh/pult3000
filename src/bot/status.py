from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_SPACER = "\u2007" * 35


def _fmt_time(seconds: float) -> str:
    total = int(seconds or 0)
    return f"{total // 60}:{total % 60:02d}"


def format_now_playing(info: dict | None) -> str:
    if not info or not info.get("currentTrack"):
        return f"{_SPACER}\n⏸ —"

    track = info["currentTrack"]
    status_icon = "▶️" if info.get("isPlaying") else "⏸"
    artist = track.get("artist") or "—"
    title = track.get("title") or track.get("name") or "—"

    badges = []
    if info.get("shuffle"):
        badges.append("🔀")
    if info.get("liked"):
        badges.append("❤️")
    volume = info.get("volume")
    if volume is not None:
        badges.append(f"🔊 {volume}%")

    duration = info.get("duration") or 0
    position = info.get("position") or 0
    progress = f"{_fmt_time(position)} / {_fmt_time(duration)}" if duration else ""

    lines = [_SPACER, f"{status_icon} {artist} — {title}"]
    if progress:
        lines.append(progress)
    if badges:
        lines.append(" · ".join(badges))
    return "\n".join(lines)


def status_keyboard(info: dict | None) -> InlineKeyboardMarkup:
    liked = bool(info and info.get("liked"))
    heart = "💔" if liked else "❤️"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔉 -5", callback_data="vol:-5"),
                InlineKeyboardButton(text=heart, callback_data="toggle:like"),
                InlineKeyboardButton(text="🔊 +5", callback_data="vol:+5"),
            ],
        ]
    )


def sync_poller(info: dict | None, chat_id: int, message_id: int) -> None:
    from src.bot import track_poller as tp

    if not tp.instance:
        return
    tp.instance.track_message(chat_id, message_id)
    track = (info or {}).get("currentTrack") or {}
    tp.instance.prime_state(
        video_id=track.get("videoId"),
        is_playing=(info or {}).get("isPlaying"),
        volume=(info or {}).get("volume"),
    )


async def render_pinned(bot, info: dict | None) -> bool:
    from src.bot import track_poller as tp

    if not tp.instance:
        return False
    chat_id = tp.instance.active_chat_id
    message_id = tp.instance.active_message_id
    if chat_id is None or message_id is None:
        return False
    try:
        await bot.edit_message_text(
            format_now_playing(info),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=status_keyboard(info),
        )
        return True
    except Exception:
        return False


async def send_new_status(bot, chat_id: int, info: dict | None):
    msg = await bot.send_message(
        chat_id,
        format_now_playing(info),
        reply_markup=status_keyboard(info),
    )
    sync_poller(info, msg.chat.id, msg.message_id)
    return msg
