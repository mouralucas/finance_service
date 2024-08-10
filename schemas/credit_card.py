import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class CreditCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_id: uuid.UUID = Field(..., serialization_alias='ownerId', description='The id of the card owner')
    nickname: str = Field(..., serialization_alias='nickname', description='The nickname of the card')
    account_id: uuid.UUID | None = Field(None, serialization_alias='accountId', description='The id of the account, if any')
    issue_date: datetime.date | None = Field(None, serialization_alias='issueDate', description='The date that the card was issued')
    cancel_date: datetime.date | None = Field(None, serialization_alias='cancelDate', description='The date that the card was cancelled')
