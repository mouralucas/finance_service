import datetime
import uuid

from pydantic import BaseModel, Field
from fastapi import Query


class CreateAccountRequest(BaseModel):
    bank_id: uuid.UUID = Field(..., alias="bankId", description="The id of the bank")
    nickname: str = Field(..., alias="nickname", description="The nickname of the account")
    description: str = Field(None, alias="description", description="The description of the account")
    branch: str = Field(None, alias="branch", description="The branch of the account")
    number: str = Field(None, alias="number", description="The number of the account")
    open_date: datetime.date = Field(None, alias="openDate", description="The open date of the account")
    close_date: datetime.date = Field(None, alias="closeDate", description="The close date of the account")
    type_id: uuid.UUID = Field(..., alias='accountTypeId', description="The type of the account")
    currency_id: str = Field(None, alias="currencyId", description="The currency of the account")


class GetAccountRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias="accountId", description="The id of the account"))


class CreateStatementRequest(BaseModel):
    account_id: uuid.UUID = Field(..., alias="accountId", description="The id of the account")
    currency_id: str = Field(..., alias="currencyId", description="The currency of the account")
    amount: float = Field(..., alias='amount', description="The amount of the transaction in the account currency")
    transaction_date: datetime.date = Field(..., alias="transactionDate", description="The date of the transaction")
    category_id: uuid.UUID = Field(..., alias="categoryId", description="The id of the category")
    description: str = Field(None, alias="description", description="The description of the transaction")
    operation_type: str = Field(None, alias="operationType", description="The type of the transaction")

    transaction_currency_id: str = Field(None, alias="transactionCurrencyId", description="The currency of the transaction")
    transaction_amount: float = Field(None, alias="transactionAmount", description="The amount in the transaction currency")
    exchange_rate: float = Field(None, alias="exchangeRate", description="The exchange rate for international transactions")
    tax_perc: float = Field(None, alias="taxPerc", description="The percentage of tax")
    tax: float = Field(None, alias="tax", description="The tax of transaction")
    spread_perc: float = Field(None, alias="spreadPerc", description="The percentage of spread")
    spread: float = Field(None, alias="spread", description="The spread of transaction")
    effective_rate: float = Field(None, alias="effectiveRate", description="The effective rate of the transaction")

    origin: str = Field("SYSTEM", alias="origin", description="The origin of the entry")
    is_validated: bool = Field(None, alias="isValidated", description="Whether the transaction is validated by the user")
