from typing import Any

from pydantic import Field, BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel
from rolf_common.schemas import SuccessResponseBase

from schemas.core import ChartSeriesSchema
from schemas.investment import InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema, InvestmentTypeSchema, InvestmentAllocationSchema, InvestmentPerformanceDataSchema


class CreateInvestmentResponse(SuccessResponseBase):
    investment: InvestmentSchema = Field(..., description='The investment created')


class UpdateInvestmentResponse(CreateInvestmentResponse):
    pass


class GetInvestmentResponse(SuccessResponseBase):
    quantity: int = Field(..., description='The total number of investment returned')
    investments: list[InvestmentSchema] = Field(..., description='The list of investments')


class GetInvestmentTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    quantity: int = Field(..., description='The number of types returned')
    investment_types: list[InvestmentTypeSchema] = Field(..., description='The list of investment types')


class LiquidateInvestmentResponse(CreateInvestmentResponse):
    # It implements exactly the same data as CreateInvestment. A new class is created to maintain the pattern every router has its response
    pass


class CreateStatementResponse(SuccessResponseBase):
    investment_statement: InvestmentStatementSchema = Field(..., serialization_alias='investmentStatement', description='The investment statement')


class GetStatementResponse(SuccessResponseBase):
    statement: list[InvestmentStatementSchema] | None = Field(None, description='The investment statement')


class CreateObjectiveResponse(SuccessResponseBase):
    objective: InvestmentObjectiveSchema = Field(..., description='The investment objective')


class GetObjectiveResponse(SuccessResponseBase):
    objectives: list[InvestmentObjectiveSchema] = Field(..., description='The list of investment objectives')


class GetInvestmentWithoutObjectives(GetInvestmentResponse):
    pass


class GetObjectiveSummaryResponse(SuccessResponseBase):
    objective_title: str = Field(..., serialization_alias='objectiveTitle', description='The title of the objective')
    amount_stipulated: float = Field(..., serialization_alias='amountStipulated', description='The amount stipulated when objective was created')
    amount_invested: float = Field(..., serialization_alias='amountInvested', description='The amount invested so far in this objective')
    perc_completed: float = Field(..., serialization_alias='percCompleted', description='The percentage completed of the objective')


# Dashboard information
class GetInvestmentAllocationResponse(SuccessResponseBase):
    type_allocation: list[InvestmentAllocationSchema] | list = Field([], serialization_alias='typeAllocation', description='The list of investment allocated by type')
    category_allocation: list[InvestmentAllocationSchema] | list = Field([], serialization_alias='categoryAllocation', description='The list of investment allocated by category')


class GetInvestmentPerformanceResponse(SuccessResponseBase):
    data: list[InvestmentPerformanceDataSchema] = Field(..., description='The investment performance data')
    series: list[ChartSeriesSchema] = Field(..., description='The performance series')
