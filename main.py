import asyncio
import logging
import sys
import os
from aiohttp import web
from sqlalchemy import select

from app.bot.main_bot import setup_bot
from app.db.connection import SessionLocal
from app.models.users_allow import UsuariosPermitidos
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SERVIDOR_URL = os.getenv("SERVIDOR_URL", "https://dominio-publico.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{SERVIDOR_URL}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 10000))


async def ping_handler(request):
    """Mantiene el bot vivo en Render para UptimeRobot"""
    return web.Response(text="EL bot está encendido y el servidor web responde.")


async def get_allowed_users():
    """Obtiene los usuarios permitidos de la DB"""
    async with SessionLocal() as db:
        query = await db.execute(select(UsuariosPermitidos.telegram_id))
        return set(query.scalars().all())


async def main():
    usuarios_permitidos = await get_allowed_users()
    bot, dp = await setup_bot(usuarios_permitidos)

    if ENVIRONMENT == "development":
        logger.info("Iniciando en Modo Desarrollo (Polling)...")
        await bot.delete_webhook(drop_pending_updates=True)

        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

    else:
        logger.info("🚀 Iniciando en Modo Producción (Webhook)...")

        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        logger.info(f"WebHook configurado en: {WEBHOOK_URL}")

        app = web.Application()
        app.router.add_get("/", ping_handler)

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        logger.info(f"Servidor Webhook corriendo en el puerto {PORT}")

        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
        finally:
            logger.info("Apagando y limpiando recursos...")
            await bot.delete_webhook()
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente")
