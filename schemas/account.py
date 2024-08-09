import uuid

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field


class AccountSchema(BaseModel):
    id: uuid.UUID = Field(..., alias="accountId", description="Unique account ID")
    # other fields