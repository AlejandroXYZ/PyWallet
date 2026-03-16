from operator import call
from aiogram import Router, types
from aiogram.methods import edit_chat_invite_link
from aiogram.types import InlineKeyboardButton, Message, reply_keyboard_markup
from aiogram.filters import Command
from app.handlers.FSM.historial_fsm import HistorialFSM
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.handlers.utils.cuentas import obtener_cuentas

historial = Router(name="historial")


def get_keyboard_historial():
    builder = InlineKeyboardBuilder()
    cuentas = obtener_cuentas()
    botones = []
    for i in cuentas:
        boton = types.InlineKeyboardButton(
            text=i.nombre, callback_data=f"{i.id}:{i.nombre}"
        )
        botones.append(boton)

    builder.row(*botones)
    return builder.as_markup()


@historial.message(Command("historial"))
async def cmd_historial(mensaje: Message, state: FSMContext):
    await mensaje.answer(
        "Qué cuenta deseas consultar??", reply_markup=get_keyboard_historial()
    )
    await state.set_state(HistorialFSM.cuenta)


@historial.callback_query(HistorialFSM.cuenta)
async def cantidad(callback: types.CallbackQuery, state: FSMContext):
    cuenta = callback.data.split(":")
    await state.update_data(cuenta=cuenta[0])

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
        return
    cantidad = callback.data
    await state.update_data(cantidad=cantidad)

    builder = InlineKeyboardBuilder()

    botones = [
        types.InlineKeyboardButton(text="Hoy", callback_data="hoy"),
        types.InlineKeyboardButton(text="Ayer", callback_data="Ayer"),
        types.InlineKeyboardButton(text="Semana Pasada", callback_data="Semana Pasada"),
        types.InlineKeyboardButton(text="Mes Pasado", callback_data="Mes Pasado"),
        types.InlineKeyboardButton(text="6 Meses", callback_data="6 Meses"),
        types.InlineKeyboardButton(text="Volver", callback_data="volver"),
    ]
    builder.row(*botones)
    builder.adjust(2)

    await callback.message.edit_text(
        f"Has Elegido {cantidad} transacciones para ver",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(HistorialFSM.fecha)
