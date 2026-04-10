from aiogram import Router, Bot, Dispatcher
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal
from app.models.user import Usuarios
from datetime import datetime
import logging
import traceback
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.handlers.FSM.start import Inicio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from app.handlers.FSM.admin_users import AdminUsersFSM
from app.models.users_allow import UsuariosPermitidos
import os

start_router = Router(name="start")
logger = logging.getLogger(name=__name__)
admin_id = os.getenv("ADMIN_ID")


class AuthCallback(CallbackData, prefix="auth"):
    action: str
    user_id: int


@start_router.message(StateFilter(Inicio.rechazada, Inicio.esperando_respuesta))
async def ignorar_mensajes_rechazados(message: Message):
    return


@start_router.callback_query(StateFilter(Inicio.rechazada, Inicio.esperando_respuesta))
async def ignorar_botones_rechazados(callback: CallbackQuery):
    await callback.answer(
        "Uso no Permitido",
        show_alert=True,
    )


@start_router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    permitidos: set,
    registrados: dict,
):
    logger.info("Iniciando Bot..")
    if message.from_user.id in registrados:
        logger.info(
            f"El usuario {message.from_user.id} ya estaba registrado. Acceso directo."
        )
        await message.answer(
            "¡Hola de nuevo! Ya tienes acceso a Pywallet. Usa /help para ver los comandos disponibles.",
            parse_mode=ParseMode.HTML,
        )
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="SI",
            callback_data=AuthCallback(
                action="si", user_id=f"{message.from_user.id}"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="NO",
            callback_data=AuthCallback(
                action="no", user_id=f"{message.from_user.id}"
            ).pack(),
        ),
    )
    await message.answer(
        """<b>Bienvenido a Pywallet, Se ha enviado una solicitud de confirmación al admin para que uses el bot, por favor espera</b>""",
        parse_mode=ParseMode.HTML,
    )
    await message.bot.send_message(
        chat_id=admin_id,
        text=f"El Usuario {message.from_user.id}, @{message.from_user.username} desea usar el bot. Permitir?",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(Inicio.esperando_respuesta)


@start_router.callback_query(AuthCallback.filter())
async def handle_admin_auth(
    callback: CallbackQuery,
    registrados: dict,
    permitidos: set,
    callback_data: AuthCallback,
    bot: Bot,
    db: AsyncSession,
    state: FSMContext,
    dp: Dispatcher,
):
    action = callback_data.action
    user_id = int(callback_data.user_id)
    await callback.message.edit_text(
        text=f"Solicitud del usuario {user_id} resuelta: {'APROBADA' if action == 'si' else 'RECHAZADA'}."
    )
    estado_usuario = FSMContext(
        storage=dp.storage,
        key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id),
    )

    if action == "si":
        await estado_usuario.clear()
        await bot.send_message(
            chat_id=user_id,
            text=" ¡Tu solicitud ha sido aprobada por el administrador! Ya puedes usar Pywallet.",
        )
        await state.update_data(telegram_id=user_id)
        info_usuario = await bot.get_chat(user_id)
        nombre = info_usuario.full_name or f"Usuario_{user_id}"
        await registro_nuevo_usuario(user_id, nombre, db, registrados, permitidos)

    elif action == "no":
        await estado_usuario.set_state(Inicio.rechazada)
        await bot.send_message(
            chat_id=user_id,
            text="Lo siento, tu solicitud de acceso ha sido denegada por el administrador.",
        )
    await callback.answer()


async def registro_nuevo_usuario(
    user_id: int,
    full_name: str,
    db: AsyncSession,
    registrados: set,
    permitidos: dict,
):
    try:
        logger.info("Creando Cuenta para el nuevo usuario")

        nuevo_permitido = UsuariosPermitidos(nombre=full_name, telegram_id=user_id)
        db.add(nuevo_permitido)
        await db.flush()
        permitidos[user_id] = full_name
        logger.info(f"Usuario: {full_name} Añadido a la lista de Usuarios Permitidos")
        if user_id in registrados:
            logger.info(
                f"Usuario ya está registrado con el nombre: {permitidos[user_id]}"
            )
            return

        usuario = Usuarios(
            alias=full_name,
            fecha_registro=datetime.now(),
            ultima_vez=datetime.now(),
            id_permitido=user_id,
        )

        db.add(usuario)
        await db.flush()
        await db.refresh(usuario)
        registrados.add(user_id)
        logger.info(
            f"Cuenta del Usuario ID: {user_id} de alias: {full_name} Creada Correctamente"
        )

    except Exception as e:
        error = traceback.format_exc()
        logger.error(error)
        logger.error(f"Ha Ocurrido un error: {e}")
        raise e
