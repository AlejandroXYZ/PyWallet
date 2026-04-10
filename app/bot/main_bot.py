from aiogram.filters import ExceptionTypeFilter
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from app.handlers.start import start_router
from app.handlers.message import IA_message
from app.handlers import historial
from app.bot.menu_commands import setup_commands
from app.handlers.help import help
from app.handlers.cuentas import account
from app.handlers.resumen import resumen
from app.handlers.data import data_router
from app.handlers.dolar import dolar_bcv
from app.middleware.user_auth import AuthUser
from app.db.connection import SessionLocal
from app.middleware.dbsession import DBSessionMiddleware
from app.handlers.admin import admin_router
from app.bot.errors_catcher import error_catcher
import logging

logger = logging.getLogger(__name__)


async def setup_bot(usuarios_permitidos):
    """Función Constructora, prepara al Bot y el Dispatcher"""
    token = os.getenv("TOKEN")
    if not token:
        logger.error("Error el token del bot no se encuentra")
        raise ValueError("Error el Token del Bot no se encuentra")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    auth_user = AuthUser()

    await auth_user.crear_usuario_admin()
    await auth_user.cargar_usuarios_permitidos()

    dp.errors.register(error_catcher, ExceptionTypeFilter(Exception))
    dp.message.outer_middleware(auth_user)
    dp.callback_query.middleware(auth_user)
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(help)
    dp.include_router(account)
    dp.include_router(resumen)
    dp.include_router(historial.historial)
    dp.include_router(IA_message)
    dp.include_router(data_router)
    dp.include_router(dolar_bcv)
    await setup_commands(bot=bot, usuarios=auth_user.ALLOW_USERS)
    return bot, dp
