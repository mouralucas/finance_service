from pydantic import BaseModel, Field

from schemas.core import CategorySchema, CurrencySchema, CountrySchema


class GetCategoryResponse(BaseModel):
    quantity: int = Field(..., description='How many categories are available in request')
    categories: list[CategorySchema] = Field(..., description='The list of available categories')


class GetCountryResponse(BaseModel):
    quantity: int = Field(..., description='How many countries are available in request')
    countries: list[CountrySchema] = Field(..., description='The list of available countries')
