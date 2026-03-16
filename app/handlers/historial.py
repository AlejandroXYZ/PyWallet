from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command 

historial = Router(name="historial")

@historial.message(Command(prefix="/historial"))
async def obtener_transacciones():

