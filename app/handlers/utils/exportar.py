import io
import csv
from app.db.connection import get_db
from sqlalchemy import select
from app.models.transaction import Transaction
from app.models.account import Cuentas


async def generar_csv():
    async with get_db() as db:
        objeto_ram = io.StringIO()
        escritor = csv.writer(objeto_ram)

        escritor.writerow(
            [
                "ID",
                "Monto",
                "Etiqueta",
                "Descripcion",
                "Tipo",
                "fecha",
                "Cuenta",
                "Moneda",
            ]
        )

        query = (
            select(
                Transaction.id,
                Transaction.monto,
                Transaction.etiqueta,
                Transaction.descripcion,
                Transaction.tipo,
                Transaction.fecha,
                Cuentas.nombre.label("Nombre_cuenta"),
                Cuentas.moneda.label("Moneda"),
            )
            .join(Transaction.cuenta_name)
            .where(Transaction.activa)
            .order_by(Transaction.fecha.desc())
        )

        resultados = await db.execute(query)
        rows = resultados.fetchall()
        escritor.writerows(rows)

        return objeto_ram.getvalue().encode("utf-8")
