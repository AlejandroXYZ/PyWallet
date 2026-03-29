from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
import logging
from app.handlers.utils.dolar import dolar_hoy

start_router = Router(name="start")

logger = logging.getLogger(name=__name__)


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info("Iniciando Bot..")
    await message.answer("""<b>Bienvenido a Pywallet</b>""", parse_mode=ParseMode.HTML)


@start_router.message(Command("dolar"))
async def dolar(message: Message):
    dolar = dolar_hoy()
    if dolar["status"]:
        await message.answer(
            f"<b>PRECIO DEL DOLAR HOY BCV</b>\n\n{dolar['precio']}\n\n"
        )
    else:
        await message.answer(dolar["mensaje"])
