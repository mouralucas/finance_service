import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake


class InvestmentCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
        serialization_alias=to_camel,
    ))

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: str | None = Field(None)


class InvestmentTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel,
    ))

    id: uuid.UUID = Field(..., serialization_alias='investmentTypeId', description='The unique identification for the investment type')
    name: str = Field(..., serialization_alias='investmentTypeName', description='The name of the investment type')
    description: str | None = Field(None, description='Description of the investment type')
    parent_id: uuid.UUID | None = Field(None, description='The id of the parent investment type')
    investment_category_id: uuid.UUID | None = Field(None, description='The id the category of this type of investment')


class InvestmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(
                                  alias=to_camel,
                                  validation_alias=to_snake,
                                  serialization_alias=to_camel,
                              ))

    id: uuid.UUID = Field(..., serialization_alias='investmentId', description='Unique identifier of the investment')
    custodian_id: uuid.UUID = Field(..., description='The id of the custodian bank')
    account_id: uuid.UUID | None = Field(None, description='The id of the account')
    name: str = Field(..., description='The name of the investment')
    description: str | None = Field(None, description='Optional description of the investment')
    type_id: uuid.UUID = Field(..., serialization_alias='investmentTypeId', description='The id of the investment type')
    transaction_date: datetime.date = Field(..., description='The date of the investment')
    maturity_date: datetime.date | None = Field(None, serialization_alias='maturityDate', description='The date that the investment will be liquidated')
    quantity: float = Field(..., description='The quantity of the investment bought')
    price: float = Field(..., description='The unit price for the investment')
    amount: float = Field(..., description='The total bought. Quantity * price')
    contracted_rate: str | None = Field(None, description='The rate of the investment')
    currency_id: str = Field(..., description='The id of the currency')
    currency_symbol: str | None = Field(None, description='The currency symbol')
    indexer_type_id: uuid.UUID = Field(..., description='The id of index type for the investment')
    indexer_type_name: str | None = Field(None, description='The name of the index type for the investment')
    indexer_id: uuid.UUID = Field(..., description='The id of the investment index')
    indexer_name: str | None = Field(None, description='The name of the investment index')
    liquidity_id: uuid.UUID = Field(..., description='The id of investment liquidity')
    liquidity_name: str | None = Field(None, description='The name of the investment liquidity')
    is_liquidated: bool = Field(False, description='Whether the investment is liquidated')
    liquidation_date: datetime.date | None = Field(None, description='The date that the investment was liquidated')
    liquidation_amount: Decimal | None = Field(None, description='The amount liquidated, after tax')
    country_id: str = Field(..., description='The id of the country')
    country_name: str | None = Field(None, description='The name of the country of the investment')
    objective_id: uuid.UUID | None = Field(None, description='The id of the objective')

    gross_amount: Decimal | None = Field(None, description='The gross amount of last period available')
    percentage_change: Decimal | None = Field(None, description='The percentage change from start to last period available')


class TaxFeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
        serialization_alias=to_camel,
    ))

    id: uuid.UUID = Field(..., serialization_alias='taxFeeId', description='The identification of the tax/fee')
    amount: Decimal = Field(..., description='The amount of the tax/fee')
    currency_id: str = Field('BRL', description='The currency of the tax/fee')


class InvestmentStatementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
        serialization_alias=to_camel,
    ))

    id: uuid.UUID = Field(..., serialization_alias='investmentStatementId', description='The id of the statement')
    investment_id: uuid.UUID = Field(..., description='The id of the investment')
    investment: InvestmentSchema = Field(..., description='The object of the investment')
    period: int = Field(..., description='The period of the statement')
    gross_amount: Decimal = Field(..., description='The gross amount of the investment in the period')
    total_tax: Decimal = Field(..., description='The total tax amount of the investment in the period')
    tax_detail: list[TaxFeeResponse] | None = Field(..., description='The detail of taxes')
    total_fee: Decimal = Field(..., description='The total fee of the investment in the period')
    fee_detail: list[TaxFeeResponse] | None = Field(..., description='The detail of fees')
    net_amount: Decimal = Field(..., description='The net amount of the investment in the period')


class InvestmentObjectiveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
        serialization_alias=to_camel,
    ))

    id: uuid.UUID = Field(..., serialization_alias='objectiveId', description='The id of the objective')
    owner_id: uuid.UUID = Field(..., description='The id of the owner of the objective')
    title: str = Field(..., description='The title of the objective')
    description: str | None = Field(None, description='The description of the objective')
    amount: Decimal = Field(..., description='The amount of the objective')
    estimated_deadline: datetime.date | None = Field(None, description='The date that are expected to reach the objective')


# Allocation
class InvestmentAllocationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        validation_alias=to_snake,
        serialization_alias=to_camel,
    ))

    name: str = Field(..., description='The name of the allocation')
    total: Decimal = Field(..., description='The total amount allocated')
