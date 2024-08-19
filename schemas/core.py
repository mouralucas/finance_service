from fastapi.openapi.models import Schema
from pydantic import Field, BaseModel, ConfigDict


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., serialization_alias='currencyId', json_schema_extra={'example': 'BRL'})
    name: str = Field(..., json_schema_extra={'example': 'Brazilian Real'})
    symbol: str = Field(..., json_schema_extra={'example': 'R$'})
