from pydantic import Field, BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel
from rolf_common.schemas import SuccessResponseBase

from schemas.credit_card import CreditCardSchema, CreditCardTransactionSchema, CreditCardBillSchema, CreditCardBillSchemaByCard, InstallmentsDueDates


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
    quantity: int = Field(..., serialization_alias='quantity', description='The number of credit cards transactions')
    transactions: list[CreditCardTransactionSchema] = Field(..., serialization_alias='transactions', description='The list of the credit transactions')


class GetInstallmentsDueDatesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))
    due_dates: list[InstallmentsDueDates] = Field(..., description='The list of installments and its due dates')


class GetCreditCardBillConsolidatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(serialization_alias=to_camel))

    average: float | None = Field(None, description='The average credit card bill')
    goal: float | None = Field(None, description='The goal credit card bill')
    period_range: list[int] | None = Field(None, description='The range of available bill periods')
    bill: list[CreditCardBillSchema] = Field(..., description='The list bill by period')


class GetCreditCardBillByCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(serialization_alias=to_camel))

    cards: list[str] | None = Field(None, description='The list of available cards')
    bill: list[CreditCardBillSchemaByCard] = Field(..., description='The list bill by period')
