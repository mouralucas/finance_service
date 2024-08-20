import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from schemas.core import CurrencySchema


class CreditCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='creditCardId', description='The id of the credit card')
    owner_id: uuid.UUID = Field(..., serialization_alias='ownerId', description='The id of the card owner')
    nickname: str = Field(..., serialization_alias='nickname', description='The nickname of the card', json_schema_extra={'example': 'My credit card for bank X'})
    account_id: uuid.UUID | None = Field(None, serialization_alias='accountId', description='The id of the account, if any')
    currency: CurrencySchema = Field(..., serialization_alias='currency', description='The currency of the card')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency of the card', json_schema_extra={'example': 'BRL'})
    issue_date: datetime.date | None = Field(None, serialization_alias='issueDate', description='The date that the card was issued')
    cancellation_date: datetime.date | None = Field(None, serialization_alias='cancellationDate', description='The date that the card was cancelled')
    due_day: int | None = Field(None, serialization_alias='dueDay', description='The day that the card id due')
    close_day: int | None = Field(None, serialization_alias='closeDay', description='The day that the card id close')


class BillEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='billEntryId', description='The id of the bill entry')
    credit_card_id: uuid.UUID = Field(..., serialization_alias='creditCardId', description='The id of the credit card')
    period: int = Field(..., serialization_alias='period', description='The period of the bill entry')
    due_date: datetime.date = Field(..., serialization_alias='dueDate', description='The due date of the bill entry')
    transaction_date: datetime.date = Field(..., serialization_alias='transactionDate', description='The date of the bill entry transaction')
    amount: float = Field(..., serialization_alias='amount', description='The amount of the bill entry')
    # category: CategorySchema = Field(..., serialization_alias='category', description='The category of the bill entry')
    category_id: uuid.UUID | None = Field(None, serialization_alias='categoryId', description='The id of the bill entry')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency of the bill entry')

    transaction_currency_id: str | None = Field(None, serialization_alias='transactionCurrencyId', description='The id of original currency of transaction')
    transaction_amount: float = Field(..., serialization_alias='transactionAmount', description='The amount of the bill entry')

    is_installment: bool = Field(..., serialization_alias='isInstallment', description='Whether the bill entry is installment')
    current_installment: int = Field(..., serialization_alias='currentInstallment', description='The installment of the bill entry')
    installments: int = Field(..., serialization_alias='installments', description='The number of installments of the bill entry')
    total_amount: float = Field(..., serialization_alias='totalAmount', description='The total amount of the bill entry')

    description: str = Field(..., description='The description of the bill entry')
