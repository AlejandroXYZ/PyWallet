from operator import call
from typing import Text
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.handlers.utils.cuentas import obtener_cuentas, obtener_cuenta_especifica
from app.handlers.FSM.cuenta_fsm import CuentaFSM
import logging
from app.handlers.CRUD import new_account, delete_account
from aiogram.enums import ParseMode
from app.handlers.utils.dolar import convertidor

account = Router(name="accounts")
logger = logging.getLogger(name=__name__)


def seleccion_opciones():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Mis Cuentas", callback_data="mis_cuentas"),
        types.InlineKeyboardButton(text="Crear Cuenta", callback_data="nueva"),
        types.InlineKeyboardButton(text="Borrar Cuenta", callback_data="borrar"),
    )
    return builder.as_markup()


@account.message(Command("accounts"))
async def menu_cuentas(message: Message):
    builder = seleccion_opciones()
    await message.answer("Selecciona:", reply_markup=builder)


@account.callback_query(F.data == "mis_cuentas")
async def ver_cuentas(callback: CallbackQuery, state: CuentaFSM):
    logger.info("El usuario seleccionó Consultar sus cuentas")
    await callback.answer()
    mis_cuentas = await obtener_cuentas()
    builder = InlineKeyboardBuilder()
    if mis_cuentas:
        for i in mis_cuentas:
            builder.button(text=i.nombre, callback_data=str(i.id))
        builder.adjust(2)
        await callback.message.edit_text(
            text="Selecciona la Cuenta que deseas consultar",
            reply_markup=builder.as_markup(),
        )
        await state.set_state(CuentaFSM.consulta)
    else:
        await callback.message.delete()
        await callback.message.answer("No Tienes Cuentas Registradas")


@account.callback_query(CuentaFSM.consulta)
async def consultando_cuenta(callback: CallbackQuery, state: CuentaFSM):
    await callback.answer()
    id = int(callback.data)
    cuenta = await obtener_cuenta_especifica(id)
    await callback.message.delete()
    if cuenta["status"]:
        cuenta_encontrada = cuenta["cuenta"]
        conversion = convertidor(
            moneda=cuenta_encontrada.moneda, saldo=cuenta_encontrada.saldo
        )
        if not conversion["status"]:
            await callback.message.answer(conversion["mensaje"])
        respuesta = f"<b>{cuenta_encontrada.nombre}</b>\n\n<b>ID: {cuenta_encontrada.id}</b>\n<b>Saldo {cuenta_encontrada.moneda}:</b> {cuenta_encontrada.saldo}\nSaldo_{conversion['moneda']}: {conversion['saldo']}"

        await callback.message.answer(respuesta, parse_mode=ParseMode.HTML)
        await state.clear()
    else:
        await callback.message.answer(cuenta["mensaje"])
        await state.clear()
        return


@account.callback_query(F.data == "borrar")
async def borrar_cuenta(callback: CallbackQuery, state: CuentaFSM):
    await callback.answer()
    logger.info("El usuario elijió borrar una cuenta")
    mis_cuentas = await obtener_cuentas()
    builder = InlineKeyboardBuilder()
    if mis_cuentas:
        for i in mis_cuentas:
            builder.button(text=i.nombre, callback_data=str(i.id))
        builder.adjust(2)
        await callback.message.edit_text(
            text="Selecciona la Cuenta que deseas borrar",
            reply_markup=builder.as_markup(),
        )
        await state.set_state(CuentaFSM.borrar)


@account.callback_query(CuentaFSM.borrar)
async def borrando(callback: CallbackQuery, state: CuentaFSM):

    logger.info(f"El usuario quiere borrar la cuenta de id {callback.data}")
    await callback.answer()
    await callback.message.delete()
    cuenta = int(callback.data)
    logger.info("Eliminando Cuenta")
    borrar = await delete_account(cuenta)

    if borrar["status"]:
        logger.info("Cuenta Eliminada con éxito")
        await callback.message.answer(borrar["mensaje"])
        await state.clear()
        return
    else:
        logger.error(borrar["mensaje"])
        await callback.message.answer(borrar["mensaje"])
        return


@account.callback_query(F.data == "nueva")
async def nueva_cuenta(callback: CallbackQuery, state: CuentaFSM):
    logger.info("El usuario seleccionó Crear Cuenta")
    await callback.message.edit_text(
        "Escribe el Nombre de la cuenta de forma abreviada con 3 o 4 letras, por ejemplo: BNC,BDV,ZIN,PAY,BIN..."
    )
    await state.set_state(CuentaFSM.nombre)


@account.message(CuentaFSM.nombre)
async def establecer_moneda(message: Message, state: CuentaFSM):
    logger.info(f"El Usuario escribió: {message.text}")
    nombre = message.text
    if len(nombre) <= 4 and len(nombre) >= 3:
        data = nombre.strip().upper()
        await state.update_data(nombre=data)
        await message.answer("Escribe El tipo de Moneda a usar\n\nVES\nUSD\nUSDT")
        await state.set_state(CuentaFSM.moneda)
    else:
        logger.info("El usuario escribió un nombre de cuenta no válido")
        await message.answer(
            "El Nombre de la cuenta debe ser solo 3 o 4 Letras, intente de nuevo"
        )


@account.message(CuentaFSM.moneda)
async def crear_cuenta(message: Message, state: CuentaFSM):
    logger.info(f"El usuario escribió: {message.text}")
    moneda = message.text
    if len(moneda) <= 4 and len(moneda) >= 3:
        moneda_data = moneda.strip().upper()
        await state.update_data(moneda=moneda_data)
        data = await state.get_data()
        cuenta = await new_account(data)
        if cuenta["status"]:
            logger.info("Creando Cuenta")
            await message.answer(cuenta["mensaje"])
            logger.info("Cuenta Creada Correctamente")
            await state.clear()
            return
        else:
            logger.error(cuenta["mensaje"])
            await message.answer(cuenta["mensaje"])
            await state.clear()
            return
    else:
        logger.info("El usuario escribió un nombre de Moneda no válido")
        await message.answer(
            "El Nombre de Moneda debe ser solo 3 Letras, intente de nuevo"
        )
