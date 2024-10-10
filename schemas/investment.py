import datetime
import uuid
from gzip import FEXTRA

from pydantic import BaseModel, Field, ConfigDict


class InvestmentTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='investmentTypeId', description='The unique identification for the investment type')
    name: str = Field(..., description='The name of the investment type')
    description: str | None = Field(None, description='Description of the investment type')
    parent_id: uuid.UUID | None = Field(None, serialization_alias='parentId', description='The id of the parent investment type')
    investment_category_id: uuid.UUID | None = Field(None, description='The id the category of this type of investment')


class InvestmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='investmentId', description='Unique identifier of the investment')
    custodian_id: uuid.UUID = Field(..., serialization_alias='custodianId', description='The id of the custodian bank')
    account_id: uuid.UUID = Field(..., serialization_alias='accountId', description='The id of the account')
    name: str = Field(..., description='The name of the investment')
    description: str | None = Field(None, description='Optional description of the investment')
    type_id: uuid.UUID = Field(..., serialization_alias='typeId', description='The id of the investment type')
    transaction_date: datetime.date = Field(..., serialization_alias='transactionDate', description='The date of the investment')
    maturity_date: datetime.date | None = Field(None, serialization_alias='maturityDate', description='The date that the investment will be liquidated')
    quantity: float = Field(None, description='The quantity of the investment bought')
    price: float = Field(None, description='The unit price for the investment')
    amount: float = Field(None, description='The total bought. Quantity * price')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency')
    indexer_type_id: uuid.UUID = Field(..., serialization_alias='indexerTypeId', description='The id of index type for the investment')

    indexer_id: uuid.UUID = Field(..., serialization_alias='indexerId', description='The id of the investment index')
    liquidity_id: uuid.UUID = Field(..., serialization_alias='liquidityId', description='The id of investment liquidity')
    is_liquidated: bool = Field(None, serialization_alias='isLiquidated', description='Whether the investment is liquidated')
    liquidation_date: datetime.date | None = Field(None, serialization_alias='liquidationDate', description='The date that the investment was liquidated')
    liquidation_amount: float | None = Field(None, serialization_alias='liquidationAmount', description='The amount liquidated, after tax')

    country_id: str = Field(..., serialization_alias='countryId', description='The id of the country')

    objective_id: uuid.UUID | None = Field(None, serialization_alias='objectiveId', description='The id of the objective')


class TaxFeeResponse(BaseModel):
    id: uuid.UUID = Field(..., serialization_alias='taxFeeId', description='The identification of the tax/fee')
    amount: float = Field(..., description='The amount of the tax/fee')
    currency_id: str = Field('BRL', serialization_alias='currencyId', description='The currency of the tax/fee')


class InvestmentStatementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='investmentStatementId', description='The id of the statement')
    investment_id: uuid.UUID = Field(..., serialization_alias='investmentId', description='The id of the investment')
    investment: InvestmentSchema = Field(..., serialization_alias='investment', description='The object of the investment')
    period: int = Field(..., serialization_alias='period', description='The period of the statement')
    gross_amount: float = Field(..., serialization_alias='grossAmount', description='The gross amount of the investment in the period')
    total_tax: float = Field(..., serialization_alias='totalTax', description='The total tax amount of the investment in the period')
    tax_detail: list[TaxFeeResponse] | None = Field(..., serialization_alias='taxDetail', description='The detail of taxes')
    total_fee: float = Field(..., serialization_alias='totalFee', description='The total fee of the investment in the period')
    fee_detail: list[TaxFeeResponse] | None = Field(..., serialization_alias='feeDetail', description='The detail of fees')
    net_amount: float = Field(..., serialization_alias='netAmount', description='The net amount of the investment in the period')


class InvestmentObjectiveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='objectiveId', description='The id of the objective')
    owner_id: uuid.UUID = Field(..., serialization_alias='ownerId', description='The id of the owner of the objective')
    title: str = Field(..., description='The title of the objective')
    description: str | None = Field(None, description='The description of the objective')
    amount: float = Field(..., description='The amount of the objective')
    estimated_deadline: datetime.date | None = Field(None, serialization_alias='estimatedDeadline', description='The date that are expected to reach the objective')
