import datetime
import uuid
from typing import Any

from fastapi import Query
from pydantic import BaseModel, Field, model_validator


class CreateCreditCardRequest(BaseModel):
    nickname: str = Field(..., alias="nickname", description='A nickname for the card')
    account_id: uuid.UUID = Field(None, alias="accountId", description='The account id, if any')
    currency_id: str = Field(..., alias="currencyId", description='The currency id')
    issue_date: datetime.date = Field(None, alias="issueDate", description='The issue date of the card')
    cancellation_date: datetime.date = Field(None, alias="cancellationDate", description='The cancel date of the card')
    due_day: int = Field(..., alias="dueDay", description='The due day of the card')
    close_day: int = Field(..., alias="closeDay", description='The close day of the card')


class CancelCreditCardRequest(BaseModel):
    id: uuid.UUID = Field(None, alias="creditCardId", description='The unique identifier of the card')
    cancellation_date: datetime.date = Field(None, alias="cancellationDate", description='The cancel date of the card')


class GetCreditCardRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias="creditCardId", description="The id of the credit card"))


class BillEntryInstallment(BaseModel):
    amount: float = Field(..., alias="amount")
    current_installment: int = Field(..., alias="currentInstallment")
    installments: int = Field(..., alias="installments")


class CreateCreditCardTransactionRequest(BaseModel):
    credit_card_id: uuid.UUID = Field(..., alias="creditCardId", description='The credit card id')
    transaction_date: datetime.date = Field(None, alias="transactionDate", description='The transaction date of the card')
    total_amount: float = Field(..., alias="totalAmount", description='The total amount of the transaction')
    installments: list[BillEntryInstallment] = Field(..., alias="installments")
    category_id: uuid.UUID = Field(..., alias="categoryId", description='The id of the category of transaction')
    currency_id: str = Field(..., alias="currencyId", description='The if of the bill currency')

    # This fields indicates an international transaction
    is_international_transaction: bool = Field(..., alias='isInternationalTransaction', description='Whether the transaction is international')
    transaction_currency_id: str = Field(None, alias="transactionCurrencyId", description='The currency of the transaction')
    transaction_amount: float = Field(None, alias="transactionAmount", description='The amount of the transaction in international currency')

    # This fields represents the values used in the convertion to default card currency
    dollar_exchange_rate: float = Field(None, alias='dollarExchangeRate', description='The dollar exchange rate with the default card currency')
    currency_dollar_exchange_rate: float = Field(None, alias='currencyDollarExchangeRate', description='The dollar exchange rate with the transaction currency')
    total_tax: float = Field(None, alias='totalTax', description='The tax amount of the transaction')
    tax_detail: dict = Field(None, alias='taxDetail', description='The tax detail of the transaction')

    description: str = Field(None, alias='description', description='The description of the transaction')

    origin: str = Field('SYSTEM', alias='origin', description='The origin of the transaction')
    operation_type: str = Field(None, alias="operationType", description="The type of the transaction")
