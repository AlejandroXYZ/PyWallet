from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
import logging
from aiogram.types import Message

help = Router(name="help")

logger = logging.getLogger(name=__name__)


@help.message(Command("help"))
async def mostrar_ayuda(message: Message):
    mensaje = """
    <b>PyWallet</b> es una billetera digital impulsada con IA que permite registrar transacciones facilmente
    """

    await message.answer(mensaje, parse_mode=ParseMode.HTML)
