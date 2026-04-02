"""Entry point for kaset-remote-bot."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.bot.handlers import commands, controls, search, voice
from src.bot.middlewares import AdminOnlyMiddleware
from src.config import Config
from src.kaset import KasetController
from src.music_search import MusicSearcher
from src.whisper_stt import WhisperSTT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config.from_env()
    logger.info("Starting Kaset Remote Bot (admin=%s)", config.admin_id)

    kaset = KasetController()
    searcher = MusicSearcher()
    whisper = WhisperSTT(model_size=config.whisper_model)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.message.middleware(AdminOnlyMiddleware(config.admin_id))
    dp.callback_query.middleware(AdminOnlyMiddleware(config.admin_id))

    # Order matters: commands first, then voice, then text (text is catch-all)
    dp.include_router(commands.router)
    dp.include_router(controls.setup(kaset))
    dp.include_router(voice.setup(kaset, searcher, whisper, config.bot_token))
    dp.include_router(search.setup(kaset, searcher))

    logger.info("Bot started, polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
