import uuid
from datetime import date

from pydantic import Field

from schemas.request.investment import CreateInvestmentBaseRequest


class CreateFixedIncomeInvestmentBrazilRequest(CreateInvestmentBaseRequest):
    issue_date: date = Field(..., description='The date the investment was issued')
    transaction_date: date = Field(..., description='The date the investment was transmitted')
    maturity_date: date = Field(..., description='The date the investment will due')
    grace_period_date: date = Field(..., description='The date the investment can be liquidated')
    contracted_rate: str = Field(..., description='The rate of the investment')
    indexer_type_id: uuid.UUID = Field(..., description='The type of the index for the investment')
    indexer_id: uuid.UUID = Field(..., description='The id of the investment index')
