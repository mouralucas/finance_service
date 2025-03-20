import datetime
from datetime import date
import uuid
from decimal import Decimal

from fastapi import Query
from pydantic import BaseModel, Field, model_validator, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel

from schemas.request.finance import TaxFeeRequest


class CreateInvestmentBaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    name: str = Field(..., description='The name of the investment')
    account_id: uuid.UUID = Field(..., description='The id of the account')

    price: Decimal = Field(None, description='The unit price for the investment')
    quantity: Decimal = Field(None, description='The quantity of the investment bought')
    amount: Decimal = Field(None, description='The total bought. Quantity * price')

    type_id: uuid.UUID = Field(..., alias='investmentTypeId', description='The id of the investment type')
    currency_id: str = Field(..., description='The id of the currency')
    country_id: str = Field('BR', description='The id of the country')

    objective_id: uuid.UUID | None = Field(None, description='The id of the objective')
    observation: str = Field(None, description='Observations for the investment')


class CreateFixedIncomeInvestmentBrazilRequest(CreateInvestmentBaseRequest):
    issue_date: datetime.date = Field(..., description='The date the investment was issued')
    transaction_date: datetime.date = Field(..., description='The date the investment was transmitted')
    maturity_date: datetime.date = Field(..., description='The date the investment will due')
    grace_period_date: datetime.date = Field(..., description='The date the investment can be liquidated')
    contracted_rate: str = Field(..., description='The rate of the investment')
    indexer_type_id: uuid.UUID = Field(..., description='The type of the index for the investment')
    indexer_id: uuid.UUID = Field(..., description='The id of the investment index')


class CreateFundInvestmentBrazilRequest(CreateInvestmentBaseRequest):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    investment_quotation_date: datetime.date = Field(..., description='The day that the investment is quoted')
    investment_settlement_date: datetime.date = Field(..., description='The date the investment is liquidated in the fund')
    redemption_quotation_date: datetime.date = Field(None, description='')
    redemption_settlement_date: datetime.date = Field(None, description='')

class CreateInvestmentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    name: str = Field(..., description='The name of the investment')
    account_id: uuid.UUID = Field(..., description='The id of the account')

    type_id: uuid.UUID = Field(..., alias='investmentTypeId', description='The id of the investment type')
    transaction_date: datetime.date = Field(..., description='The date of the investment')
    maturity_date: datetime.date = Field(None, description='The date that the investment will be liquidated')

    quantity: Decimal = Field(None, description='The quantity of the investment bought')
    price: Decimal = Field(None, description='The unit price for the investment')
    amount: Decimal = Field(None, description='The total bought. Quantity * price')
    contracted_rate: str = Field(..., description='The rate of the investment')

    currency_id: str = Field(..., description='The id of the currency')

    indexer_type_id: uuid.UUID = Field(..., description='The type of the index for the investment')
    indexer_id: uuid.UUID = Field(..., description='The id of the investment index')
    liquidity_id: uuid.UUID = Field(..., description='The id of investment liquidity')
    liquidation_date: datetime.date | None = Field(None, description='The date that the investment was liquidated')
    liquidation_amount: Decimal | None = Field(None, description='The amount liquidated, after tax')
    # tax_detail: TaxFeeRequest | None = Field(None, description='The tax detail of the investment')
    # fee_detail: TaxFeeRequest | None= Field(None, description='The fee detail of the investment')
    country_id: str = Field(..., description='The id of the country')

    observation: str = Field(None, description='Observations for the investment')

    objective_id: uuid.UUID | None = Field(None, description='The id of the objective')

    @model_validator(mode='before')
    def check_liquidation(cls, data: dict) -> dict:
        if (data.get('liquidationAmount') and not data.get('liquidationDate') or
                not data.get('liquidationAmount') and data.get('liquidationDate')):
            raise ValueError('both liquidation date and amount must be specified')

        return data


