from app.db.connection import get_db
from app.models.account import Cuentas
from app.models.transaction import Transaction
from decimal import Decimal
import logging
from app.handlers.utils.cuentas import obtener_cuentas

logger = logging.getLogger(name=__name__)


def create(message: dict):
    with get_db() as db:
        logger.info("Verificando existencia de la cuenta")

        cuenta_id = (
            db.query(Cuentas).filter(message["cuenta"] == Cuentas.nombre).first()
        )

        if not cuenta_id:
            return False

        logger.info("Cuenta Verificada Correctamente")
        logger.info("Creando transaccion")
        transaccion = Transaction(
            monto=message["monto"],
            etiqueta=message["etiqueta"],
            descripcion=message["descripcion"],
            cuenta=cuenta_id.id,
            fecha=message["fecha"],
            tipo=message["tipo"],
        )
        match message["tipo"]:
            case "ingreso":
                logger.info("Sumando monto a la cuenta")
                cuenta_id.saldo = cuenta_id.saldo + Decimal(transaccion.monto)
            case "gasto":
                logger.info("Restando monto de la cuenta")
                cuenta_id.saldo = cuenta_id.saldo - Decimal(transaccion.monto)
            case "transferencia":
                pass
            case _:
                logger.error("Tipo de transacción no válido")
                return False

        db.add(transaccion)
        db.commit()
        db.refresh(transaccion)
        db.refresh(cuenta_id)
        return [transaccion.id, cuenta_id.saldo, cuenta_id.nombre]


def delete(message: dict) -> dict:
    r"""Función de Borrado, no borra la transacción solo cambia entre un estado activa o desactiva ocultando su existencia"""
    with get_db() as db:
        logger.info("Verificando ID de la transaccion en la DB")
        transaccion_existente = (
            db.query(Transaction).filter(Transaction.id == message["id"]).first()
        )
        if not transaccion_existente:
            logger.error("El ID de la transaccion no existe")
            return {"status": False, "mensaje": "El ID de la transacción no existe"}

        logger.info("Buscando Cuenta de la transaccion")
        cuenta = (
            db.query(Cuentas).filter(Cuentas.id == transaccion_existente.cuenta).first()
        )
        logger.info(f"Cuenta Encontrada: {cuenta.nombre}")

        if transaccion_existente.activa:
            logger.info("Transaccion Activa, Eliminando...")
            transaccion_existente.activa = False
            cuenta.saldo = cuenta.saldo - transaccion_existente.monto
            db.commit()
            db.refresh(transaccion_existente)
            db.refresh(cuenta)
            logger.info("Hecho")
            return {
                "status": True,
                "mensaje": f"Transaccion eliminada correctamente de la cuenta {cuenta.nombre}",
            }

        elif not transaccion_existente.activa:
            logger.info("Transacción ya Eliminada")
            return {"status": False, "mensaje": "Error, la transacción ya no existe"}

        else:
            logger.error(
                "Error en la base de datos, la transaccion no se encuentra ni activa ni desactiva"
            )
            return {
                "status": False,
                "mensaje": "Error en la base de datos, la transaccion no se encuentra activa ni desactiva",
            }


def new_account(message: dict) -> dict:
    """Función para crear cuentas nuevas a través del comando /accounts"""

    with get_db() as db:
        cuentas = obtener_cuentas()
        logger.info(cuentas)
        if cuentas:
            for i in cuentas:
                if message["nombre"] == i.nombre:
                    return {
                        "status": False,
                        "mensaje": f"Ya Tienes una cuenta con el nombre: {message['nombre']}",
                    }

        new = Cuentas(nombre=message["nombre"], moneda=message["moneda"])
        db.add(new)
        db.commit()
        db.refresh(new)
        return {
            "status": True,
            "mensaje": f"Cuenta {new.nombre} creada correctamente, ID: {new.id}",
        }


def delete_account(id: int) -> dict:
    with get_db() as db:
        cuenta_existente = db.query(Cuentas).where(Cuentas.id == id).first()

        if not cuenta_existente:
            return {"status": False, "mensaje": "Error, la Cuenta no existe"}

        cuenta_existente.activa = False
        db.commit()
        db.refresh(cuenta_existente)
        return {
            "status": True,
            "cuenta": cuenta_existente,
            "mensaje": f"Eliminada la cuenta {cuenta_existente.nombre} con Éxito",
        }
