from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import logging

start_router = Router(name="start")

logger = logging.getLogger(name=__name__)


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info("Iniciando Bot..")
    await message.answer("""<b>Bienvenido a Pywallet</b>""", parse_mode=ParseMode.HTML)
