from datetime import datetime, date
import uuid
from decimal import Decimal

from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel


class CreateCreditCardRequest(BaseModel):
    nickname: str = Field(..., alias="nickname", description='A nickname for the card')
    account_id: uuid.UUID = Field(None, alias="accountId", description='The account id, if any')
    currency_id: str = Field(..., alias="currencyId", description='The currency id')
    issue_date: date = Field(None, alias="issueDate", description='The issue date of the card')
    cancellation_date: date = Field(None, alias="cancellationDate", description='The cancel date of the card')
    due_day: int = Field(..., alias="dueDay", description='The due day of the card')
    close_day: int = Field(..., alias="closeDay", description='The close day of the card')


class CancelCreditCardRequest(BaseModel):
    id: uuid.UUID = Field(None, alias="creditCardId", description='The unique identifier of the card')
    cancellation_date: date = Field(None, alias="cancellationDate", description='The cancel date of the card')


class GetCreditCardRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias="creditCardId", description="The id of the credit card"))


class BillEntryInstallment(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    current_installment: int = Field(..., description="The current installment")
    amount: Decimal = Field(..., description="The amount of the installment")
    due_date: date = Field(..., description='The due date of the installments')


class CreateCreditCardTransactionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    credit_card_id: uuid.UUID = Field(..., description='The credit card id')
    transaction_date: date = Field(None, description='The transaction date of the card')
    total_amount: Decimal = Field(..., description='The total amount of the transaction')
    tot_installments: int = Field(..., description='The total number of installments')
    installments: list[BillEntryInstallment] = Field(...)
    category_id: uuid.UUID = Field(..., description='The id of the category of transaction')
    currency_id: str = Field(..., description='The if of the bill currency')

    # This fields indicates an international transaction
    is_international_transaction: bool = Field(..., description='Whether the transaction is international')
    transaction_currency_id: str = Field(None, description='The currency of the transaction')
    transaction_amount: float = Field(None, description='The amount of the transaction in international currency')

    # This fields represents the values used in the convertion to default card currency
    dollar_exchange_rate: float = Field(None, description='The dollar exchange rate with the default card currency')
    currency_dollar_exchange_rate: float = Field(None, description='The dollar exchange rate with the transaction currency')
    total_tax: Decimal = Field(None, description='The tax amount of the transaction')
    tax_detail: dict = Field(None, description='The tax detail of the transaction')

    description: str = Field(None, description='The description of the transaction')

    origin: str = Field('SYSTEM', description='The origin of the transaction')


class GetInstallmentsDueDatesRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    transaction_date: date = Field(..., description='The transaction date')
    credit_card_id: uuid.UUID = Field(..., description='The credit card id')
    tot_installments: int = Field(..., description='The total installment')

class GetCreditCardTransactionsRequest(BaseModel):
    credit_card_id: uuid.UUID | None = Field(None, alias='creditCardId', description='The id of the credit card')
    start_period: int = Field(None, alias='startPeriod', description='The start period of the transaction')
    end_period: int = Field(None, alias='endPeriod', description='The end period of the transaction')


class GetCreditCardBillRequest(BaseModel):
    start_period: int = Field(None, alias="startPeriod", description='The start period of the bill')
    end_period: int = Field(None, alias="endPeriod", description='The end period of the bill')
