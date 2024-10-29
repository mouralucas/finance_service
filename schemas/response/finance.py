from pydantic import Field
from rolf_common.schemas import SuccessResponseBase


class GetSummaryResponse(SuccessResponseBase):
    total_invested: float = Field(..., serialization_alias='totalInvested', description='The total amount invested in the period')
    total_credit_card: float = Field(..., serialization_alias='totalCreditCard', description='The total amount spent in credit card in the period')
    incoming: float = Field(..., serialization_alias='incoming', description='The total amount incoming in the period')
    outgoing: float = Field(..., serialization_alias='outgoing', description='The total amount outgoing in the period')
    balance: float = Field(..., serialization_alias='balance', description='The total amount in the period')