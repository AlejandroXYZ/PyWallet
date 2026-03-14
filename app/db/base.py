from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Convención para nombres automáticos de índices y constraints
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",  #index
    "uq": "uq_%(table_name)s_%(column_0_name)s",   #unic
    "ck": "ck_%(table_name)s_%(constraint_name)s",  #check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", #foraignkey 
    "pk": "pk_%(table_name)s"  # llave primaria
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
