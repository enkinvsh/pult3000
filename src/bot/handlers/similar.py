"""Radio handler — Deezer recommendations played via YouTube Music."""

import asyncio
import logging

from aiogram import F, Router
from aiogram.types import Message

from src.bot.status import format_now_playing, sync_poller
from src.deezer import DeezerRecommender
from src.kaset import KasetController
from src.music_search import MusicSearcher

logger = logging.getLogger(__name__)

router = Router(name="similar")


def setup(
    kaset: KasetController, searcher: MusicSearcher, deezer: DeezerRecommender
) -> Router:

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
        title = track.get("name", "")

        if not artist or not title:
            await message.answer("📻 Не могу определить трек")
            return

        recommendations = await deezer.get_similar(artist, title, limit=5)
        if not recommendations:
            await message.answer("📻 Не нашёл похожих")
            return

        for rec in recommendations:
            query = f"{rec.artist} {rec.name}"
            yt_results = searcher.search(query, limit=1)
            if yt_results:
                first = yt_results[0]
                logger.info(
                    "Radio: Deezer '%s - %s' -> YT '%s - %s'",
                    rec.artist,
                    rec.name,
                    first.artist,
                    first.title,
                )
                await kaset.play_video(first.video_id)
                await asyncio.sleep(2)
                await _update_status(message, kaset)
                return

        await message.answer("📻 Не нашёл в YouTube Music")

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
