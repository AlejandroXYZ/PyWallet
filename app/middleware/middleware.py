from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler,
        event: Message,
        data
    ):
        async with self.session_pool() as session:
            
            data['db'] = session w
            
            try:
                resultado = await handler(event, data)
                await session.commit()
                return resultado
                
            except Exception as e:
                await session.rollback()
                print(f"Error en el handler: {e}")
                
                if isinstance(event, Message):
                    await event.answer("Hubo un error interno procesando tu solicitud.")
