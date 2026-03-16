from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from app.handlers.start import start_router
from app.handlers.message import IA_message
from app.bot.menu_commands import setup_commands
import asyncio
import logging

logger = logging.getLogger(__name__)


async def setup_bot():
    """Función Constructora, prepara al Bot y el Dispatcher"""
    token = os.getenv("TOKEN")
    if not token:
        logger.error("Error el token del bot no se encuentra")
        raise ValueError("Error el Token del Bot no se encuentra")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(IA_message)
    await setup_commands(bot=bot)
    return bot, dp
