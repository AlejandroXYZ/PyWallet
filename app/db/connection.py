from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.models.account import Cuentas
from app.models.transaction import Transaction
from app.models.user import Usuarios
from app.models.users_allow import UsuariosPermitidos
import os


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=1800, pool_timeout=8
)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
