from pydantic import BaseModel, Field

from schemas.investment_brazilian_fund import InvestmentBrazilianFundSchema, InvestmentBrazilianFundStatementSchema


class CreateBrazilianFundInvestmentResponse(BaseModel):
    fund: InvestmentBrazilianFundSchema = Field(..., description='The investment fund br created')


class CreateBrazilianFundInvestmentStatementResponse(BaseModel):
    statement: InvestmentBrazilianFundStatementSchema = Field(..., description='The fund investment statement')


class GetBrazilianFundInvestmentStatementResponse(BaseModel):
    quantity: int = Field(..., description='The quantity of the fund investment statements')
    statements: list[InvestmentBrazilianFundStatementSchema] = Field(..., description='The list of statement')