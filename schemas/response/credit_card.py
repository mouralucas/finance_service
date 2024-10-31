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


class GetCreditCardTransactionResponse(SuccessResponseBase):
    transactions: list[CreditCardTransactionSchema] = Field(..., serialization_alias='transactions', description='The list of the credit transactions')


class GetCreditCardBillResponse(SuccessResponseBase):
    # TODO: separate response for aggregated and creds
    average: float | None = Field(None, description='The average credit card bill')
    goal: float | None = Field(None, description='The goal credit card bill')
    period_range: list[int] | None = Field(None, serialization_alias='periodRange', description='The range of available bill periods')
    cards: list[str] | None = Field(None, description='The list of available cards')
    bill: list[dict] = Field(..., description='The list bill by period')
