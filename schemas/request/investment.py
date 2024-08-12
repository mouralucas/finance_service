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

