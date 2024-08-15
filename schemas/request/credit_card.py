import uuid
import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class CreateCreditCardRequest(BaseModel):
    nickname: str = Field(..., alias="nickname", description='A nickname for the card')
    account_id: uuid.UUID = Field(..., alias="accountId", description='The account id, if any')
    issue_date: datetime.date = Field(None, alias="issueDate", description='The issue date of the card')
    cancellation_date: datetime.date = Field(None, alias="cancellationDate", description='The cancel date of the card')
    due_day: int = Field(..., alias="dueDay", description='The due day of the card')
    close_day: int = Field(..., alias="closeDay", description='The close day of the card')


class CreateBillEntryRequest(BaseModel):
    credit_card_id: uuid.UUID = Field(..., alias="creditCardId", description='The credit card id')
    due_date: datetime.date = Field(None, alias="dueDate", description='The due date of the card')
    transaction_date: datetime.date = Field(None, alias="transactionDate", description='The transaction date of the card')
    amount: float = Field(..., alias="amount", description='The amount of the transaction')

    currency_id: str = Field(..., alias="currencyId", description='The if of the bill currency')

    # In the front-end put a check-box "compra internacional" then open a box with this info
    # Create this field only here, the exclude from model_dump()
    transaction_currency_id: str = Field(None, alias="transactionCurrencyId", description='The currency of the transaction')

    @model_validator(mode='before')
    def validate_international_transaction(cls, data: dict[str: Any]) -> dict[str, Any]:
        if data['transactionCurrencyId'] is None:
            data['transactionCurrencyId'] = data['currencyId']

        return data
