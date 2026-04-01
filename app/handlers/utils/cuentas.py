from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Cuentas
from app.handlers.utils.dolar import convertidor
import logging


logger = logging.getLogger(name=__name__)


async def obtener_cuentas(db: AsyncSession) -> list | bool:
    query = await db.scalars(select(Cuentas).where(Cuentas.activa))
    cuentas = query.all()
    if cuentas:
        return cuentas
    else:
        return False


async def obtener_cuenta_especifica(id: int, db: AsyncSession) -> dict:
    cuenta = await db.execute(
        select(Cuentas).filter(id == Cuentas.id and Cuentas.activa)
    )
    cuenta = cuenta.scalar_one_or_none()

    if not cuenta:
        logger.error("La cuenta no fue encontrada por su ID")
        return {"status": False, "mensaje": "Cuenta no encontrada"}

    return {"status": True, "mensaje": "Cuenta encontrada", "cuenta": cuenta}


async def obtener_total(db: AsyncSession):
    query = select(
        Cuentas.moneda, func.sum(Cuentas.saldo).label("saldo_total")
    ).group_by(Cuentas.moneda)

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
