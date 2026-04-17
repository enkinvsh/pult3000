_SPACER = "\u2007" * 35


def format_now_playing(info: dict | None) -> str:
    if not info or not info.get("currentTrack"):
        return f"{_SPACER}\n⏸ —"
    track = info["currentTrack"]
    status = "▶️" if info.get("isPlaying") else "⏸"
    artist = track.get("artist") or "—"
    title = track.get("title") or track.get("name") or "—"
    return f"{_SPACER}\n{status} {artist} — {title}"


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
