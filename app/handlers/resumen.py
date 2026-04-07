import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.utils.dolar import dolar_hoy
from app.handlers.utils.cuentas import obtener_cuentas, obtener_total
from aiogram.enums import ParseMode
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal

resumen = Router(name="resumen")
logger = logging.getLogger(name=__name__)
resumen.message.middleware(DBSessionMiddleware(SessionLocal))


@resumen.message(Command("resumen"))
async def obtener_resumen(message: Message, db: AsyncSession):
    dolar = await dolar_hoy()
    cuentas = await obtener_cuentas(db, message.from_user.id)
    total = await obtener_total(db, message.from_user.id)
    if not total:
        total = "Error, no se pudo obtener los totales"
    texto_cuentas = ""
    if cuentas:
        for i in cuentas:
            texto = f"{i.nombre}: {i.saldo} {i.moneda}\n"
            texto_cuentas += texto
    else:
        texto_cuentas = "No hay Cuentas Creadas"

    if not dolar["status"]:
        logger.error("No se pudo obtener el precio del dolar")
        dolar = "No se pudo obtener el precio del dolar"

    respuesta = f"<b>Resumen Financiero</b>\n\nPrecio Dolar Hoy: {dolar['precio']}\n\n<b>Cuentas</b>\n{texto_cuentas}\n\n<b>Dinero Total por Moneda</b>\n{total['por_moneda']}\n\n"
    await message.answer(respuesta, parse_mode=ParseMode.HTML)
