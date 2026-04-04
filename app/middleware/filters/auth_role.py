import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuarios
from app.models.user import Roles


logger = logging.getLogger(__name__)


class AuthRole(BaseFilter):
    """Clase Filtro para autenticar si el mensaje recibido es de un usuario de rol Client o Admin"""

    async def __call__(self, db: AsyncSession, message: Message) -> bool:
        try:
            query = select(Usuarios).filter(
                message.from_user.id == Usuarios.id,
                Usuarios.rol == Roles.admin,
            )
            resultado = await db.execute(query)

            if not resultado:
                logger.error("No Hubieron resultados")
                return False
            user = resultado.scalar_one_or_none()
            logger.info(f"Usuario {user.nombre} es Admin")
            return True

        except Exception as e:
            raise e
