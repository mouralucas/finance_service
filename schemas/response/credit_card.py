from typing import Any

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from schemas.credit_card import (
    CreditCardBillHistorySchema,
    CreditCardBillSchema,
    CreditCardSchema,
    CreditCardTransactionSchema,
    InstallmentsDueDates,
)


class CreateCreditCardResponse(BaseModel):
    credit_card: CreditCardSchema = Field(..., serialization_alias="creditCard")


class CancelCreditCardResponse(CreateCreditCardResponse):
    pass


class GetCreditCardResponse(BaseModel):
    quantity: int = Field(
        ...,
        serialization_alias="quantity",
        description="The number of credit cards fetched",
    )
    credit_cards: list[CreditCardSchema] = Field(
        ...,
        serialization_alias="creditCards",
        description="The list of the credit cards of the user",
    )


class CreateCreditCardTransactionResponse(BaseModel):
    transaction: list[CreditCardTransactionSchema] = Field(
        ...,
        serialization_alias="transaction",
        description="The transaction(s) created. If installments transaction, \
                        will return more than one transaction",
    )


class GetCreditCardTransactionResponse(BaseModel):
    quantity: int = Field(
        ...,
        serialization_alias="quantity",
        description="The number of credit cards transactions",
    )
    transactions: list[CreditCardTransactionSchema] = Field(
        ...,
        serialization_alias="transactions",
        description="The list of the credit transactions",
    )


class GetInstallmentsDueDatesResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )
    due_dates: list[InstallmentsDueDates] = Field(
        ..., description="The list of installments and its due dates"
    )


class GetCreditCardBillConsolidatedResponse(BaseModel):
    # add configuration to allow extra fields not mapped to the model
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        extra="allow",
    )

    average: float | None = Field(None, description="The average credit card bill")
    goal: float | None = Field(None, description="The goal credit card bill")
    bill: list[CreditCardBillSchema] | None = Field(
        ..., description="The list of consolidated bill by period"
    )
    bill_stacked: list[dict[str, Any]] = Field(
        ..., description="The list of bill stacked by card/period"
    )
    series: list[str] = Field(
        ..., description="The list of available series for the bill stacked"
    )


class GetCreditCardBillHistoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    credit_card_bill_history: list[CreditCardBillHistorySchema] = Field(
        ..., description="The list bill by period"
    )
