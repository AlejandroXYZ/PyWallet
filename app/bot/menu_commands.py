from aiogram import Bot
from aiogram.types import BotCommand


async def setup_commands(bot: Bot):
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
    await bot.set_my_commands(commands)
