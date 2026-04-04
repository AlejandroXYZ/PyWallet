from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UsuariosPermitidos(Base):
    __tablename__ = "Usuarios_Permitidos"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[BigInteger] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    usuarios: Mapped["Usuarios"] = relationship("Usuarios", back_populates="allow")
