import uuid

from pydantic import BaseModel, Field


class SyncIndexerSeriesRequest(BaseModel):
    indexer_id: uuid.UUID = Field(
        ..., alias="indexerId", description="The unique identifier for the indexer"
    )
    periodicity_id: uuid.UUID = Field(
        ...,
        alias="periodicityId",
        description="The unique identifier for the periodicity",
    )
