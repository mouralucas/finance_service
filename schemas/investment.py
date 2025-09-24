from pydantic import BaseModel, ConfigDict, AliasGenerator, Field
from pydantic.alias_generators import to_camel

from schemas.core import ChartSeriesSchemaV2

class InvestmentPerformance(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    x_label: str = Field(...)
    data: list[ChartSeriesSchemaV2] = Field(...)