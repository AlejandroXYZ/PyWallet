from sqlalchemy import select
from app.db.connection import get_db
from app.models.account import Cuentas
import logging


logger = logging.getLogger(name=__name__)


def obtener_cuentas() -> list:
    with get_db() as db:
        cuentas = db.execute(select(Cuentas)).scalars().all()
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
