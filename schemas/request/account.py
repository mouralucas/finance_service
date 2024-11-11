import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from fastapi import Query
from pydantic.alias_generators import to_camel, to_snake
from rolf_common.schemas.base import DefaultModel


class CreateAccountRequest(BaseModel):
    bank_id: uuid.UUID = Field(..., alias="bankId", description="The id of the bank")
    nickname: str = Field(..., alias="nickname", description="The nickname of the account")
    description: str = Field(None, alias="description", description="The description of the account")
    branch: str = Field(None, alias="branch", description="The branch of the account")
    number: str = Field(None, alias="number", description="The number of the account")
    open_date: datetime.date = Field(None, alias="openDate", description="The open date of the account")
    close_date: datetime.date = Field(None, alias="closeDate", description="The close date of the account")
    type_id: uuid.UUID = Field(..., alias='accountTypeId', description="The type of the account")
    currency_id: str = Field(..., alias="currencyId", description="The currency of the account")


class CloseAccountRequest(BaseModel):
    id: uuid.UUID = Field(..., alias="accountId", description="The id of the account")
    close_date: datetime.date = Field(None, alias="closeDate", description="The close date of the account")


class GetAccountRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias="accountId", description="The id of the account"))
    currency_id: str | None = Field(Query(None, alias="currencyId", description="The currency of the account"))
    active: bool = Field(Query(True, description="Whether the account is active"))


class CreateAccountTransactionRequest(DefaultModel):

    account_id: uuid.UUID = Field(..., description="The id of the account")
    currency_id: str = Field(..., description="The currency of the account")
    amount: Decimal = Field(..., description="The amount of the transaction in the account currency")
    transaction_date: datetime.date = Field(..., description="The date of the transaction")
    category_id: uuid.UUID = Field(..., description="The id of the category")
    description: str = Field(None,  description="The description of the transaction")

    transaction_currency_id: str = Field(None, description="The currency of the transaction")
    transaction_amount: Decimal = Field(None, description="The amount in the transaction currency")
    exchange_rate: Decimal | None = Field(None, description="The exchange rate for international transactions")
    tax_perc: Decimal = Field(None, description="The percentage of tax")
    tax: Decimal = Field(None, description="The tax of transaction")
    spread_perc: Decimal = Field(None, description="The percentage of spread")
    spread: Decimal = Field(None, description="The spread of transaction")
    effective_rate: Decimal | None = Field(None, description="The effective rate of the transaction")

    origin: str = Field("SYSTEM", description="The origin of the entry")
    is_validated: bool = Field(None, description="Whether the transaction is validated by the user")


class UpdateAccountTransactionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel,
        serialization_alias=to_camel,
    ))

    id: int = Field(...,  alias='transactionId', description="The id of the account")
    account_id: uuid.UUID | None = Field(None, description="The id of the account")
    currency_id: str | None = Field(None, description="The currency of the account")
    amount: Decimal | None = Field(None, description="The amount of the transaction in the account currency")
    transaction_date: datetime.date | None = Field(None, description="The date of the transaction")
    category_id: uuid.UUID | None = Field(None, description="The id of the category")
    description: str | None = Field(None, description="The description of the transaction")
    transaction_currency_id: str | None = Field(None, description="The currency of the transaction")
    transaction_amount: Decimal | None = Field(None, description="The amount in the transaction currency")
    exchange_rate: Decimal | None = Field(None, description="The exchange rate for international transactions")
    tax_perc: Decimal | None = Field(None, description="The percentage of tax")
    tax: Decimal | None = Field(None, description="The tax of transaction")
    spread_perc: Decimal | None = Field(None, description="The percentage of spread")
    spread: Decimal | None = Field(None, description="The spread of transaction")
    effective_rate: Decimal | None = Field(None, description="The effective rate of the transaction")

    origin: str = Field("SYSTEM", description="The origin of the entry")
    is_validated: bool | None = Field(None, description="Whether the transaction is validated by the user")


class CreateBalanceRequest(BaseModel):
    account_id: uuid.UUID = Field(None, alias='accountId', description='The id of the account')
    start_period: int = Field(None, alias='startPeriod', description='The start period of the balance')


class GetBalanceRequest(BaseModel):
    account_id: uuid.UUID = Field(None, alias='accountId', description='The id of the account')
    start_period: int | None = Field(None, alias='startPeriod', description='The start period of the balance')
    end_period: int | None = Field(None, alias='endPeriod', description='The end period of the balance')
