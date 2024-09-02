import uuid

from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.investment import InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema


class CreateInvestmentResponse(SuccessResponseBase):
    investment: InvestmentSchema = Field(..., description='The investment created')


class GetInvestmentResponse(SuccessResponseBase):
    quantity: int = Field(..., description='The total number of investment returned')
    investments: list[InvestmentSchema] = Field(..., description='The list of investments')


class LiquidateInvestmentResponse(CreateInvestmentResponse):
    # It implements exactly the same data as CreateInvestment. A new class is created to maintain the pattern every router has its response
    pass


class CreateStatementResponse(SuccessResponseBase):
    investment_statement: InvestmentStatementSchema = Field(..., serialization_alias='investmentStatement', description='The investment statement')


class GetStatementResponse(SuccessResponseBase):
    statement: list[InvestmentStatementSchema] = Field(..., description='The investment statement')


class CreateObjectiveResponse(SuccessResponseBase):
    objective: InvestmentObjectiveSchema = Field(..., description='The investment objective')


class GetInvestmentObjectiveResponse(SuccessResponseBase):
    pass
