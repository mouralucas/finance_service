import uuid
from datetime import date
from decimal import Decimal

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GetCurrencyCostAverage(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))


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


class TaxFeeQuotationRequest(BaseModel):
    """
    Created by: Lucas Penha de Moura - 19/03/2025
        This model define the request for the tax/fee quotation details for the investment.
        Which tax/fee are applied to the investment and the percentage of each one.
    """
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    id: uuid.UUID = Field(..., alias='taxFeeId', description='The identification of the tax/fee')
    percentage: str = Field(..., description='The percentage of the tax/fee')


class CreateBrazilianFundRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

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

    fees: list[TaxFeeQuotationRequest] | None = Field(None, description='The fee details of the fund fees')

    benchmark: str | None = Field(None, description='The benchmark of the fund')
