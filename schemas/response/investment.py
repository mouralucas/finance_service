from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.investment import InvestmentSchema


class CreateInvestmentResponse(SuccessResponseBase):
    investment: InvestmentSchema = Field(..., description='The investment created')


class GetInvestmentResponse(SuccessResponseBase):
    quantity: int = Field(..., description='The total number of investment returned')
    investments: list[InvestmentSchema] = Field(..., description='The list of investments')
