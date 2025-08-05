import uuid
from datetime import date
from decimal import Decimal

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from schemas.request.investment import CreateInvestmentBaseRequest, CreateInvestmentStatementBaseRequest


class CreateBrazilianFundInvestmentRequest(CreateInvestmentBaseRequest):
    fund_id: uuid.UUID = Field(..., description='The identification of the fund')

    investment_quotation_date: date = Field(..., description='The day that the investment was quoted')
    investment_settlement_date: date = Field(..., description='The date the investment was liquidated in the fund')
    redemption_quotation_date: date | None = Field(None, description='The day that the redemption was quoted')
    redemption_settlement_date: date | None = Field(None, description='The day that the amount was settled')


class CreateBrazilianFundInvestmentStatementRequest(CreateInvestmentStatementBaseRequest):
    fund_id: uuid.UUID = Field(..., description='The unique identification of the fund')
    # contribution: float = Field(..., description='The amount of money contributed to the fund in the period')
    price: Decimal = Field(..., description='The price of the fund in the reference day')
    penalty: Decimal | None = Field(Decimal('0'), description='The penalty applied to the investment in the period')


class GetBrazilianFundInvestmentStatementRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    fund_id: uuid.UUID = Field(..., description='The unique identification of the fund')
    start_period: int | None = Field(None, description='The start period of the statement')
    end_period: int | None = Field(None, description='The end period of the statement')
    period: int | None = Field(None, description='The period of the statement')

    @model_validator(mode='after')
    def check_periods(self):
        if self.period and (self.start_period or self.end_period):
            raise ValueError('only specific period or a range is allowed')

        if self.start_period and self.end_period and (self.end_period < self.start_period):
            raise ValueError('start period must be before end period')

        return self
