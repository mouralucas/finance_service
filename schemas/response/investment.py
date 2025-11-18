import uuid
from datetime import date

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from schemas.core import ChartSeriesSchema, ChartSeriesSchemaV2
from schemas.investment_deprecated import (
    InvestmentAllocationSchema,
    InvestmentObjectiveSchema,
    InvestmentPerformanceDataSchema,
    InvestmentSchema,
    InvestmentStatementSchema,
    InvestmentTypeSchema,
)


# Investment Schemas
class CreateInvestmentResponse(BaseModel):
    investment: InvestmentSchema = Field(..., description="The investment created")


class UpdateInvestmentResponse(CreateInvestmentResponse):
    pass


class GetInvestmentResponse(BaseModel):
    quantity: int = Field(..., description="The total number of investment returned")
    investments: list[InvestmentSchema] = Field(
        ..., description="The list of investments"
    )


class GetInvestmentTypeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    quantity: int = Field(..., description="The number of types returned")
    investment_types: list[InvestmentTypeSchema] = Field(
        ..., description="The list of investment types"
    )


class SettleInvestmentResponse(CreateInvestmentResponse):
    # It implements exactly the same data as CreateInvestment.
    # A new class is created to maintain the pattern every router has its response
    pass


# Statement Schemas
class CreateStatementResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    created: bool = Field(..., description="Indicates if the statement was created")
    statement_id: uuid.UUID = Field(..., description="The ID of the created statement")


class UpdateStatementResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    updated: bool = Field(..., description="Indicates if the statement was created")
    statement_id: uuid.UUID | None = Field(
        ..., description="The ID of the created statement"
    )


class GetStatementByIdResponse(BaseModel):
    """
    Get only one statement
    """

    statement: InvestmentStatementSchema | None = Field(
        None, description="The investment statement"
    )


class GetStatementsResponse(BaseModel):
    quantity: int = Field(..., description="The total number of statement returned")
    statements: list[InvestmentStatementSchema] | None = Field(
        None, description="The investment statements"
    )


class GetStatementMetadataResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )
    period: int = Field(...)
    reference_date: date = Field(
        ..., description="The last business day of the month - ignores holidays"
    )
    contribution: float = Field(0)


# Objectives Schemas
class CreateObjectiveResponse(BaseModel):
    objective_created: bool = Field(
        ..., description="Indicates if the objective was created"
    )


class GetObjectiveResponse(BaseModel):
    quantity: int = Field(..., description="The total number of objectives returned")
    objectives: list[InvestmentObjectiveSchema] = Field(
        ..., description="The list of investment objectives"
    )


class GetInvestmentWithoutObjectives(GetInvestmentResponse):
    pass


class GetObjectiveSummaryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    objective_title: str = Field(..., description="The title of the objective")
    amount_stipulated: float = Field(
        ..., description="The amount stipulated when objective was created"
    )
    amount_invested: float = Field(
        ..., description="The amount invested so far in this objective"
    )
    perc_completed: float = Field(
        ..., description="The percentage completed of the objective"
    )


# Dashboard information
class GetInvestmentAllocationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    type_allocation: list[InvestmentAllocationSchema] | list = Field(
        ..., description="The list of investment allocated by type"
    )
    category_allocation: list[InvestmentAllocationSchema] | list = Field(
        ..., description="The list of investment allocated by category"
    )
    custodian_allocation: list[InvestmentAllocationSchema] | list = Field(
        ..., description="The list of investment allocated by category"
    )
    objective_allocation: list[InvestmentAllocationSchema] | list = Field(
        ..., description="The list of investment allocated by objective"
    )


class GetInvestmentPerformanceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    indexer_name: str = Field(..., description="The name of the indexer")
    data: list[InvestmentPerformanceDataSchema] = Field(
        ..., description="The investment performance data"
    )
    series: list[ChartSeriesSchema] = Field(..., description="The performance series")
    total_invested: float = Field(..., description="The total invested")


class GetInvestmentPerformanceResponseV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    x_label: list[int] = Field(...)
    data: list[ChartSeriesSchemaV2] = Field(...)
    indexer_name: str
