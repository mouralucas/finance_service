import uuid
import datetime

from pydantic import BaseModel, Field


class CreateCreditCardRequest(BaseModel):
    nickname: str = Field(..., alias="nickname", description='A nickname for the card')
    account_id: uuid.UUID = Field(..., alias="accountId", description='The account id, if any')
    issue_date: datetime.date = Field(None, alias="issueDate", description='The issue date of the card')
    cancel_date: datetime.date = Field(None, alias="cancelDate", description='The cancel date of the card')
    due_date: int = Field(..., alias="dueDate", description='The due date of the card')
    close_date: int = Field(..., alias="closeDate", description='The close date of the card')
