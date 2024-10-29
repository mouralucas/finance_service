from pydantic import BaseModel, Field


class GetSummaryRequest(BaseModel):
    period: int | None = Field(None, description='The period of the summary')