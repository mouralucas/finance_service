import uuid

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field, ConfigDict


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., serialization_alias="accountId", description="Unique account ID")
    # other fields
