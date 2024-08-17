import datetime
import uuid

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field, ConfigDict


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias="accountId", description="Unique account ID")
    bank_id: uuid.UUID = Field(..., serialization_alias='bankId', description="Bank account ID")
    nickname: str = Field(..., description="Nickname of the account")
    description: str | None = Field(None, description="Description of the account")
    branch: str | None = Field(None, description="Branch of bank")
    number: str | None = Field(None, description="Account number")
    open_date: datetime.date = Field(..., serialization_alias="openDate", description="Account open date")
    close_date: datetime.date | None = Field(None, serialization_alias="closeDate", description="Account close date")
    type_id: uuid.UUID = Field(..., serialization_alias="typeId", description="Account type")
    currency_id: str = Field(..., serialization_alias='currencyId', description="Account currency")


class StatementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., serialization_alias="statementEntryId", description="Unique statement ID")
    owner_id: uuid.UUID = Field(..., serialization_alias="ownerId", description="Account owner")
    # account object
    account_id: uuid.UUID = Field(..., serialization_alias="accountId", description="Account identification")
    period: int = Field(..., description="Transaction period")
    currency_id: str = Field(..., serialization_alias="currencyId", description="Account currency")
    amount: float = Field(..., description="Transaction amount")
    transaction_date: datetime.date = Field(..., serialization_alias='transactionDate', description="Transaction date")
    # category object
    category_id: uuid.UUID = Field(..., serialization_alias="categoryId", description="Transaction category")
    description: str | None = Field(None, description="Description of the transaction")
    operation_type: str = Field(..., serialization_alias='operationType', description="Transaction operation type")
    transaction_currency_id: str = Field(..., serialization_alias='transactionCurrencyId', description="Transaction currency identification")
    transaction_amount: float = Field(..., serialization_alias='transactionAmount', description="Transaction amount")
    exchange_rate: float | None = Field(None, serialization_alias='exchangeRate', description="Exchange rate")
    tax_perc: float | None = Field(None, serialization_alias='taxPerc', description="Tax percentage")
    tax: float | None = Field(None, serialization_alias='tax', description="Tax amount")
    spread_perc: float | None = Field(None, serialization_alias='spreadPerc', description="Spread percentage")
    spread: float | None = Field(None, serialization_alias='spread', description="Spread amount")
    effective_rate: float | None = Field(None, serialization_alias='effectiveRate', description="Effective rate")
