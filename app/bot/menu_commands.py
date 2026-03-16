from aiogram import Bot
from aiogram.types import BotCommand


async def setup_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Iniciar el bot"),
        BotCommand(command="help", description="Ver ayuda"),
        BotCommand(
            command="historial", description="Menú de Historiales de Transacciones"
        ),
    ]
    await bot.set_my_commands(commands)
