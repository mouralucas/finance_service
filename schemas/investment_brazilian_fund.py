import uuid
from datetime import date

from pydantic import Field

from schemas.finance import FundsBrSchema
from schemas.investment import InvestmentBaseSchema, InvestmentStatementBase


class InvestmentBrazilianFundSchema(InvestmentBaseSchema):
    fund_id: uuid.UUID = Field(..., description="The identification of the fund")
    fund: FundsBrSchema = Field(..., exclude=True)
    fund_name: str | None = Field(None, description="The name of the fund")

    investment_quotation_date: date = Field(
        ..., description="The date the investment was quoted"
    )
    investment_settlement_date: date = Field(
        ..., description="The date the investment was liquidated in the fund"
    )
    redemption_quotation_date: date | None = Field(
        None, description="The date that the redemption was quoted"
    )
    redemption_settlement_date: date | None = Field(
        None, description="The date that the redemption was settled"
    )

    def transform(self):
        self.fund_name = self.fund.name

        return self


class InvestmentBrazilianFundStatementSchema(InvestmentStatementBase):
    fund_id: uuid.UUID = Field(..., description="The unique identification of the fund")
    contribution: float = Field(
        ..., description="The amount of money contributed to the fund in the period"
    )
    price: float = Field(..., description="The price of the fund in the reference day")
    penalty: float = Field(
        ..., description="The penalty applied to the investment in the period"
    )
