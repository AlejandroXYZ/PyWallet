from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
import logging
from app.handlers.utils.dolar import dolar_hoy


dolar_bcv = Router(name="dolar")
logger = logging.getLogger(__name__)


@dolar_bcv.message(Command("dolar"))
async def dolar(message: Message):
    dolar = await dolar_hoy()
    if dolar["status"]:
        await message.answer(
            f"<b>PRECIO DEL DOLAR HOY BCV</b>\n\n{dolar['precio']}\n\n",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(dolar["mensaje"])
