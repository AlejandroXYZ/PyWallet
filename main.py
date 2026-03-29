import asyncio
import logging
from contextlib import asynccontextmanager
from app.bot.main_bot import setup_bot
import os
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)
webhook_url = os.getenv("WEBHOOK_URL", "https://dominio-publico.com")
environment = os.getenv("ENVIRONMENT", "development")


@asynccontextmanager
async def lifespan():
    bot, dp = await setup_bot()

    if environment == "development":
        logger.info("Modo Desarrollo")
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(
            dp.start_polling(bot, allowed_updates=["message", "callback_query"])
        )
        yield
        polling_task.cancel()

    else:
        logger.info("Modo Producción")

        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=(True),
            allowed_updates=["message", "callback_query"],
        )

        yield

        await bot.delete_webhook()
        await bot.session.close()


async def run_bot():
    async with lifespan():
        logger.info("Bot en ejecución... Presiona Ctrl+C para detener.")
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente")
