from aiogram import Router
from aiogram.types import Message
from app.IA.groq import IA_Response


IA_message = Router(name="IA_message")


@IA_message.message()
async def analizar_mensaje(mensaje: Message):
    respuesta = IA_Response(mensaje.text)
    await mensaje.answer(respuesta)
