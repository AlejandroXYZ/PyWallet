import re
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.dbsession import DBSessionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.db.connection import SessionLocal
from app.handlers.FSM.admin_users import AdminUsersFSM
from app.models.users_allow import UsuariosPermitidos
from aiogram.enums import ParseMode
import logging


admin_router = Router(name="admin_router")
admin_router.message.middleware(DBSessionMiddleware(SessionLocal))

logger = logging.getLogger(__name__)


@admin_router.message(Command("users"))
async def new_user(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Añadir", callback_data="añadir"),
        types.InlineKeyboardButton(text="Borrar", callback_data="borrar"),
        types.InlineKeyboardButton(text="Listar", callback_data="listar"),
    )
    await message.answer(text="Selecciona:", reply_markup=builder.as_markup())


@admin_router.callback_query(F.data == "añadir")
async def id_usuario(callback: CallbackQuery, state: AdminUsersFSM):
    await state.set_state(AdminUsersFSM.telegram_id)
    await callback.answer()
    await callback.message.edit_text(text="Escribe el ID del Usuario que deseas Añadir")


@admin_router.message(AdminUsersFSM.telegram_id)
async def verificar_id(message: Message, state: AdminUsersFSM, permitidos: dict):
    patron = re.compile(r"\d+")
    verificar = bool(patron.fullmatch(string=message.text))
    if not verificar:
        logger.info(f"El Admin escribió un Código no válido: {message.text}")
        await message.answer("Código no válido, Intenta de Nuevo")
    elif int(message.text) in permitidos:
        logger.info("El Usuario ya está registrado")
        await message.answer("El Usuario ya está registrado como Usuario Permitido")
        await state.clear()
    else:
        logger.info(f"El admin desea añadir este ID: {message.text}")
        await state.update_data(telegram_id=int(message.text))
        await message.answer("Escribe el Nombre del Nuevo Usuario")
        await state.set_state(AdminUsersFSM.nombre_usuario)


@admin_router.message(AdminUsersFSM.nombre_usuario)
async def nuevo_usuario(
    message: Message, state: AdminUsersFSM, db: AsyncSession, permitidos: dict
):
    logger.info("Nombre del Nuevo Usuario: {message.text}")
    datos = await state.get_data()
    usuario = UsuariosPermitidos(nombre=message.text, telegram_id=datos["telegram_id"])
    db.add(usuario)
    await db.flush()
    await db.refresh(usuario)
    logger.info("Usuario Añadido Correctamente")
    permitidos[datos["telegram_id"]] = message.text
    await message.answer(f"Usuario {message.text} Añadido Correctamente")
    await state.clear()


@admin_router.callback_query(F.data == "listar")
async def listar_usuarios(callback: CallbackQuery, permitidos: dict):
    await callback.answer()
    texto = ""
    for i, x in permitidos.items():
        texto_para_añadir = f"<b>Usuario:</b> {x}    <b>ID:</b> {i}\n"
        texto += texto_para_añadir
    await callback.message.answer(
        f"<b>Usuarios:</b>\n\n{texto}", parse_mode=ParseMode.HTML
    )


@admin_router.callback_query(F.data == "borrar")
async def borrar_usuario(callback: CallbackQuery, state: AdminUsersFSM):
    logger.info("El Admin desea eliminar un Usuario de la lista de permitidos")
    await callback.answer()
    await callback.message.answer("Escribe el ID del Usuario que deseas eliminar")
    await state.set_state(AdminUsersFSM.borrar)


@admin_router.message(AdminUsersFSM.borrar)
async def eliminando(
    message: Message, db: AsyncSession, state: AdminUsersFSM, permitidos: dict
):
    patron = re.compile(r"\d+")
    busqueda = bool(patron.fullmatch(message.text))
    if not busqueda:
        logger.info(f"El Admin escribió un ID no válido: {message.text}")
        await message.answer("ID no Válido")
        await state.clear()
        return
    elif int(message.text) not in permitidos:
        logger.info("El Usuario no Existe en la lista de permitidos")
        await message.answer("Usuario no encontrado")
        await state.clear()
        return
    else:
        logger.info("Eliminando Usuario")
        query = await db.execute(
            select(UsuariosPermitidos).filter(
                UsuariosPermitidos.telegram_id == int(message.text)
            )
        )
        usuario = query.scalar_one_or_none()
        await db.delete(usuario)
        await db.flush()
        nombre = permitidos.pop(int(message.text), None)
        logger.info(f"Usuario {nombre} eliminado")
        await message.answer(f"Usuario {nombre} Eliminado Correctamente")
