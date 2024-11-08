from pydantic import BaseModel

from schemas.core import CategorySchema, CurrencySchema


class GetCategoryResponse(BaseModel):
    categories: list[CategorySchema]
