from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Cuentas
from app.models.transaction import Transaction
from decimal import Decimal
import logging
from app.handlers.utils.cuentas import obtener_cuentas
from app.models.user import Usuarios

logger = logging.getLogger(name=__name__)


async def create(message: dict, db: AsyncSession, id: int):
    logger.info("Verificando existencia de la cuenta")

    query = (
        select(Cuentas)
        .join(Usuarios)
        .filter(
            message["cuenta"] == Cuentas.nombre,
            Usuarios.id_permitido == id,
            Cuentas.activa,
        )
    )
    busqueda_cuenta = await db.execute(query)
    logger.info(busqueda_cuenta)
    cuenta_id = busqueda_cuenta.scalar_one_or_none()

    if not cuenta_id:
        return {
            "status": False,
            mensaje: "Error no se encontró la cuenta, verifica que esa cuenta existe o crea una",
        }

    if int(message["monto"]) > cuenta_id.saldo:
        return {
            "status": False,
            "mensaje": f"No te alcanza el dinero, el saldo de tu cuenta es: {cuenta_id.saldo}",
        }
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
    await db.flush()
    await db.refresh(transaccion)
    await db.refresh(cuenta_id)
    return {
        "id": transaccion.id,
        "saldo": cuenta_id.saldo,
        "nombre": cuenta_id.nombre,
        "status": True,
    }


async def delete(message: dict, db: AsyncSession) -> dict:
    r"""Función de Borrado, no borra la transacción solo cambia entre un estado activa o desactiva ocultando su existencia"""
    logger.info("Verificando ID de la transaccion en la DB")
    query = select(Transaction).filter(Transaction.id == message["id"])
    resultado = await db.execute(query)
    transaccion_existente = resultado.scalar_one_or_none()
    if not transaccion_existente:
        logger.error("El ID de la transaccion no existe")
        return {"status": False, "mensaje": "El ID de la transacción no existe"}

    logger.info("Buscando Cuenta de la transaccion")
    query = select(Cuentas).filter(Cuentas.id == transaccion_existente.cuenta)
    resultado = await db.execute(query)
    cuenta = resultado.scalar_one_or_none()
    logger.info(f"Cuenta Encontrada: {cuenta.nombre}")
    if transaccion_existente.activa:
        logger.info("Transaccion Activa, Eliminando...")
        transaccion_existente.activa = False
        cuenta.saldo = cuenta.saldo - transaccion_existente.monto
        await db.refresh(transaccion_existente)
        await db.refresh(cuenta)
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


async def new_account(message: dict, registrados: dict, db: AsyncSession) -> dict:
    try:
        """Función para crear cuentas nuevas a través del comando /accounts"""
        logger.info("Creando Cuenta")
        cuentas = await obtener_cuentas(db, message["telegram_id"])
        if cuentas:
            for i in cuentas:
                if message["nombre"] == i.nombre:
                    return {
                        "status": False,
                        "mensaje": f"Ya Tienes una cuenta con el nombre: {message['nombre']}",
                    }

        usuario_id = next(
            (i for i in registrados if i == message["telegram_id"]),
            None,
        )
        if not usuario_id:
            return {"status": False, "mensaje": "No se encontró el ID del usuario"}
        query_usuario = await db.execute(
            select(Usuarios.id).where(Usuarios.id_permitido == usuario_id)
        )
        id = query_usuario.scalar()
        new = Cuentas(
            nombre=message["nombre"],
            moneda=message["moneda"],
            propietario=int(id),
        )
        db.add(new)
        await db.flush()
        await db.refresh(new)
        return {
            "status": True,
            "mensaje": f"Cuenta {new.nombre} creada correctamente, ID: {new.id}",
        }
    except Exception as e:
        logger.error(f"Ha ocurrido un error:\n\n{e}\n\n")
        await db.rollback()
        return {
            "status": False,
            "mensaje": "Lo sentimos ha ocurrido un error interno, ya el admin fue notificado",
        }


async def delete_account(id: int, db: AsyncSession) -> dict:

    query = select(Cuentas).join(Usuarios).filter(Cuentas.id == id)
    resultado = await db.execute(query)
    cuenta_existente = resultado.scalar_one_or_none()

    if not cuenta_existente:
        return {"status": False, "mensaje": "Error, la Cuenta no existe"}

    cuenta_existente.activa = False
    await db.commit()
    return {
        "status": True,
        "cuenta": cuenta_existente,
        "mensaje": f"Eliminada la cuenta {cuenta_existente.nombre} con Éxito",
    }
