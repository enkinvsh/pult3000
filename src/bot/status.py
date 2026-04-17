_SPACER = "\u2007" * 35


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

    lines = [_SPACER, f"{status_icon} {artist} — {title}"]
    if badges:
        lines.append(" · ".join(badges))
    return "\n".join(lines)


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
        )
        return True
    except Exception:
        return False


async def send_new_status(bot, chat_id: int, info: dict | None):
    msg = await bot.send_message(chat_id, format_now_playing(info))
    sync_poller(info, msg.chat.id, msg.message_id)
    return msg
