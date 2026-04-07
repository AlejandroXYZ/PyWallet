import logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.connection import SessionLocal
from app.models import user
from app.models.users_allow import UsuariosPermitidos
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuarios


logger = logging.getLogger(__name__)


class AuthUser(BaseMiddleware):
    def __init__(self):
        self.ALLOW_USERS: dict = {}
        self.REGISTERED_USERS: set = set()

    async def verificar_usuario(self, db: AsyncSession, id: int):
        logger.info(f"Verificando si el usuario de id: {id} tiene una cuenta")
        query = (
            select(Usuarios)
            .join(Usuarios.allow)
            .options(joinedload(Usuarios.allow))
            .where(id == UsuariosPermitidos.telegram_id)
        )
        resultado = await db.execute(query)
        usuario = resultado.scalar_one_or_none()
        if not usuario:
            logger.info(f"Usuario {id} no tiene cuenta")
            return False
        logger.info(
            f"El usuario {id} tiene una cuenta de nombre: {usuario.allow.nombre}"
        )
        return True

    async def cargar_usuarios_permitidos(self):
        async with SessionLocal() as db:
            query = await db.execute(
                select(
                    UsuariosPermitidos.telegram_id,
                    UsuariosPermitidos.nombre,
                )
            )
            self.ALLOW_USERS = dict(query.all())
            query = await db.execute(select(Usuarios.id_permitido))
            users = set(query.scalars().all())
            self.REGISTERED_USERS.update(users)

    async def __call__(self, handler, message: Message, data):
        data["registrados"] = self.REGISTERED_USERS
        data["permitidos"] = self.ALLOW_USERS
        if message.from_user.id not in self.ALLOW_USERS:
            logger.info(f"El Usuario de id {message.from_user.id} no está autorizado")
            await message.answer("Acceso No Autorizado")
            return

        if message.from_user.id in self.REGISTERED_USERS:
            logger.info(
                f"Usuario {message.from_user.id} se encuentra registrado con el nombre: {self.ALLOW_USERS[message.from_user.id]}"
            )
            return await handler(message, data)
        else:
            if message.text == "/iniciar":
                return await handler(message, data)
            else:
                logger.info(
                    f"Usuario {message.from_user.id} no se encuentra registrado"
                )
                logger.info("Creando una Cuenta")
                await message.answer(
                    "Por favor escribe '/iniciar' para empezar a usar el bot'"
                )
