from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
import traceback
import logging


logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self, handler, event: Message, data):
        async with self.session_pool() as session:
            data["db"] = session

            try:
                resultado = await handler(event, data)
                await session.commit()
                return resultado

            except Exception:
                await session.rollback()
                error = traceback.format_exc()
                logger.error(error)

                if isinstance(event, Message):
                    await event.answer("Hubo un error interno procesando tu solicitud.")
