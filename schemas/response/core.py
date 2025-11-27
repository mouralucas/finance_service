from pydantic import BaseModel, Field

from schemas.core import CountrySchema


class GetCountryResponse(BaseModel):
    quantity: int = Field(
        ..., description="How many countries are available in request"
    )
    countries: list[CountrySchema] = Field(
        ..., description="The list of available countries"
    )
