from operator import call
from aiogram import Router, types
from aiogram.methods import edit_chat_invite_link
from aiogram.types import InlineKeyboardButton, Message, message, reply_keyboard_markup
from aiogram.filters import Command
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.FSM.historial_fsm import HistorialFSM
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.handlers.utils.cuentas import obtener_cuentas
from app.handlers.utils.transacciones import obtener_transacciones
import logging
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal


historial = Router(name="historial")
logger = logging.getLogger(name=__name__)


async def get_keyboard_historial(db: AsyncSession, id: int):
    logging.info("Mostrando Cuentas al Usuario")
    builder = InlineKeyboardBuilder()
    cuentas = await obtener_cuentas(db, id)
    botones = []
    if not cuentas:
        logger.info("No Hay Cuentas Creadas")
        return False

    for i in cuentas:
        boton = types.InlineKeyboardButton(
            text=i.nombre, callback_data=f"{i.id}:{i.nombre}"
        )
        botones.append(boton)

    builder.row(*botones)
    return builder.as_markup()


@historial.message(Command("historial"))
async def cmd_historial(mensaje: Message, state: FSMContext, db: AsyncSession):
    try:
        logger.info("Capturando mensaje")
        keyboard = await get_keyboard_historial(db, mensaje.from_user.id)
        if not keyboard:
            await mensaje.answer("No hay Cuentas Creadas, Crea una Primero")
        else:
            await mensaje.answer("Qué cuenta deseas consultar??", reply_markup=keyboard)
            await state.set_state(HistorialFSM.cuenta)
    except Exception as e:
        logger.error(f"Ha ocurrido un error:\n\n{e}\n\n")


@historial.callback_query(HistorialFSM.cuenta)
async def cantidad(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    cuenta = callback.data.split(":")
    await state.update_data(cuenta=cuenta[0])
    logger.info(f"El Usuario eligió: {callback.data}")

    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="5", callback_data="5"),
        types.InlineKeyboardButton(text="15", callback_data="15"),
        types.InlineKeyboardButton(text="25", callback_data="25"),
        types.InlineKeyboardButton(text="50", callback_data="50"),
        types.InlineKeyboardButton(text="Volver", callback_data="volver"),
    )

    await callback.message.edit_text(
        f"Has Elegido {cuenta[1]}, ahora elije la cantidad de transacciones a ver",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(HistorialFSM.cantidad)


@historial.callback_query(HistorialFSM.cantidad)
async def fecha(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "volver":
        await state.set_state(HistorialFSM.cuenta)
        await callback.message.edit_text(
            text="Qué Cuenta deseas Consultar??", reply_markup=get_keyboard_historial()
        )
        logger.info("El usuario eligió: 'Volver'")
        return
    await callback.answer()

    cantidad = callback.data
    logger.info(f"El Usuario eligió cantidad: {callback.data} ")
    await state.update_data(cantidad=cantidad)

    builder = InlineKeyboardBuilder()

    botones = [
        types.InlineKeyboardButton(text="Hoy", callback_data="hoy"),
        types.InlineKeyboardButton(text="Ayer", callback_data="ayer"),
        types.InlineKeyboardButton(text="Semana Pasada", callback_data="semana"),
        types.InlineKeyboardButton(text="Mes", callback_data="mes"),
        types.InlineKeyboardButton(text="6 Meses", callback_data="6 meses"),
        types.InlineKeyboardButton(text="Volver", callback_data="volver"),
    ]
    builder.row(*botones)
    builder.adjust(2)

    await callback.message.edit_text(
        f"Has Elegido {cantidad} transacciones para ver",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(HistorialFSM.fecha)


@historial.callback_query(HistorialFSM.fecha)
async def finalizar_historial(
    callback: types.CallbackQuery, state: FSMContext, db: AsyncSession
):

    await callback.answer()
    await callback.message.delete()
    fecha = callback.data
    await state.update_data(fecha=fecha)
    data = await state.get_data()
    logger.info(f"El usuario eligió fecha: {fecha}\n\n\n{data}\n\n\n")
    respuesta = await obtener_transacciones(data, db, callback.message.from_user.id)
    if respuesta["status"]:
        logger.info(f"Resultados:\n\n{respuesta['registros']}")
        await callback.message.answer(respuesta["registros"], parse_mode=ParseMode.HTML)
        await state.clear()

    else:
        logging.error(f"Error {respuesta['mensaje']}")
        await callback.message.answer(respuesta["mensaje"])
