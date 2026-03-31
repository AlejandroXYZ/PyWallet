from app.models.account import Cuentas
from app.models.transaction import Transaction
from app.db.connection import get_db
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import select
import logging

logger = logging.getLogger(name=__name__)


async def obtener_transacciones(data):
    async with get_db() as db:
        query = select(Cuentas).filter(data["cuenta"] == Cuentas.id)
        resultado = await db.execute(query)
        cuenta_id = resultado.scalar_one_or_none()

        if not cuenta_id:
            return {"status": False, "mensaje": "Error: La cuenta no existe"}

        fecha_actual = datetime.now()
        inicio_del_dia = fecha_actual.replace(hour=0, minute=0, second=0, microsecond=0)

        match data["fecha"]:
            case "hoy":
                data["fecha"] = inicio_del_dia

            case "ayer":
                ayer = timedelta(days=1)
                data["fecha"] = inicio_del_dia - ayer
            case "semana":
                semana = timedelta(weeks=1)
                data["fecha"] = inicio_del_dia - semana

            case "Mes":
                mes = relativedelta(months=1)
                data["fecha"] = inicio_del_dia - mes

            case "6 meses":
                meses = relativedelta(months=6)
                data["fecha"] = inicio_del_dia - meses

            case _:
                return {
                    "status": False,
                    "mensaje": f"Callback de fecha no válido, callback pasado: {data['fecha']}",
                }

        query = (
            select(Transaction)
            .where(
                Transaction.cuenta == cuenta_id.id,
                Transaction.fecha >= data["fecha"],
                Transaction.activa,
            )
            .order_by(Transaction.fecha.desc())
            .limit(int(data["cantidad"]))
        )
        resultado = await db.scalars(query)
        registros = resultado.all()
        if not registros:
            return {"status": False, "mensaje": "No hay registros de Transacciones"}

        respuesta = "📋 <b>Resultados:</b>\n\n"
        for i in registros:
            respuesta += f"<b>ID:</b>{i.id}  |  <b>Descripción:</b> {i.descripcion}  |  <b>Etiqueta:</b> {i.etiqueta}  | <b>Tipo:</b>  {i.tipo}  | <b>Monto:</b> {i.monto}  |  <b>Fecha:</b> {i.fecha.strftime('%d/%m/%Y %H:%M')}\n\n"
        return {"status": True, "registros": respuesta}
