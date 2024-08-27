import uuid

from fastapi.openapi.models import Schema
from pydantic import Field, BaseModel, ConfigDict


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., serialization_alias='currencyId', json_schema_extra={'example': 'BRL'})
    name: str = Field(..., json_schema_extra={'example': 'Brazilian Real'})
    symbol: str = Field(..., json_schema_extra={'example': 'R$'})


class TaxSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., json_schema_extra={'example': uuid.uuid4()})
    name: str = Field(..., description='The name of the tax')
    description: str | None = Field(None, description='The description of the tax')
    country_id: str = Field(..., description='The country of the tax')
