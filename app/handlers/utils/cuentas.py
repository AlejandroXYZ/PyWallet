from sqlalchemy import select
from app.db.connection import get_db
from app.models.account import Cuentas


def obtener_cuentas():
    with get_db() as db:
        cuentas = db.execute(select(Cuentas)).scalars().all()
        return cuentas
