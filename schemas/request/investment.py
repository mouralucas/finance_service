import datetime
import uuid
from datetime import date
from decimal import Decimal

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from schemas.request.finance import TaxFeeRequest


# The base schemas for investment
class CreateInvestmentBaseRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    name: str = Field(..., description="The name of the investment")
    account_id: uuid.UUID = Field(..., description="The id of the account")

    price: float | None = Field(None, description="The unit price for the investment")
    quantity: float | None = Field(
        None, description="The quantity of the investment bought"
    )
    amount: float | None = Field(None, description="The total bought. Quantity * price")

    transaction_date: date = Field(..., description="The date")

    type_id: uuid.UUID = Field(
        ..., alias="investmentTypeId", description="The id of the investment type"
    )
    currency_id: str = Field("BRL", description="The id of the currency")
    country_id: str = Field("BR", description="The id of the country")

    objective_id: uuid.UUID | None = Field(None, description="The id of the objective")
    observation: str | None = Field(None, description="Observations for the investment")


class CreateInvestmentStatementBaseRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    period: int = Field(
        ...,
        alias="period",
        description="The period of the statement",
        examples=["202408"],
    )
    reference_date: datetime.date = Field(
        ...,
        description="The date when the statement was calculated, \
            usually the last business of the month",
    )
    gross_amount: float = Field(..., description="The gross amount of the period")
    net_amount: float = Field(..., description="The net amount of the period")
    tax_detail: list[TaxFeeRequest] | None = Field(
        None, description="The tax details of the investment tax"
    )
    fee_detail: list[TaxFeeRequest] | None = Field(
        None, description="The fee details of the investment fee"
    )


# Investment Schemas
class CreateInvestmentRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(alias=to_camel),
    )

    name: str = Field(..., description="The name of the investment")
    account_id: uuid.UUID = Field(..., description="The id of the account")

    type_id: uuid.UUID = Field(
        ..., alias="investmentTypeId", description="The id of the investment type"
    )
    transaction_date: datetime.date = Field(
        ..., description="The date of the investment"
    )
    maturity_date: datetime.date | None = Field(
        None, description="The date that the investment will be liquidated"
    )

    quantity: Decimal | None = Field(
        None, description="The quantity of the investment bought"
    )
    price: Decimal | None = Field(None, description="The unit price for the investment")
    amount: Decimal | None = Field(
        None, description="The total bought. Quantity * price"
    )
    contracted_rate: str = Field(..., description="The rate of the investment")

    currency_id: str = Field(..., description="The id of the currency")

    indexer_type_id: uuid.UUID = Field(
        ..., description="The type of the index for the investment"
    )
    indexer_id: uuid.UUID = Field(..., description="The id of the investment index")
    liquidity_id: uuid.UUID = Field(..., description="The id of investment liquidity")
    settlement_date: datetime.date | None = Field(
        None, description="The date that the investment was liquidated"
    )
    settlement_amount: Decimal | None = Field(
        None, description="The amount liquidated, after tax"
    )
    # tax_detail: TaxFeeRequest | None = Field(None,
    # description='The tax detail of the investment')
    # fee_detail: TaxFeeRequest | None= Field(None,
    # description='The fee detail of the investment')
    country_id: str = Field(..., description="The id of the country")

    observation: str | None = Field(None, description="Observations for the investment")

    objective_id: uuid.UUID | None = Field(None, description="The id of the objective")

    @model_validator(mode="after")
    def check_settlement(self):
        if (
            self.settlement_amount
            and not self.settlement_date
            or not self.settlement_amount
            and self.settlement_date
        ):
            raise ValueError("both settlement date and amount must be specified")

        return self


class UpdateInvestmentRequest(CreateInvestmentRequest):
    """
    It is the same as CreateInvestment, but without any required field
    Only investment id is required
    """

    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID = Field(
        ..., alias="investmentId", description="The unique identifier of the investment"
    )
    name: str | None = Field(None, description="The name of the investment")
    account_id: uuid.UUID | None = Field(None, description="The id of the account")
    type_id: uuid.UUID | None = Field(None, description="The id of the investment type")
    transaction_date: datetime.date | None = Field(
        None, description="The date of the investment"
    )
    contracted_rate: str | None = Field(None, description="The rate of the investment")

    currency_id: str | None = Field(None, description="The id of the currency")

    indexer_type_id: uuid.UUID | None = Field(
        None, description="The type of the index for the investment"
    )
    indexer_id: uuid.UUID | None = Field(
        None, description="The id of the investment index"
    )
    liquidity_id: None = Field(None, description="The id of investment liquidity")
    country_id: str | None = Field(None, description="The id of the country")


# Brazilian Funds Investments Schemas
class GetBrazilianFundInvestmentsRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID | None = Field(
        None, alias="investmentId", description="The id of the investment"
    )
    is_settled: bool = Field(
        False, alias="isSettled", description="Whether the investment is settled"
    )


