from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.credit_card import CreditCardSchema, BillEntrySchema


class CreateCreditCardResponse(SuccessResponseBase):
    credit_card: CreditCardSchema = Field(..., serialization_alias='creditCard')


class GetCreditCardResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of credit cards fetched')
    credit_cards: list[CreditCardSchema] = Field(..., serialization_alias='creditCards', description='The list of the credit cards of the user')


class CreateBillEntryResponse(SuccessResponseBase):
    bill_entry: list[BillEntrySchema] = Field(..., serialization_alias='billEntry', description='The entry (or entries) created. If installments transactions will return more than one entry')