class UpdateInvestmentRequest(CreateInvestmentRequest):
    """
        It is the same as CreateInvestment, but without any required field
        Only investment id is required
    """
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    id: uuid.UUID = Field(..., alias='investmentId', description='The unique identifier of the investment')
    name: str | None = Field(None, description='The name of the investment')
    account_id: uuid.UUID | None = Field(None, description='The id of the account')
    type_id: uuid.UUID | None = Field(None, description='The id of the investment type')
    transaction_date: datetime.date | None = Field(None, description='The date of the investment')
    contracted_rate: str | None = Field(None, description='The rate of the investment')

    currency_id: str | None = Field(None, description='The id of the currency')

    indexer_type_id: uuid.UUID | None = Field(None, description='The type of the index for the investment')
    indexer_id: uuid.UUID | None = Field(None, description='The id of the investment index')
    liquidity_id: None = Field(None, description='The id of investment liquidity')
    country_id: str | None = Field(None, description='The id of the country')


class GetInvestmentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    id: uuid.UUID | None = Field(None, alias='investmentId', description='The id of the investment')
    start_date: datetime.date | None = Field(None, description='The start date of the filter')
    end_date: datetime.date | None = Field(None, description='The end date of the filter')
    is_liquidated: bool | None = Field(None, description='Whether the investment is liquidated')


class LiquidateInvestmentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    id: uuid.UUID = Field(..., alias='investmentId', description='The unique identifier of the investment')
    gross_amount: Decimal = Field(None, description='The gross amount of the investment at liquidation')
    net_amount: Decimal = Field(None, description='The net amount of the investment at liquidation')
    tax_detail: list[TaxFeeRequest] = Field(None, description='The tax detail of the investment')
    fee_detail: list[TaxFeeRequest] = Field(None, description='The fee detail of the investment')

    liquidation_date: datetime.date = Field(None, alias='liquidationDate', description='The date that the investment was liquidated')
    liquidation_amount: Decimal = Field(None, alias='liquidationAmount', description='The amount liquidated, after tax and fees, usually the same as net_amount')


class CreateStatementRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(alias=to_camel))

    investment_id: uuid.UUID = Field(..., description='The unique identifier of the investment')
    period: int = Field(..., alias='period', description='The period of the statement', examples=['202408'])
    reference_date: datetime.date = Field(..., description='The date when the statement was calculated, usually the last business of the month')
    gross_amount: Decimal = Field(..., description='The gross amount of the period')
    net_amount: Decimal = Field(..., description='The net amount of the period')
    tax_details: list[TaxFeeRequest] | None = Field(None, description='The tax details of the investment tax')
    fee_details: list[TaxFeeRequest] | None = Field(None, description='The fee details of the investment fee')


class CreateBatchStatementRequest(BaseModel):
    statements: list[CreateStatementRequest] = Field(...)


class GetStatementRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    investment_id: uuid.UUID = Field(..., description='The id of the statement')
    start_period: int | None = Field(None, description='The start period of the statement')
    end_period: int | None = Field(None, description='The end period of the statement')
    period: int | None = Field(None, description='The period of the statement')

    @model_validator(mode='before')
    def check_periods(cls, data: dict) -> dict:
        if data.get('period') and (data.get('startPeriod') or data.get('endPeriod')):
            raise ValueError('only specific period or a range is allowed')

        if data.get('startPeriod') and data.get('endPeriod') and (data.get('endPeriod') < data.get('startPeriod')):
            raise ValueError('start period must be before end period')

        return data


class CreateObjectiveRequest(BaseModel):
    title: str = Field(..., alias='title', description='The title of the objective')
    description: str = Field(None, alias='description', description='The description of the objective')
    amount: Decimal = Field(None, alias='amount', description='The amount of the objective')
    estimated_deadline: datetime.date | None = Field(None, alias='estimatedDeadline', description='The estimated deadline of the objective')


class GetObjectiveRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias='objectiveId', description='The unique identifier of the investment objective'))


class GetObjectiveSummaryRequest(BaseModel):
    id: uuid.UUID = Field(..., alias='objectiveId', description='The unique identification of the investment objective')


class GetPerformanceRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    investment_id: uuid.UUID | None = Field(None, description='The id of the investment')
    indexer_id: uuid.UUID = Field('2a2b100f-17d9-4c61-b3b4-f06662113953', description='The unique identifier of the indexer - Default is CDI')
    period_range: int = Field(12, description='The period range of the objective, how many months will be displayed')
