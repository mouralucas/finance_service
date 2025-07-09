import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from schemas.credit_card import CreditCardSchema


class AccountTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='accountTypeId', description='The unique identification of the account type')
    type: str = Field(..., description='The type of account')
    description: str = Field(..., description='The description of the account type')


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias="accountId", description="Unique account id")
    active: bool = Field(..., description="Whether the account is active (open) or closed")
    bank_id: uuid.UUID = Field(..., serialization_alias='bankId', description="Bank account id")
    nickname: str = Field(..., description="Nickname of the account")
    description: str | None = Field(None, description="Description of the account")
    branch: str | None = Field(None, description="Branch of bank")
    number: str | None = Field(None, description="Account number")
    open_date: datetime.date = Field(..., serialization_alias="openDate", description="Account open date")
    close_date: datetime.date | None = Field(None, serialization_alias="closeDate", description="Account close date")
    type_id: uuid.UUID = Field(..., serialization_alias="typeId", description="Account type")
    currency_id: str = Field(..., serialization_alias='currencyId', description="Account currency")
    credit_cards: list[CreditCardSchema] | None = Field(None, serialization_alias='creditCards', description="List of credit cards of the account")


class AccountTransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., serialization_alias="transactionId", description="Unique transaction ID")
    owner_id: uuid.UUID | None = Field(..., serialization_alias="ownerId", description="Account owner")
    # account object
    account_id: uuid.UUID = Field(..., serialization_alias="accountId", description="Account identification")
    account_nickname: str = Field(None, serialization_alias='accountNickname', description='The nickname of the account')
    period: int = Field(..., description="Transaction period")
    currency_id: str = Field(..., serialization_alias="currencyId", description="Account currency")
    currency_symbol: str | None = Field(None, serialization_alias='currencySymbol', description='The currency symbol')
    amount: float = Field(..., description="Transaction amount")
    transaction_date: datetime.date = Field(..., serialization_alias='transactionDate', description="Transaction date")
    # category object
    category_id: uuid.UUID = Field(..., serialization_alias="categoryId", description="Transaction category")
    category_name: str | None = Field(None, serialization_alias='categoryName', description='The category name of the transaction')
    description: str | None = Field(None, description="Description of the transaction")
    operation_type: str | None = Field(None, serialization_alias='operationType', description="Transaction operation type")
    transaction_currency_id: str = Field(..., serialization_alias='transactionCurrencyId', description="Transaction currency identification")
    transaction_currency_symbol: str | None = Field(None, serialization_alias='transactionCurrencySymbol', description='The transaction currency symbol')
    transaction_amount: float = Field(..., serialization_alias='transactionAmount', description="Transaction amount")
    exchange_rate: float | None = Field(None, serialization_alias='exchangeRate', description="Exchange rate")
    tax_perc: float | None = Field(None, serialization_alias='taxPerc', description="Tax percentage")
    tax: float | None = Field(None, serialization_alias='tax', description="Tax amount")
    spread_perc: float | None = Field(None, serialization_alias='spreadPerc', description="Spread percentage")
    spread: float | None = Field(None, serialization_alias='spread', description="Spread amount")
    effective_rate: float | None = Field(None, serialization_alias='effectiveRate', description="Effective rate")


class BalanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias='balanceEntryId', description='The id of the balance entry')
    account_id: uuid.UUID = Field(..., serialization_alias='accountId', description='Account identification')
    previous_balance: Decimal = Field(None, description="The balance from the past period")
    incoming: Decimal = Field(None, description="The amount o money that enter the account in the period")
    outgoing: Decimal = Field(None, description="The amount o money that leave the account in the period")
    transactions: Decimal = Field(None, description="The difference between incoming and outgoing")
    earning: Decimal = Field(None, description="How much the account profits in the period, if set")
    balance: Decimal = Field(None, description="How many money is in the account by the end of the period")


class AccountBalanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # id: uuid.UUID = Field(..., serialization_alias='balanceId', description='The id of the balance')
    # account_id: uuid.UUID = Field(..., serialization_alias='accountId', description='Account identification')
    period: int = Field(..., description='The period of the balance')
    previous_balance: Decimal = Field(None, description="The balance from the past period")
    incoming: Decimal = Field(None, description="The amount o money that enter the account in the period")
    outgoing: Decimal = Field(None, description="The amount o money that leave the account in the period")
    transactions: Decimal = Field(None, description="The difference between incoming and outgoing")
    earnings: Decimal = Field(None, description="How much the account profits in the period, if set")
    balance: Decimal = Field(None, description="How many money is in the account by the end of the period")