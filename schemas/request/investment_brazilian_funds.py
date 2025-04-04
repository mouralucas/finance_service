import uuid
from datetime import date
from decimal import Decimal

from pydantic import Field

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