# Statement Schemas
class UpdateStatementRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID = Field(..., alias="statementId")
    contribution: Decimal | None = Field(None)
    withdrawn: Decimal | None = Field(None)
    gross_amount: Decimal | None = Field(None)
    net_amount: Decimal | None = Field(None)
    tax_detail: list[TaxFeeRequest] | None = Field(None)
    fee_detail: list[TaxFeeRequest] | None = Field(None)


class GetStatementMetadata(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    investment_id: uuid.UUID = Field(..., description="The id of the investment")


# Old schemas
class GetInvestmentRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID | None = Field(
        None, alias="investmentId", description="The id of the investment"
    )
    start_date: datetime.date | None = Field(
        None, description="The start date of the filter"
    )
    end_date: datetime.date | None = Field(
        None, description="The end date of the filter"
    )
    is_settled: bool | None = Field(
        None, description="Whether the investment is settled"
    )


class SettleInvestmentRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID = Field(
        ..., alias="investmentId", description="The unique identifier of the investment"
    )
    gross_amount: Decimal | None = Field(
        None, description="The gross amount of the investment at settlement"
    )
    net_amount: Decimal | None = Field(
        None, description="The net amount of the investment at settlement"
    )
    tax_detail: list[TaxFeeRequest] | None = Field(
        None, description="The tax detail of the investment"
    )
    fee_detail: list[TaxFeeRequest] | None = Field(
        None, description="The fee detail of the investment"
    )

    settlement_date: datetime.date | None = Field(
        None, description="The date that the investment was liquidated"
    )
    settlement_amount: Decimal | None = Field(
        None,
        description="The amount liquidated, after tax and fees, \
                                                   usually the same as net_amount",
    )


class CreateStatementRequest(BaseModel):
    # TODO: use CreateInvestmentStatementBaseRequest
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    investment_id: uuid.UUID = Field(
        ..., description="The unique identifier of the investment"
    )
    period: int = Field(
        ...,
        alias="period",
        description="The period of the statement",
        examples=["202408"],
    )
    contribution: float = Field(0, description="The contribution amount for the period")
    withdrawn: float = Field(0, description="The withdrawn amount for the period")
    reference_date: datetime.date = Field(
        ...,
        description="The date when the statement was calculated, \
            usually the last business of the month",
    )
    gross_amount: Decimal = Field(..., description="The gross amount of the period")
    net_amount: Decimal = Field(..., description="The net amount of the period")
    tax_details: list[TaxFeeRequest] | None = Field(
        None, description="The tax details of the investment tax"
    )
    fee_details: list[TaxFeeRequest] | None = Field(
        None, description="The fee details of the investment fee"
    )


class CreateBatchStatementRequest(BaseModel):
    statements: list[CreateStatementRequest] = Field(...)


class GetStatementsRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    investment_id: uuid.UUID = Field(..., description="The id of the statement")
    start_period: int | None = Field(
        None, description="The start period of the statement"
    )
    end_period: int | None = Field(None, description="The end period of the statement")
    period: int | None = Field(None, description="The period of the statement")

    @model_validator(mode="after")
    def validate_periods(self):
        if self.period and (self.start_period or self.end_period):
            raise ValueError("only specific period or a range is allowed")

        if (
            self.start_period
            and self.end_period
            and (self.end_period < self.start_period)
        ):
            raise ValueError("start period must be before end period")

        return self


class GetStatementByIdRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )
    statement_id: uuid.UUID


class CreateObjectiveRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    title: str = Field(..., description="The title of the objective")
    description: str | None = Field(
        None, alias="description", description="The description of the objective"
    )
    currency_id: str = Field(..., description="The currency of the objective")
    amount: Decimal | None = Field(None, description="The amount of the objective")
    estimated_deadline: datetime.date | None = Field(
        None,
        description="The estimated deadline of the objective",
    )


class GetObjectiveRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    id: uuid.UUID | None = Field(
        None,
        alias="objectiveId",
        description="The unique identifier of the investment objective",
    )


class GetObjectiveSummaryRequest(BaseModel):
    id: uuid.UUID = Field(
        ...,
        alias="objectiveId",
        description="The unique identification of the investment objective",
    )


class GetPerformanceRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=AliasGenerator(alias=to_camel)
    )

    investment_id: uuid.UUID | None = Field(
        None, description="The id of the investment"
    )
    indexer_id: uuid.UUID = Field(
        uuid.UUID("2a2b100f-17d9-4c61-b3b4-f06662113953"),
        description="The unique identifier of the indexer - Default is CDI",
    )
    period_range: int = Field(
        12,
        description="The period range of the objective, \
            how many months will be displayed",
    )
