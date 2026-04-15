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
from app.handlers.utils.cuentas import obtener_cuentas

IA_message = Router(name="IA_message")

logger = logging.getLogger(name=__name__)


@IA_message.message(F.text.regexp(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]"))
async def analizar_mensaje(mensaje: Message, db: AsyncSession):
    logger.info(f"user id: {mensaje.from_user.id}\nUser mensaje: {mensaje.text}")
    cuentas = await obtener_cuentas(db, mensaje.from_user.id)
    if not cuentas:
        message.answer(
            "No se encontraron Cuentas, crea una cuenta antes de empezar a registrar"
        )
        logger.info("No se obtuvieron Cuentas, el usuario no tiene cuentas")
        return
    nombres_cuentas = []
    nombres_cuentas = [cuenta.nombre for cuenta in cuentas]
    respuesta = await IA_Response(mensaje.text, nombres_cuentas)
    respuesta_limpia = respuesta.strip("`").removeprefix("json").strip()
    json_dict = json.loads(respuesta_limpia)
    logger.info(f"respuesta de Groq:\n\n{json_dict}")
    match json_dict["accion"]:
        case "CREATE":
            transaccion = await CRUD.create(json_dict, db, mensaje.from_user.id)
            if transaccion["status"]:
                answer = f"Transaccion Completada id:{transaccion['id']}\n\n{json_dict['comentario']}\n\nSaldo en tu cuenta {transaccion['nombre']}: {transaccion['saldo']}"
                logger.info(answer)
                await mensaje.answer(answer)
            else:
                answer = transaccion["mensaje"]
                logger.error(answer)
                await mensaje.answer(answer)

        case "DELETE":
            transaccion = await CRUD.delete(json_dict, db)
            if transaccion["status"]:
                await mensaje.answer(transaccion["mensaje"])
            else:
                await mensaje.answer(f"{transaccion['mensaje']}")

        case "CONFLICT":
            await mensaje.answer(
                f"Te falta especificar: {json_dict['falta']}, en tu mensaje"
            )
        case _:
            print("Respuesta incorrecta por parte de la IA")
