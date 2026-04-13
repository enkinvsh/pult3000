import asyncio
import logging

from aiogram import Bot

from src.bot.status import format_now_playing
from src.browser_player import BrowserPlayer

logger = logging.getLogger(__name__)

instance: "TrackPoller | None" = None


class TrackPoller:
    def __init__(self, player: BrowserPlayer, bot: Bot) -> None:
        self._player = player
        self._bot = bot
        self._last_video_id: str | None = None
        self._last_is_playing: bool | None = None
        self._last_volume: int | None = None
        self._active_message_id: int | None = None
        self._active_chat_id: int | None = None

    def track_message(self, chat_id: int, message_id: int) -> None:
        self._active_chat_id = chat_id
        self._active_message_id = message_id
        logger.info("Tracking message %s in chat %s", message_id, chat_id)

    def start(self) -> None:
        asyncio.create_task(self._poll_loop())
        logger.info("Track poller started (10s interval)")

    async def _poll_loop(self) -> None:
        while True:
            await asyncio.sleep(10)
            try:
                await self._check_track()
            except Exception as e:
                logger.warning("Poller error: %s", e)

    async def _check_track(self) -> None:
        if not self._active_message_id or not self._active_chat_id:
            return

        info = await self._player.get_player_info()
        if not info or not info.get("currentTrack"):
            return

        video_id = info["currentTrack"].get("videoId")
        is_playing = info.get("isPlaying")
        volume = info.get("volume")

        if (
            video_id == self._last_video_id
            and is_playing == self._last_is_playing
            and volume == self._last_volume
        ):
            return

        self._last_video_id = video_id
        self._last_is_playing = is_playing
        self._last_volume = volume
        text = format_now_playing(info)
        try:
            await self._bot.edit_message_text(
                text,
                chat_id=self._active_chat_id,
                message_id=self._active_message_id,
            )
            logger.info("Updated status: %s", video_id)
        except Exception as e:
            logger.warning("Failed to update status message: %s", e)
