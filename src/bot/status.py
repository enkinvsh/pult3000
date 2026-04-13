_SPACER = "\u2007" * 35


def format_now_playing(info: dict | None) -> str:
    if not info or not info.get("currentTrack"):
        return f"{_SPACER}\n⏸ —\n🔊 —"
    track = info["currentTrack"]
    status = "▶️" if info.get("isPlaying") else "⏸"
    artist = track.get("artist") or "—"
    title = track.get("title") or track.get("name") or "—"
    vol = info.get("volume", "—")
    return f"{_SPACER}\n{status} {artist} — {title}\n🔊 {vol}%"


def sync_poller(info: dict | None, chat_id: int, message_id: int) -> None:
    from src.bot import track_poller as tp

    if tp.instance:
        tp.instance.track_message(chat_id, message_id)
        tp.instance._last_video_id = (
            info.get("currentTrack", {}).get("videoId") if info else None
        )
        tp.instance._last_is_playing = info.get("isPlaying") if info else None
        tp.instance._last_volume = info.get("volume") if info else None
