from sqlalchemy import select, func
from app.db.connection import get_db
from app.models.account import Cuentas
from app.handlers.utils.dolar import convertidor
from decimal import Decimal
import logging


logger = logging.getLogger(name=__name__)


async def obtener_cuentas() -> list | bool:
    async with get_db() as db:
        query = await db.execute(select(Cuentas).where(Cuentas.activa))
        cuentas = query.scalars().all()
        if cuentas:
            return cuentas
        else:
            return False


async def obtener_cuenta_especifica(id: int) -> dict:
    async with get_db() as db:
        cuenta = await db.execute(
            select(Cuentas).filter(id == Cuentas.id and Cuentas.activa)
        ).scalar_one_or_none()

        if not cuenta:
            logger.error("La cuenta no fue encontrada por su ID")
            return {"status": False, "mensaje": "Cuenta no encontrada"}

        return {"status": True, "mensaje": "Cuenta encontrada", "cuenta": cuenta}


async def obtener_total():
    async with get_db() as db:
        query = select(
            Cuentas.moneda, func.sum(Cuentas.saldo).label("saldo_total")
        ).group_by(Cuentas.moneda)

        resultado = await db.execute(query)
        query = resultado.all()

        texto = ""
        suma = {}
        for moneda, total in query:
            conversion = convertidor(moneda=moneda, saldo=total)
            if conversion["status"]:
                total = f"Total en {moneda}: {total}\nEquivalente a {conversion['moneda']}: {conversion['saldo']}\n\n"
                texto += total

            else:
                return False
        return {"por_moneda": texto, "patrimonio": suma}
