from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.utils.cuentas import obtener_cuentas, obtener_cuenta_especifica
from app.handlers.FSM.cuenta_fsm import CuentaFSM
import logging
from app.handlers.CRUD import new_account, delete_account
from aiogram.enums import ParseMode
from app.handlers.utils.dolar import convertidor
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal

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
async def ver_cuentas(callback: CallbackQuery, state: CuentaFSM, db: AsyncSession):
    logger.info(f"El usuario {callback.from_user.id} seleccionó Consultar sus cuentas")
    await callback.answer()
    mis_cuentas = await obtener_cuentas(db, callback.from_user.id)
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
async def consultando_cuenta(
    callback: CallbackQuery, state: CuentaFSM, db: AsyncSession
):
    await callback.answer()
    id = callback.data
    cuenta = await obtener_cuenta_especifica(id, db)
    await callback.message.delete()
    if cuenta["status"]:
        cuenta_encontrada = cuenta["cuenta"]
        conversion = await convertidor(
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
async def borrar_cuenta(callback: CallbackQuery, state: CuentaFSM, db: AsyncSession):
    await callback.answer()
    logger.info("El usuario elijió borrar una cuenta")
    mis_cuentas = await obtener_cuentas(db, callback.from_user.id)
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
    else:
        logger.info("El usuario no tiene cuentas que borrar")
        await callback.message.answer("No hay Cuentas, Crea una primero")


@account.callback_query(CuentaFSM.borrar)
async def borrando(callback: CallbackQuery, state: CuentaFSM, db: async_sessionmaker):

    logger.info(f"El usuario quiere borrar la cuenta de id {callback.data}")
    await callback.answer()
    await callback.message.delete()
    cuenta = int(callback.data)
    logger.info("Eliminando Cuenta")
    borrar = await delete_account(cuenta, db)

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
    logger.info(f"El usuario {callback.from_user.id}seleccionó Crear Cuenta")
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
        await message.answer("Escribe El tipo de Moneda a usar\n\nVES\nUSD")
        await state.set_state(CuentaFSM.moneda)
    else:
        logger.info("El usuario escribió un nombre de cuenta no válido")
        await message.answer(
            "El Nombre de la cuenta debe ser solo 3 o 4 Letras, intente de nuevo"
        )


@account.message(CuentaFSM.moneda)
async def crear_cuenta(
    message: Message, state: CuentaFSM, db: AsyncSession, registrados: dict
):
    logger.info(f"El usuario escribió: {message.text}")
    moneda = message.text
    monedas_permitidas = ["VES", "USD"]
    moneda_data = moneda.strip().upper()
    if len(moneda) <= 4 and len(moneda) >= 3 and moneda_data:
        if moneda_data in monedas_permitidas:
            await state.update_data(moneda=moneda_data)
            datos = await state.get_data()
            datos["telegram_id"] = message.from_user.id
            cuenta = await new_account(message=datos, registrados=registrados, db=db)
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
            logger.info(
                "El Usuarió {message.from_user.id} escribió {message.text} y no se pudo crear la cuenta porque no es una moneda permitida"
            )
            await message.answer("Por favor asegurate de escribir una moneda válida")
    else:
        logger.info("El usuario escribió un nombre de Moneda no válido")
        await message.answer(
            "El Nombre de Moneda debe ser solo 3 Letras, intente de nuevo"
        )
