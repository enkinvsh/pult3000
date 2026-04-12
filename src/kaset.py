"""Kaset controller — headless-safe via defaults, URL scheme, and System Events.

No direct AppleScript to Kaset — those hang on headless Macs.
Instead:
 - Player info: `defaults export com.sertacozercan.Kaset -` (plist → JSON)
 - Play video:  `open kaset://play?v=VIDEO_ID` (URL scheme)
 - Controls:    System Events keyboard shortcuts to Kaset process
"""

import asyncio
import json
import logging
import plistlib

logger = logging.getLogger(__name__)

_BUNDLE = "com.sertacozercan.Kaset"


async def _run(cmd: list[str], timeout: float = 10.0) -> str:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"timed out after {timeout}s: {' '.join(cmd)}")
    if proc.returncode != 0:
        raise RuntimeError(f"cmd failed ({proc.returncode}): {stderr.decode().strip()}")
    return stdout.decode().strip()


async def _keystroke(key: str, modifiers: str = "") -> None:
    if modifiers:
        script = (
            f'tell application "System Events" to tell process "Kaset" to '
            f'keystroke "{key}" using {{{modifiers}}}'
        )
    else:
        script = (
            f'tell application "System Events" to tell process "Kaset" to '
            f'keystroke "{key}"'
        )
    await _run(["osascript", "-e", script])


async def _key_code(code: int, modifiers: str = "") -> None:
    if modifiers:
        script = (
            f'tell application "System Events" to tell process "Kaset" to '
            f"key code {code} using {{{modifiers}}}"
        )
    else:
        script = (
            f'tell application "System Events" to tell process "Kaset" to '
            f"key code {code}"
        )
    await _run(["osascript", "-e", script])


class KasetController:
    async def playpause(self) -> None:
        await _key_code(49)  # space

    async def play(self) -> None:
        await self.playpause()

    async def pause(self) -> None:
        await self.playpause()

    async def next_track(self) -> None:
        await _key_code(124, "command down")  # ⌘→

    async def previous_track(self) -> None:
        await _key_code(123, "command down")  # ⌘←

    async def set_volume(self, level: int) -> None:
        level = max(0, min(100, level))
        info = await self.get_player_info()
        if not info:
            return
        current = round(info.get("volume", 50))
        diff = level - current
        step = 6
        presses = abs(diff) // step
        code = 126 if diff > 0 else 125  # ↑ or ↓
        for _ in range(presses):
            await _key_code(code, "command down")
            await asyncio.sleep(0.05)

    async def toggle_shuffle(self) -> None:
        await _keystroke("s", "command down")  # ⌘S

    async def cycle_repeat(self) -> None:
        await _keystroke("r", "command down")  # ⌘R

    async def like_track(self) -> None:
        await _keystroke("l", "command down")  # ⌘L

    async def dislike_track(self) -> None:
        logger.warning("dislike_track not available via keyboard shortcut")

    async def toggle_mute(self) -> None:
        info = await self.get_player_info()
        if not info:
            return
        current = info.get("volume", 0)
        if current > 0:
            self._volume_before_mute = current
            await self.set_volume(0)
        else:
            await self.set_volume(getattr(self, "_volume_before_mute", 50))

    async def get_player_info(self) -> dict | None:

        try:
            raw = await _run(["defaults", "export", _BUNDLE, "-"])
            data = plistlib.loads(raw.encode())

            session_bytes = data.get("kaset.saved.playbackSession", b"")
            if not session_bytes:
                return None

            session = json.loads(
                session_bytes.decode()
                if isinstance(session_bytes, bytes)
                else session_bytes
            )
            queue = session.get("queue", [])
            idx = session.get("currentIndex", 0)
            current = queue[idx] if idx < len(queue) else {}

            artists = current.get("artists", [])
            artist = artists[0].get("name") if artists else "Unknown"
            volume_raw = data.get("playerVolume", 0.5)
            volume = round(float(volume_raw) * 100)

            return {
                "isPlaying": True,
                "currentTrack": {
                    "name": current.get("title", "Unknown"),
                    "artist": artist,
                    "videoId": session.get("currentVideoId", ""),
                    "album": "",
                },
                "volume": volume,
                "duration": session.get("duration", 0),
                "position": session.get("progress", 0),
            }
        except Exception as e:
            logger.warning("Failed to get player info: %s", e)
            return None

    async def play_video(self, video_id: str) -> None:

        logger.info("Playing video: %s", video_id)
        await _run(["open", f"kaset://play?v={video_id}"])
