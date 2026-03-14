from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

start_router = Router(name="start")


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("""<b>Bienvenido a Pywallet</b>""", parse_mode=ParseMode.HTML)
