import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from schemas.core import CurrencySchema


class CreditCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_id: uuid.UUID = Field(..., serialization_alias='ownerId', description='The id of the card owner')
    nickname: str = Field(..., serialization_alias='nickname', description='The nickname of the card')
    account_id: uuid.UUID | None = Field(None, serialization_alias='accountId', description='The id of the account, if any')
    currency: CurrencySchema = Field(..., serialization_alias='currency', description='The currency of the card')
    currency_id: str = Field(..., serialization_alias='currencyId', description='The id of the currency of the card')
    issue_date: datetime.date | None = Field(None, serialization_alias='issueDate', description='The date that the card was issued')
    cancellation_date: datetime.date | None = Field(None, serialization_alias='cancellationDate', description='The date that the card was cancelled')
    due_day: int | None = Field(None, serialization_alias='dueDay', description='The day that the card id due')
    close_day: int | None = Field(None, serialization_alias='closeDay', description='The day that the card id close')

