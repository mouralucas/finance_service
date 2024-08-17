from fastapi.openapi.models import Schema
from pydantic import Field, BaseModel, ConfigDict


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., serialization_alias='currencyId', example='BRL')
    name: str = Field(..., example='Real')
    symbol: str = Field(..., example='R$')
