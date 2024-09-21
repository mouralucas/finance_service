import uuid

from fastapi.openapi.models import Schema
from pydantic import Field, BaseModel, ConfigDict


class BankSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='bankId', description='The unique id og the bank')
    name: str = Field(..., description='The name of the bank')


class CountrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description='The unique id of the country')
    name: str = Field(..., description='The name of the country')


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., serialization_alias='currencyId', json_schema_extra={'example': 'BRL'})
    name: str = Field(..., json_schema_extra={'example': 'Brazilian Real'})
    symbol: str = Field(..., json_schema_extra={'example': 'R$'})


class TaxSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='taxId', json_schema_extra={'example': uuid.uuid4()})
    name: str = Field(..., description='The name of the tax')
    description: str | None = Field(None, description='The description of the tax')
    country_id: str = Field(..., serialization_alias='countryId', description='The country of the tax')


class IndexerTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='indexerTypeId', description='The unique id of the index type')
    name: str = Field(..., description='The name of the index type')
    description: str | None = Field(None, description='The description of the index type')


class IndexerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(serialization_alias='indexerId', description=' The unique identification of the index', json_schema_extra={'example': uuid.uuid4()})
    name: str = Field(..., description='The name of the index')
    description: str | None = Field(None, description='The description of the index')


class LiquiditySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='liquidityId', description='The unique id of the liquidity')
    name: str = Field(..., description='The name of the liquidity')
    description: str | None = Field(None, description='The description of the liquidity')


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='categoryId', description='The unique id of the category')
    name: str = Field(..., description='The name of the category')
    comment: str | None = Field(None, description='The description of the category')
    order: int | None = Field(None, description='The order of the category')
