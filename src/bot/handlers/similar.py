import asyncio
import logging

from aiogram import F, Router
from aiogram.types import Message

from src.bot.status import format_now_playing, sync_poller
from src.browser_player import BrowserPlayer
from src.music_search import MusicSearcher
from src.queue import queue

logger = logging.getLogger(__name__)

router = Router(name="similar")


def setup(player: BrowserPlayer, searcher: MusicSearcher) -> Router:

    @router.message(F.text == "📻")
    async def on_radio(message: Message) -> None:
        try:
            await message.delete()
        except Exception:
            pass

        info = await player.get_player_info()
        if not info or not info.get("currentTrack"):
            await message.answer("📻 Сейчас ничего не играет")
            return

        track = info["currentTrack"]
        artist = track.get("artist", "")

        if not artist:
            await message.answer("📻 Не могу определить артиста")
            return

        playlist_tracks = searcher.get_playlist_tracks(artist, limit=50)
        if not playlist_tracks:
            started = await player.search_and_play_playlist(artist)
            if started:
                await asyncio.sleep(2)
                await _update_status(message, player)
            else:
                await message.answer(f"📻 Не нашёл плейлистов для {artist}")
            return

        queue.set_playlist(playlist_tracks, shuffle=True)
        first_track = queue.current()
        if not first_track:
            await message.answer("📻 Пустой плейлист")
            return

        logger.info(
            "Radio: started queue for %s (%d tracks)", artist, len(playlist_tracks)
        )
        await player.play_video(first_track.video_id)
        await asyncio.sleep(2)
        await _update_status(message, player)

    return router


async def _update_status(message: Message, player: BrowserPlayer) -> None:
    from src.bot import track_poller as tp

    info = await player.get_player_info()
    text = format_now_playing(info)

    if tp.instance and tp.instance._active_message_id:
        try:
            await message.bot.edit_message_text(
                text,
                chat_id=tp.instance._active_chat_id,
                message_id=tp.instance._active_message_id,
            )
        except Exception as e:
            logger.debug("Could not edit status message: %s", e)
        sync_poller(info, tp.instance._active_chat_id, tp.instance._active_message_id)
        return

    msg = await message.answer(text)
    sync_poller(info, msg.chat.id, msg.message_id)
