from aiogram import Router, F
from aiogram.types import Message, message
from sqlalchemy.ext.asyncio import AsyncSession
from app.IA.groq import IA_Response
import json
import app.handlers.CRUD as CRUD
import logging
import os
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal

IA_message = Router(name="IA_message")
IA_message.message.middleware(DBSessionMiddleware(SessionLocal))

logger = logging.getLogger(name=__name__)
user_id = int(os.getenv("ID_USUARIO", 0))


@IA_message.message(F.text.regexp(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]"))
async def analizar_mensaje(mensaje: Message, db: AsyncSession):
    logger.info(f"user id: {user_id}\nUser mensaje: {mensaje.from_user.id}")
    if mensaje.from_user.id == user_id:
        respuesta = await IA_Response(mensaje.text)
        json_dict = json.loads(respuesta)
        logger.info(f"respuesta de Groq:\n\n{json_dict}")
        match json_dict["accion"]:
            case "CREATE":
                transaccion = await CRUD.create(json_dict, db)
                if transaccion:
                    answer = f"Transaccion Completada id:{transaccion[0]}\n\n{json_dict['comentario']}\n\nSaldo en tu cuenta {transaccion[2]}: {transaccion[1]}"
                    logger.info(answer)
                    await mensaje.answer(answer)
                else:
                    answer = "La cuenta no es válida, verifique sus cuentas"
                    logger.error(answer)
                    await mensaje.answer(answer)

            case "DELETE":
                transaccion = await CRUD.delete(json_dict, db)
                if transaccion["status"]:
                    await mensaje.answer(transaccion["mensaje"])
                else:
                    await mensaje.answer(f"{transaccion['mensaje']}")

            case "CONFLICT":
                await mensaje.answer(respuesta)
            case _:
                print("Respuesta incorrecta por parte de la IA")
    else:
        logger.error("Usuario no permitido")
        return
