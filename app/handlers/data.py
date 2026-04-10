from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.handlers.utils.exportar import generar_csv
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal
from app.handlers.utils.graficas import (
    grafico_evolucion_gastos,
    extraer_transacciones,
    generar_reporte_texto,
)
import asyncio

logger = logging.getLogger(__name__)
data_router = Router(name="data")
data_router.message.middleware(DBSessionMiddleware(SessionLocal))
data_router.callback_query.middleware(DBSessionMiddleware(SessionLocal))


@data_router.message(Command("datos"))
async def data(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="exportar datos", callback_data="exportar"),
        types.InlineKeyboardButton(text="Gráficas", callback_data="graficas"),
    )
    builder = builder.as_markup()
    await message.answer("Selecciona:", reply_markup=builder)


@data_router.callback_query(F.data == "exportar")
async def exportar(callback: types.CallbackQuery):
    logger.info("El Usuario eligió Exportar")
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Historial CSV", callback_data="csv"),
        types.InlineKeyboardButton(text="Backup SQL", callback_data="sql"),
    )
    await callback.message.edit_text(
        text="Qué deseas?", reply_markup=builder.as_markup()
    )


@data_router.callback_query(F.data == "csv")
async def csv(callback: CallbackQuery, db: async_sessionmaker):
    await callback.answer("Generando CSV")
    archivo = await generar_csv(db, callback.from_user.id)
    bufer = BufferedInputFile(file=archivo, filename="Historial.csv")
    await callback.message.delete()
    await callback.message.answer_document(document=bufer, caption="Historial CSV")


@data_router.callback_query(F.data == "sql")
async def sql(callback: CallbackQuery):
    await callback.answer("Generando SQL")
    await callback.message.delete()
    await callback.message.answer("Opción no Disponible por Ahora")


@data_router.callback_query(F.data == "graficas")
async def elegir_grafica(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Evolución de Gastos", callback_data="gastos_evolucion"
        ),
        types.InlineKeyboardButton(text="Gastos del Mes", callback_data="gastos_mes"),
    )
    await callback.message.edit_text("Selecciona:", reply_markup=builder.as_markup())


@data_router.callback_query(F.data == "gastos_evolucion")
async def gastos_evolucion(callback: CallbackQuery, db: AsyncSession):
    await callback.answer()
    datos = await extraer_transacciones(db=db, id=callback.from_user.id)
    if datos.empty:
        logger.info("El usuario no tiene datos para hacer la gráfica")
        await callback.message.answer("No hay Datos para hacer la gráfica")
        return
    grafica = await asyncio.to_thread(grafico_evolucion_gastos, datos)
    if not grafica:
        await callback.message.answer("No se pudo hacer la gráfica")
        logger.error(
            f"Error al hacer la gráfica de evolución para el usuario: {callback.from_user.id}"
        )
    imagen = BufferedInputFile(file=grafica, filename="Evolucion de gastos")
    await callback.message.answer_photo(photo=imagen, caption="Evolución de tus gastos")


@data_router.callback_query(F.data == "gastos_mes")
async def gastos_mes(callback: CallbackQuery, db: AsyncSession):
    await callback.answer()
    datos = await extraer_transacciones(db=db, id=callback.from_user.id)
    if datos.empty:
        logger.info("El usuario no tiene datos para hacer la gráfica")
        await callback.message.answer("No hay Datos para hacer la gráfica")
        return
    grafica = await asyncio.to_thread(generar_reporte_texto, datos)
    if not grafica:
        await callback.message.answer("No se pudo hacer la gráfica")
        logger.error(
            f"Error al hacer la gráfica para el usuario: {callback.from_user.id}"
        )
    await callback.message.answer(grafica, parse_mode="HTML")
    logger.info("Grafica enviada al usuario")
