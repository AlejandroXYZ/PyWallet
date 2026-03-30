from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from app.handlers.utils.csv import generar_csv

logger = logging.getLogger(__name__)
data_router = Router(name="data")


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
async def estadisticas(callback: types.CallbackQuery):
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
async def csv(callback: CallbackQuery):
    await callback.answer("Generando CSV")
    archivo = generar_csv()
    bufer = BufferedInputFile(file=archivo, filename="Historial.csv")
    await callback.message.delete()
    await callback.message.answer_document(document=bufer, caption="Historial CSV")
