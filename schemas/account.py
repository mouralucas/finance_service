import datetime
import uuid

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field, ConfigDict


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias="accountId", description="Unique account ID")
    bank_id: uuid.UUID = Field(..., serialization_alias='bankId', description="Bank account ID")
    nickname: str = Field(..., description="Nickname of the account")
    description: str | None = Field(None, description="Description of the account")
    branch: str | None = Field(None, description="Branch of bank")
    number: str | None = Field(None, description="Account number")
    open_date: datetime.date = Field(..., serialization_alias="openDate", description="Account open date")
    close_date: datetime.date | None = Field(None, serialization_alias="closeDate", description="Account close date")
    type_id: uuid.UUID = Field(..., serialization_alias="typeId", description="Account type")
    currency_id: str = Field(..., serialization_alias='currencyId', description="Account currency")
