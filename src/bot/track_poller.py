import asyncio
import logging

from aiogram import Bot

from src import state as app_state
from src.bot.status import format_now_playing, status_keyboard
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
        self._last_liked: bool | None = None
        self._last_shuffle: bool | None = None
        self.active_message_id: int | None = None
        self.active_chat_id: int | None = None
        self._task: asyncio.Task | None = None
        self._busy: bool = False

        saved = app_state.load()
        self.active_chat_id = saved.get("chat_id")
        self.active_message_id = saved.get("message_id")
        if self.active_chat_id:
            logger.info(
                "Restored active message %s in chat %s",
                self.active_message_id,
                self.active_chat_id,
            )

    def track_message(self, chat_id: int, message_id: int) -> None:
        self.active_chat_id = chat_id
        self.active_message_id = message_id
        app_state.save({"chat_id": chat_id, "message_id": message_id})
        logger.info("Tracking message %s in chat %s", message_id, chat_id)

    def has_active_message(self) -> bool:
        return self.active_message_id is not None and self.active_chat_id is not None

    def prime_state(
        self,
        video_id: str | None,
        is_playing: bool | None,
        volume: int | None,
    ) -> None:
        self._last_video_id = video_id
        self._last_is_playing = is_playing
        self._last_volume = volume

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        # Keep a reference so the task isn't garbage-collected.
        self._task = asyncio.create_task(self._poll_loop(), name="track-poller")
        logger.info("Track poller started (10s interval)")

    async def _poll_loop(self) -> None:
        while True:
            await asyncio.sleep(5 if self._last_is_playing else 15)
            if self._busy:
                logger.debug("Poller: previous iteration still running, skipping")
                continue
            self._busy = True
            try:
                await self._check_track()
            except Exception as e:
                logger.warning("Poller error: %s", e)
            finally:
                self._busy = False

    async def _check_track(self) -> None:
        if not self.has_active_message():
            return

        info = await self._player.get_player_info()
        if not info or not info.get("currentTrack"):
            return

        video_id = info["currentTrack"].get("videoId")
        is_playing = info.get("isPlaying")
        volume = info.get("volume")
        liked = info.get("liked")
        shuffle = info.get("shuffle")

        if (
            video_id == self._last_video_id
            and is_playing == self._last_is_playing
            and volume == self._last_volume
            and liked == self._last_liked
            and shuffle == self._last_shuffle
        ):
            return

        self._last_video_id = video_id
        self._last_is_playing = is_playing
        self._last_volume = volume
        self._last_liked = liked
        self._last_shuffle = shuffle

        try:
            await self._bot.edit_message_text(
                format_now_playing(info),
                chat_id=self.active_chat_id,
                message_id=self.active_message_id,
                reply_markup=status_keyboard(info),
            )
            logger.info("Updated status: %s", video_id)
        except Exception as e:
            if "not modified" in str(e):
                logger.debug("Status unchanged: %s", e)
            else:
                logger.warning("Failed to update status message: %s", e)
