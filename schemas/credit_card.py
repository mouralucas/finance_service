import datetime
import uuid

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from schemas.core import CurrencySchema


class CreditCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='creditCardId', description='The id of the credit card')
    active: bool = Field(..., description='Whether the credit card is active (cancelled) or not')
    owner_id: uuid.UUID = Field(..., serialization_alias='ownerId', description='The id of the card owner')
    nickname: str = Field(..., serialization_alias='nickname', description='The nickname of the card', json_schema_extra={'example': 'My credit card for bank X'})
    # Problem with AccountSchema with crossed imports
    # account: AccountSchema | None = Field(None, serialization_alias='account', description='The account object')
    account_id: uuid.UUID | None = Field(None, serialization_alias='accountId', description='The id of the account, if any')
    currency: CurrencySchema = Field(..., serialization_alias='currency', description='The currency of the card')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency of the card', json_schema_extra={'example': 'BRL'})
    issue_date: datetime.date | None = Field(None, serialization_alias='issueDate', description='The date that the card was issued')
    cancellation_date: datetime.date | None = Field(None, serialization_alias='cancellationDate', description='The date that the card was cancelled')
    due_day: int | None = Field(None, serialization_alias='dueDay', description='The day that the card id due')
    close_day: int | None = Field(None, serialization_alias='closeDay', description='The day that the card id close')


class CreditCardTransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., serialization_alias='transactionId', description='The id of the bill entry')
    credit_card_nickname: str | None = Field(None, serialization_alias='creditCardNickname', description='The nickname of the card')
    credit_card_id: uuid.UUID = Field(..., serialization_alias='creditCardId', description='The id of the credit card')
    period: int = Field(..., serialization_alias='period', description='The period of the bill entry')
    due_date: datetime.date = Field(..., serialization_alias='dueDate', description='The due date of the bill entry')
    transaction_date: datetime.date = Field(..., serialization_alias='transactionDate', description='The date of the bill entry transaction')
    amount: float = Field(..., serialization_alias='amount', description='The amount of the bill entry')
    # category: CategorySchema = Field(..., serialization_alias='category', description='The category of the bill entry')

    category_id: uuid.UUID = Field(..., serialization_alias='categoryId', description='The id of the bill entry')
    category_name: str | None = Field(None, serialization_alias='categoryName', description='The category name of the transaction')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency of the bill entry')
    currency_symbol: str | None = Field(None, serialization_alias='currencySymbol', description='The currency symbol')

    transaction_currency_id: str | None = Field(None, serialization_alias='transactionCurrencyId', description='The id of original currency of transaction')
    transaction_currency_symbol: str | None = Field(None, serialization_alias='transactionCurrencySymbol', description='The transaction currency symbol')
    transaction_amount: float = Field(..., serialization_alias='transactionAmount', description='The amount of the bill entry')

    is_installment: bool = Field(..., serialization_alias='isInstallment', description='Whether the bill entry is installment')
    current_installment: int = Field(..., serialization_alias='currentInstallment', description='The installment of the bill entry')
    installments: int = Field(..., serialization_alias='installments', description='The number of installments of the bill entry')
    total_amount: float | None = Field(None, serialization_alias='totalAmount', description='The total amount of the bill entry')

    description: str | None = Field(None, description='The description of the bill entry')

    created_at: datetime.datetime = Field(..., description='The date that the transaction was created')
    edited_at: datetime.datetime | None = Field(None, description='The date that the transaction was edited')


class CreditCardBillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(serialization_alias=to_camel))

    nickname: str = Field(..., description='The nickname of the credit card')
    period: int = Field(..., description='The period of the bill')
    total_amount: float = Field(..., description='The total amount of the bill')


class CreditCardsTotalBillByCardSchema(BaseModel):
    nickname: str = Field(..., description='The nickname of the credit card')
    currency_symbol: str = Field(..., description='The currency symbol for the credit card')
    total: float = Field(..., description='The total for the credit card')


class CreditCardTotalBillByCurrencySchema(BaseModel):
    currency_symbol: str = Field(..., description='The currency symbol for the credit card')
    total: float = Field(..., description='The total amount for the currency')


class CreditCardBillHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(serialization_alias=to_camel),
                              extra="allow",
                              )

    id: int = Field(..., description='The id of the bill, usually the period')
    period: int = Field(..., description='The period of the bill')
    total_amount: list[CreditCardTotalBillByCurrencySchema] = Field(..., description='The total spent in the period by currency')
    credit_cards: list[CreditCardsTotalBillByCardSchema] = Field(..., description='The list of credit cards')

class InstallmentsDueDates(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    current_installment: int = Field(..., description='The current installment')
    due_date: datetime.date = Field(..., description='The due date for the installment')
