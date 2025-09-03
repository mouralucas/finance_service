from pydantic import BaseModel, Field

from schemas.investment_brazilian_fund import (
    InvestmentBrazilianFundSchema,
    InvestmentBrazilianFundStatementSchema,
)


class CreateBrazilianFundInvestmentResponse(BaseModel):
    fund: InvestmentBrazilianFundSchema = Field(
        ..., description="The investment fund br created"
    )


class GetBrazilianFundInvestmentsResponse(BaseModel):
    quantity: int = Field(
        ..., description="The quantity of brazilian fund investments available"
    )
    investments: list[InvestmentBrazilianFundSchema] = Field(
        ..., description="The list of brazilian fund investments"
    )


class CreateBrazilianFundInvestmentStatementResponse(BaseModel):
    statement: InvestmentBrazilianFundStatementSchema = Field(
        ..., description="The fund investment statement"
    )


class GetBrazilianFundInvestmentStatementResponse(BaseModel):
    quantity: int = Field(
        ..., description="The quantity of brazilian fund investment statements"
    )
    statements: list[InvestmentBrazilianFundStatementSchema] = Field(
        ..., description="The list of statement"
    )
