from typing import Any

from pydantic import BaseModel, Field

from schemas.investment_brazilian_fund import InvestmentBrazilianFundSchema, InvestmentBrazilianFundStatementSchema


class CreateBrazilianFundInvestmentResponse(BaseModel):
    fund: InvestmentBrazilianFundSchema = Field(..., description='The investment fund br created')


class CreateInvestmentFundsBrResponse(BaseModel):
    statement: InvestmentBrazilianFundStatementSchema = Field(..., description='The fund investment statement')