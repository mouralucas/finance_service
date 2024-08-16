import datetime
import uuid

from pydantic import BaseModel, Field
from fastapi import Query

class CreateAccountRequest(BaseModel):
    bank_id: uuid.UUID = Field(..., alias="bankId", description="The id of the bank")
    nickname: str = Field(..., alias="nickname", description="The nickname of the account")
    description: str = Field(None, alias="description", description="The description of the account")
    branch: str = Field(None, alias="branch", description="The branch of the account")
    number: str = Field(None, alias="number", description="The number of the account")
    open_date: datetime.date = Field(None, alias="openDate", description="The open date of the account")
    close_date: datetime.date = Field(None, alias="closeDate", description="The close date of the account")
    type_id: uuid.UUID = Field(..., alias='accountTypeId', description="The type of the account")


class GetAccountRequest(BaseModel):
    id: uuid.UUID | None = Field(Query(None, alias="accountId", description="The id of the account"))

