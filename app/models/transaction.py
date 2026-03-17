from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.db import base
import datetime
from sqlalchemy import DateTime


class Transaction(base.Base):
    __tablename__ = "Transacciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    monto: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), nullable=False, default="0.00"
    )
    etiqueta: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(13))
    cuenta: Mapped[int] = mapped_column(ForeignKey("Cuentas.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @validates("fecha")
    def validar_formato_fecha(self, clave, valor):

        if isinstance(valor, datetime.datetime):
            return valor

        if isinstance(valor, str):
            try:
                fecha = datetime.datetime.strptime(valor, "%d/%m/%Y %H:%M")
                return fecha
            except ValueError:
                raise ValueError(f"La fecha '{valor}' no tiene el formato correcto")
        raise TypeError("La fecha deb ser un string o un objeto datetime")
