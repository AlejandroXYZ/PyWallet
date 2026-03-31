from sqlalchemy import String, ForeignKey, BigInteger, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from decimal import Decimal


class Cuentas(Base):
    __tablename__ = "Cuentas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    saldo: Mapped[Decimal] = mapped_column(Numeric(8, 2), default="0.00")
    moneda: Mapped[str] = mapped_column(String(4), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    transacciones: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="cuenta_name"
    )
    propietario: Mapped[BigInteger] = mapped_column(
        ForeignKey("Usuarios.id"), nullable=False
    )
