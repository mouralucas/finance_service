import uuid
import datetime

from pydantic import BaseModel, Field


class CreateCreditCardRequest(BaseModel):
    nickname: str = Field(..., alias="nickname", description='A nickname for the card')
    account_id: uuid.UUID = Field(..., alias="accountId", description='The account id, if any')
    issue_date: datetime.date = Field(None, alias="issueDate", description='The issue date of the card')
    cancellation_date: datetime.date = Field(None, alias="cancellationDate", description='The cancel date of the card')
    due_day: int = Field(..., alias="dueDay", description='The due day of the card')
    close_day: int = Field(..., alias="closeDay", description='The close day of the card')
