import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel


class GetSummaryRequest(BaseModel):
    period: int | None = Field(None, description='The period of the summary')


class GetTaxFeeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    country_id: str = Field('BR', description='The id of the country for the tax or fee')
    type: str = Field(..., description='Whether is tax or fee to fetch')


class TaxFeeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    id: uuid.UUID = Field(..., alias='taxFeeId', description='The identification of the tax/fee')
    amount: Decimal = Field(..., description='The amount of the tax/fee')
    currency_id: str = Field('BRL', alias='currencyId', description='The currency of the tax/fee')
