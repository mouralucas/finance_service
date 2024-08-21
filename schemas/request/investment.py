import datetime
import uuid
from dataclasses import Field

from pydantic import BaseModel, Field


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
    pass


class GetStatementRequest(BaseModel):
    pass
