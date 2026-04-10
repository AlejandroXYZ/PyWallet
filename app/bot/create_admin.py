from app.models.users_allow import UsuariosPermitidos
from app.models.user import Usuarios
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
from app.db.connection import AsyncSession
from datetime import datetime

logger = logging.getLogger(__name__)


async def crear_usuario_admin():
    async with AsyncSession() as db:
        try:
            id_admin = os.getenv("ADMIN_ID", None)
            if not id_admin:
                logger.error("No hay Usuario admin en las variables de entorno")
                raise Exception

            admin_permitido = UsuariosPermitidos(nombre="ADMIN", telegram_id=id_admin)

            db.add(admin_permitido)
            await db.flush()
            await db.refresh(admin_permitido)

            fecha = datetime.now()
            admin_usuario = Usuarios(
                alias="@admin",
                fecha_registro=fecha,
                ultima_vez=fecha,
                rol="admin",
                id_permitido=id_admin,
            )

            db.add(admin_usuario)
            db.flush()
            db.refresh(admin_usuario)

            await db.commit()
        except Exception as e:
            logger.error("Ha ocurrido un error mientras se creaba el usuario admin")
            raise e
