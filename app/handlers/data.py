from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.handlers.utils.exportar import generar_csv
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal

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
