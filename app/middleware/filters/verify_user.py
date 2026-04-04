from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuarios


async def verificar_usuario(db: AsyncSession, id: int):
    query = db.execute(select(Usuarios).filter(id == Usuarios.telegram_id))
    usuario = query.scalar_one_or_none()
    if not usuario:
        return False
    return True
