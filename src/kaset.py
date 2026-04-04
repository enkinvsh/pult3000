import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_HELPER = Path(__file__).parent.parent / "open-url"


async def run_osascript(script: str, timeout: float = 5.0) -> str:
    proc = await asyncio.create_subprocess_exec(
        "osascript",
        "-e",
        script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"osascript timed out after {timeout}s: {script}")
    if proc.returncode != 0:
        error_msg = stderr.decode().strip()
        raise RuntimeError(f"osascript failed: {error_msg}")
    result = stdout.decode().strip()
    logger.debug("osascript result: %s", result[:200])
    return result


async def run_subprocess(cmd: list[str]) -> None:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


class KasetController:
    _TELL = 'tell application "Kaset" to '

    async def play(self) -> None:
        await run_osascript(f"{self._TELL}play")

    async def pause(self) -> None:
        await run_osascript(f"{self._TELL}pause")

    async def playpause(self) -> None:
        await run_osascript(f"{self._TELL}playpause")

    async def next_track(self) -> None:
        await run_osascript(f"{self._TELL}next track")

    async def previous_track(self) -> None:
        await run_osascript(f"{self._TELL}previous track")

    async def set_volume(self, level: int) -> None:
        level = max(0, min(100, level))
        await run_osascript(f"{self._TELL}set volume {level}")

    async def toggle_shuffle(self) -> None:
        await run_osascript(f"{self._TELL}toggle shuffle")

    async def cycle_repeat(self) -> None:
        await run_osascript(f"{self._TELL}cycle repeat")

    async def like_track(self) -> None:
        await run_osascript(f"{self._TELL}like track")

    async def dislike_track(self) -> None:
        await run_osascript(f"{self._TELL}dislike track")

    async def toggle_mute(self) -> None:
        await run_osascript(f"{self._TELL}toggle mute")

    async def get_player_info(self) -> dict | None:
        try:
            raw = await run_osascript(f"{self._TELL}get player info")
            return json.loads(raw)
        except (RuntimeError, json.JSONDecodeError) as e:
            logger.warning("Failed to get player info: %s", e)
            return None

    async def play_video(self, video_id: str) -> None:
        logger.info("Playing video: %s", video_id)
        await run_osascript(f'{self._TELL}play video "{video_id}"')
