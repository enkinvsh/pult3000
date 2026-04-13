import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from src.bot.handlers import commands, controls, search, similar
from src.bot.middlewares import AdminOnlyMiddleware
from src.bot.track_poller import TrackPoller
from src.browser_player import BrowserPlayer
from src.config import Config
from src.music_search import MusicSearcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config.from_env()
    logger.info("Starting Pult3000 (admin=%s)", config.admin_id)

    player = BrowserPlayer(proxy_url=config.proxy_url)
    searcher = MusicSearcher(proxy_url=config.proxy_url)

    session = AiohttpSession(proxy=config.proxy_url) if config.proxy_url else None
    bot = Bot(token=config.bot_token, session=session)
    dp = Dispatcher()

    dp.message.middleware(AdminOnlyMiddleware(config.admin_id))
    dp.callback_query.middleware(AdminOnlyMiddleware(config.admin_id))

    from src.bot import track_poller as tp

    poller = TrackPoller(player, bot)
    tp.instance = poller

    dp.include_router(commands.setup(player))
    dp.include_router(controls.setup(player))
    dp.include_router(similar.setup(player, searcher))
    dp.include_router(search.setup(player, searcher))

    await player.open()
    poller.start()
    logger.info("Bot started, polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await player.close()


if __name__ == "__main__":
    asyncio.run(main())
