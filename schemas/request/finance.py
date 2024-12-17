from pydantic import BaseModel, Field, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel


class GetSummaryRequest(BaseModel):
    period: int | None = Field(None, description='The period of the summary')


class GetTaxFeeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        alias=to_camel
    ))

    country_id: str = Field('BR', description='The id of the country for the tax or fee')
    type: str = Field(..., description='Whether is tax or fee to fetch')
