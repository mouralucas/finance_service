import uuid
from datetime import date

from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel

from schemas.request.finance import TaxFeeQuote


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
    fees: list[TaxFeeQuote] | None = Field(None, description='The fee details of the fund fees')

    benchmark: str | None = Field(None, description='The benchmark of the fund')
