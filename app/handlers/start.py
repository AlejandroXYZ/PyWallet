from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.dbsession import DBSessionMiddleware
from app.db.connection import SessionLocal
from app.handlers.help import help
from app.models.user import Usuarios
from datetime import datetime
import logging
import traceback

start_router = Router(name="start")
logger = logging.getLogger(name=__name__)
start_router.message.middleware(DBSessionMiddleware(SessionLocal))


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info("Iniciando Bot..")
    await message.answer("""<b>Bienvenido a Pywallet</b>""", parse_mode=ParseMode.HTML)


@start_router.message(Command("iniciar"))
async def bienvenida(
    message: Message, db: AsyncSession, registrados: set, permitidos: dict
):
    try:
        logger.info("Creando Cuenta para el nuevo usuario")

        if message.from_user.id in registrados:
            logger.info(
                f"Usuario ya está registrado con el nombre: {permitidos[message.from_user.id]}"
            )
            await message.answer("Ya estás registrado")
            return

        usuario = Usuarios(
            alias=message.from_user.full_name,
            fecha_registro=datetime.now(),
            ultima_vez=datetime.now(),
            id_permitido=message.from_user.id,
        )
        db.add(usuario)
        await db.flush()
        await db.refresh(usuario)
        registrados.add(message.from_user.id)

        logger.info(
            f"Cuenta del Usuario ID: {message.from_user.id} de alias: {message.from_user.full_name} Creada Correctamente"
        )
        await message.answer(
            "Felicidades, Ya se ha creado tú usuario, ahora puedes usar el Bot, si quieres aprender a usarlo escribe: '/help'"
        )
        return
    except Exception as e:
        error = traceback.format_exc()
        logger.error(error)
        logger.error(f"Ha Ocurrido un error: {e}")
        await message.answer(
            "Ha ocurrido un Error interno mientras se creaba tu usuario"
        )
