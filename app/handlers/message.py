from aiogram import Router
from aiogram.types import Message
from app.IA.groq import IA_Response
import json
import app.handlers.CRUD as CRUD
import logging

IA_message = Router(name="IA_message")

logger = logging.getLogger(name=__name__)


@IA_message.message()
async def analizar_mensaje(mensaje: Message):
    respuesta = IA_Response(mensaje.text)
    json_dict = json.loads(respuesta)
    match json_dict["accion"]:
        case "CREATE":
            transaccion = CRUD.create(json_dict)
            if transaccion:
                answer = f"Transaccion Completada, id: {transaccion}"
                logger.info(answer)
                await mensaje.answer(answer)
            else:
                answer = "La cuenta no es válida, verifique sus cuentas"
                logger.error(answer)
                await mensaje.answer(answer)

        case "DELETE":
            print("borrar")
        case "UPDATE":
            print("Actualizar")
        case "CONFLICT":
            print("error")
        case _:
            print("Respuesta incorrecta por parte de la IA")
