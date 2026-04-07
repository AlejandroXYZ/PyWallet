from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Cuentas
from app.handlers.utils.dolar import convertidor
import logging
from app.models.user import Usuarios


logger = logging.getLogger(name=__name__)


async def obtener_cuentas(db: AsyncSession, id: int) -> list | bool:
    try:
        logger.info(f"Obteniendo Cuentas de Usuario {id}")
        query = await db.execute(
            select(Cuentas)
            .join(Usuarios)
            .where(Cuentas.activa, Usuarios.id_permitido == id)
        )
        cuentas = query.scalars().all()
        logger.info(f"Cuentas del usuario {id}:\n{cuentas}\n")
        if cuentas:
            return cuentas
        else:
            return False
    except Exception as e:
        raise e


async def obtener_cuenta_especifica(id: int, db: AsyncSession) -> dict:
    cuenta = await db.execute(select(Cuentas).filter(id == Cuentas.id, Cuentas.activa))
    cuenta = cuenta.scalar_one_or_none()

    if not cuenta:
        logger.error("La cuenta no fue encontrada por su ID")
        return {"status": False, "mensaje": "Cuenta no encontrada"}

    return {"status": True, "mensaje": "Cuenta encontrada", "cuenta": cuenta}


async def obtener_total(db: AsyncSession, telegram_id: int):

    query = (
        select(Cuentas.moneda, func.sum(Cuentas.saldo).label("saldo_total"))
        .join(Usuarios)
        .where(Usuarios.id_permitido == telegram_id)
        .group_by(Cuentas.moneda)
    )
    resultado = await db.execute(query)
    query = resultado.all()

    texto = ""
    suma = {}
    for moneda, total in query:
        conversion = await convertidor(moneda=moneda, saldo=total)
        if conversion["status"]:
            total = f"Total en {moneda}: {total}\nEquivalente a {conversion['moneda']}: {conversion['saldo']}\n\n"
            texto += total

        else:
            return False
    return {"por_moneda": texto, "patrimonio": suma}
