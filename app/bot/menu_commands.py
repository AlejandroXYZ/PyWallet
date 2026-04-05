from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
import logging

logger = logging.getLogger(__name__)


async def setup_commands(bot: Bot, usuarios: dict):
    commands = [
        BotCommand(command="help", description="Ver ayuda"),
        BotCommand(command="resumen", description="Resumen Financiero"),
        BotCommand(command="dolar", description="Obtener precio del Dolar BCV"),
        BotCommand(
            command="historial", description="Menú de Historiales de Transacciones"
        ),
        BotCommand(command="accounts", description="Menú de Cuentas"),
        BotCommand(command="datos", description="Analisis de datos"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

    commands_admin = [BotCommand(command="users", description="Gestionar usuarios")]
    comandos_totales = commands + commands_admin
    for id, nombre in usuarios.items():
        if nombre == "ADMIN":
            try:
                await bot.set_my_commands(
                    comandos_totales, scope=BotCommandScopeChat(chat_id=id)
                )
            except Exception as e:
                logger.error(e)
                logger.warning("No se pudo configurar menú para admins")
