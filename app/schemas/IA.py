from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class ActionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespaces=True, extras="forbid"
    )
    accion: Literal["CREATE", "UPDATE", "DELETE", "READ"] = Field(max_length=7)


class IAResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespaces=True, extras="forbid"
    )
    monto: Decimal = Field(gt=0, decimal_places=2, max_digits=8)
    etiqueta: str = Field(max_length=20)
    descripcion: str = Field(max_length=60)
    cuenta: str = Field(max_length=20)


class IAResponseDelete(BaseModel):
    id: int = Field(gt=0)
