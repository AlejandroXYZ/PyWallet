from sqlalchemy import select, func
from app.db.connection import get_db
from app.models.account import Cuentas
from app.handlers.utils.dolar import convertidor
from decimal import Decimal
import logging


logger = logging.getLogger(name=__name__)


def obtener_cuentas() -> list | bool:
    with get_db() as db:
        cuentas = db.execute(select(Cuentas).where(Cuentas.activa)).scalars().all()
        if cuentas:
            return cuentas
        else:
            return False


def obtener_cuenta_especifica(id: int) -> dict:
    with get_db() as db:
        cuenta = db.query(Cuentas).where(id == Cuentas.id and Cuentas.activa).first()

        if not cuenta:
            logger.error("La cuenta no fue encontrada por su ID")
            return {"status": False, "mensaje": "Cuenta no encontrada"}

        return {"status": True, "mensaje": "Cuenta encontrada", "cuenta": cuenta}


def obtener_total():
    with get_db() as db:
        query = (
            db.query(Cuentas.moneda, func.sum(Cuentas.saldo).label("Saldo Total"))
            .group_by(Cuentas.moneda)
            .all()
        )

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
