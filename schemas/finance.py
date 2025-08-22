from unittest.mock import Base
import uuid
from datetime import date

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_snake
import datetime

class TaxFeeQuotationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
    ))

    id: uuid.UUID = Field(..., serialization_alias='taxFeeId', description='The identification of the tax/fee')
    percentage: str = Field(..., description='The percentage of the tax/fee')


class FundsBrSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel))

    id: uuid.UUID = Field(..., serialization_alias='fundId', description='The unique identification for the fund')
    name: str = Field(..., description='The name of the fund')
    fund_cnpj: str = Field(..., min_length=14, max_length=18, description='The cnpj of the fund')
    administrator: str = Field(..., description='The administrator of the fund')
    administrator_cnpj: str = Field(..., min_length=14, max_length=18, description='The cnpj of the administrator of the fund')
    status: str | None = Field(None, description='The status of the fund')
    start_date: date = Field(..., description='The day that the fund started')

    minimum_balance: float = Field(..., description='The minimum balance to stay investing in the fund')
    minimum_investment: float = Field(..., description='The minimum amount of each investment')
    minimum_withdraw: float = Field(..., description='The minimum amount to withdraw')
    initial_investment: float = Field(..., description='The initial amount of the investment')

    investment_quotation: str = Field(..., description='The number of days until the quotation after the investment')
    redemption_quotation: str = Field(..., description='The number of days until the quotation after the redemption')
    redemption_settlement: str = Field(..., description='The number of days until the redemption is settled to the investor')

    # TODO: maybe change the TaxFeeQuote for one schema not in request folder
    fees: list[TaxFeeQuotationSchema] | None = Field(None, description='The fee details of the fund fees')

    benchmark: str | None = Field(None, description='The benchmark of the fund')


class IndexerSeries(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(serialization_alias=to_camel)
    )

    id: uuid.UUID = Field(...)
    indexer_id: uuid.UUID = Field(..., description='The internal id of the indexer')
    indexer_name: str | None = Field(None, description='The name of the indexer')
    date: datetime.date | None = Field(None, description='The reference date of the value')
    period: int | None = Field(None, description='The reference period of the value')
    value: float = Field(..., description='The value of the indexer at the date/period')
    periodicity_id: uuid.UUID = Field(..., description='The internal id of periodocity')
    periodocity_name: str | None = Field(None, description='The name of the periodicity')
    unit: str = Field(..., description='The unit of the value')