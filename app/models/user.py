from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum as EnumType
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, BigInteger
from enum import Enum, unique


class Roles(str, Enum):
    user = "user"
    admin = "admin"


class Usuarios(Base):
    __tablename__ = "Usuarios"
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, unique=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram_id: Mapped[BigInteger] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    alias: Mapped[str] = mapped_column(String(80), nullable=True, unique=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ultima_vez: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    rol: Mapped[Roles] = mapped_column(
        EnumType(Roles, names="roles_enum"), nullable=False, default="user"
    )
