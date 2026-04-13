import asyncio
import logging
import random

from aiogram import F, Router
from aiogram.types import Message

from src.bot.status import format_now_playing, sync_poller
from src.kaset import KasetController
from src.music_search import MusicSearcher

logger = logging.getLogger(__name__)

router = Router(name="similar")


def setup(kaset: KasetController, searcher: MusicSearcher) -> Router:

    @router.message(F.text == "📻")
    async def on_radio(message: Message) -> None:
        try:
            await message.delete()
        except Exception:
            pass

        info = await kaset.get_player_info()
        if not info or not info.get("currentTrack"):
            await message.answer("📻 Сейчас ничего не играет")
            return

        track = info["currentTrack"]
        artist = track.get("artist", "")
        current_video_id = track.get("id", "")

        if not artist:
            await message.answer("📻 Не могу определить артиста")
            return

        playlist_tracks = searcher.get_playlist_tracks(artist, limit=50)
        if not playlist_tracks:
            await message.answer(f"📻 Не нашёл плейлистов для {artist}")
            return

        candidates = [t for t in playlist_tracks if t.video_id != current_video_id]
        if not candidates:
            await message.answer("📻 Нет других треков в плейлисте")
            return

        chosen = random.choice(candidates)
        logger.info("Radio: playlist track %s - %s", chosen.artist, chosen.title)
        await kaset.play_video(chosen.video_id)
        await asyncio.sleep(2)
        await _update_status(message, kaset)

    return router


async def _update_status(message: Message, kaset: KasetController) -> None:
    from src.bot import track_poller as tp

    info = await kaset.get_player_info()
    text = format_now_playing(info)

    if tp.instance and tp.instance._active_message_id:
        try:
            await message.bot.edit_message_text(
                text,
                chat_id=tp.instance._active_chat_id,
                message_id=tp.instance._active_message_id,
            )
            return
        except Exception:
            pass

    msg = await message.answer(text)
    sync_poller(info, msg.chat.id, msg.message_id)
