from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.credit_card import CreditCardSchema


class CreateCreditCardResponse(SuccessResponseBase):
    credit_card: CreditCardSchema = Field(..., serialization_alias='creditCard')


class GetCreditCardResponse(SuccessResponseBase):
    quantity: int = Field(..., alias='quantity', description='The number of credit cards fetched')
    credit_cards: list[CreditCardSchema] = Field(..., alias='creditCard', description='The list of the credit cards of the user')
