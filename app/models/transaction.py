from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import base, mixins


class Transaction(base.Base, mixins.TimestampMixin):
    __tablename__ = "Transacciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    monto: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), nullable=False, default="0.00"
    )
    etiqueta: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(100))
    cuenta: Mapped[int] = mapped_column(ForeignKey("Cuentas.id"), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
