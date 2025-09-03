import uuid

from pydantic import BaseModel, Field


class CreateIndexerSeriesRequest(BaseModel):
    indexer_code: int = Field(
        ..., alias="indexerCode", description="The code of the indexer in SGS system"
    )
    indexer_id: uuid.UUID = Field(
        ..., alias="indexerId", description="The unique identifier for the indexer"
    )
    periodicity_id: uuid.UUID = Field(
        ...,
        alias="periodicityId",
        description="The unique identifier for the periodicity",
    )
