import io
import csv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.models.account import Cuentas
from app.models.user import Usuarios


async def generar_csv(db: AsyncSession, telegram_id: int):

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
        .join(Cuentas, Transaction.cuenta == Cuentas.id)
        .join(Usuarios, Cuentas.propietario == Usuarios.id)
        .where(Transaction.activa, Usuarios.id_permitido == telegram_id)
        .order_by(Transaction.fecha.desc())
    )

    resultados = await db.execute(query)
    rows = resultados.fetchall()
    escritor.writerows(rows)

    return objeto_ram.getvalue().encode("utf-8")
