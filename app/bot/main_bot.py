from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from app.handlers.start import start_router
from app.handlers.message import IA_message

token = os.getenv("TOKEN")

if token:

    def setup_bot():
        """Función Constructora, prepara al Bot y el Dispatcher para FastAPI"""

        bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        dp = Dispatcher()

        dp.include_router(start_router)
        dp.include_router(IA_message)
        return bot, dp

    bot, dp = setup_bot()

else:
    print("No encontró el token")
