import datetime
import uuid
from dataclasses import Field

from pydantic import BaseModel, Field
from sqlalchemy import alias

from schemas.core import TaxSchema


class CreateInvestmentRequest(BaseModel):
    custodian_id: uuid.UUID = Field(..., alias='custodianId', description='The id of the custodian bank')
    account_id: uuid.UUID = Field(..., alias='accountId', description='The id of the account')
    name: str = Field(..., description='The name of the investment')
    description: str = Field(None, description='Optional description of the investment')
    type_id: uuid.UUID = Field(..., alias='typeId', description='The id of the investment type')
    transaction_date: datetime.date = Field(..., alias='transactionDate', description='The date of the investment')
    maturity_date: datetime.date = Field(None, alias='maturityDate', description='The date that the investment will be liquidated')
    quantity: float = Field(None, description='The quantity of the investment bought')
    price: float = Field(None, description='The unit price for the investment')
    amount: float = Field(None, description='The total bought. Quantity * price')
    currency_id: str = Field(..., alias='currencyId', description='The id of the currency')
    index_type_id: uuid.UUID = Field(..., alias='indexTypeId', description='The type of the index for the investment')

    index_id: uuid.UUID = Field(..., alias='indexId', description='The id of the investment index')
    liquidity_id: uuid.UUID = Field(..., alias='liquidityId', description='The id of investment liquidity')
    liquidation_date: datetime.date = Field(None, alias='liquidationDate', description='The date that the investment was liquidated')
    liquidation_amount: float = Field(None, alias='liquidationAmount', description='The amount liquidated, after tax')
    country_id: str = Field(..., alias='countryId', description='The id of the country')


class GetInvestmentRequest(BaseModel):
    id: uuid.UUID = Field(None, alias='investmentId', description='The id of the investment')
    owner_id: uuid.UUID = Field(None, alias='ownerId', description='The id of the owner of the investment')
    start_date: datetime.date = Field(None, alias='startDate', description='The start date of the filter')
    end_date: datetime.date = Field(None, alias='end_date', description='The end date of the filter')
    # other fields...


class LiquidateInvestmentRequest(BaseModel):
    id: uuid.UUID = Field(..., alias='investmentId', description='The unique identifier of the investment')
    liquidation_date: datetime.date = Field(None, alias='liquidationDate', description='The date that the investment was liquidated')
    liquidation_amount: float = Field(None, alias='liquidationAmount', description='The amount liquidated, after tax')


class CreateStatementRequest(BaseModel):
    investment_id: uuid.UUID = Field(..., alias='investmentId', description='The unique identifier of the investment')
    period: int = Field(..., alias='period', description='The period of the statement', examples=['202408'])
    gross_amount: float = Field(..., alias='grossAmount', description='The gross amount of the period')
    total_tax: float = Field(0, alias='totalTax', description='The total of the tax if investment were liquidated in the period')
    total_fee: float = Field(0, alias='totalFee', description='The total of fee if investment were liquidated in the period')
    net_amount: float = Field(..., alias='netAmount', description='The net amount of the period')
    tax_detail: dict | None = Field(None, alias='taxDetail', description='The tax details of the investment tax')
    fee_detail: dict | None = Field(None, alias='feeDetail', description='The fee details of the investment fee')


class GetStatementRequest(BaseModel):
    pass
