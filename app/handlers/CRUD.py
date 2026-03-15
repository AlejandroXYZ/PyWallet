from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.account import Cuentas
from app.models.transaction import Transaction
from decimal import Decimal
import logging

logger = logging.getLogger(name=__name__)


def create(message: dict):
    with get_db() as db:
        logger.info("Verificando existencia de la cuenta")
        cuenta_id = verificar_cuenta(message["cuenta"])
        logger.info("Cuenta Verificada Correctamente")
        if cuenta_id:
            logger.info("Creando transaccion")
            transaccion = Transaction(
                monto=message["monto"],
                etiqueta=message["etiqueta"],
                descripcion=message["descripcion"],
                cuenta=cuenta_id.id,
            )
            logger.info("Sumando monto a la cuenta")
            cuenta_id.saldo = cuenta_id.saldo + Decimal(transaccion.monto)

            db.add(transaccion)
            db.commit()
            db.refresh(transaccion)
            return transaccion.id
        else:
            return False


def verificar_cuenta(cuenta: str):
    with get_db() as db:
        verificacion = db.query(Cuentas).filter(cuenta == Cuentas.nombre).first()

        if not verificacion:
            return False

        return verificacion
