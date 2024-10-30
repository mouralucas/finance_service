from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.credit_card import CreditCardSchema, CreditCardTransactionSchema


class CreateCreditCardResponse(SuccessResponseBase):
    credit_card: CreditCardSchema = Field(..., serialization_alias='creditCard')


class CancelCreditCardResponse(CreateCreditCardResponse):
    pass


class GetCreditCardResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of credit cards fetched')
    credit_cards: list[CreditCardSchema] = Field(..., serialization_alias='creditCards', description='The list of the credit cards of the user')


class CreateCreditCardTransactionResponse(SuccessResponseBase):
    transaction: list[CreditCardTransactionSchema] = Field(..., serialization_alias='transaction', description='The transaction(s) created. If installments transaction, will return more than one transaction')


class GetCreditCardBillResponse(SuccessResponseBase):
    average: float = Field(..., description='The average credit card bill')
    goal: float = Field(..., description='The goal credit card bill')
    period_range: list[int] = Field(..., serialization_alias='periodRange', description='The range of available bill periods')
    bill: list[dict] = Field(..., description='The list bill by period')


