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
    logger.info(f"respuesta de Groq:\n\n{json_dict}")
    match json_dict["accion"]:
        case "CREATE":
            transaccion = CRUD.create(json_dict)
            if transaccion:
                answer = f"Transaccion Completada id:{transaccion[0]}\n\n{json_dict['comentario']}\n\nSaldo en tu cuenta {transaccion[2]}: {transaccion[1]}"
                logger.info(answer)
                await mensaje.answer(answer)
            else:
                answer = "La cuenta no es válida, verifique sus cuentas"
                logger.error(answer)
                await mensaje.answer(answer)

        case "DELETE":
            transaccion = CRUD.delete(json_dict)
            if transaccion["status"]:
                await mensaje.answer(transaccion["mensaje"])
            else:
                await mensaje.answer(f"{transaccion['mensaje']}")

        case "UPDATE":
            print("Actualizar")
        case "CONFLICT":
            await mensaje.answer(respuesta)
        case _:
            print("Respuesta incorrecta por parte de la IA")
