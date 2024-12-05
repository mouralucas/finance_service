from pydantic import BaseModel, ConfigDict, AliasGenerator, Field
from pydantic.alias_generators import to_snake
import uuid

class CreateCategoryExpenseRelationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_snake
    ))

    category_id: uuid.UUID = Field(..., description="Unique identifier for the category")
    expense_type_id: uuid.UUID = Field(..., description="Unique identifier for the expense type")