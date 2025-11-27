from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from schemas.account import (
    AccountSchema,
    AccountTransactionSchema,
)


class CreateAccountResponse(BaseModel):
    account: AccountSchema = Field(
        ...,
        serialization_alias="account",
        description="The new account created by the user",
    )


class CloseAccountResponse(CreateAccountResponse):
    pass


class CreateAccountTransactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    transaction: AccountTransactionSchema = Field(
        ...,
        description="The entry statement created by the user",
    )


class UpdateTransactionResponse(CreateAccountTransactionResponse):
    pass


class CreateBalanceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    account_nickname: str = Field(..., description="The account nickname")
    periods_saved: int = Field(..., description="The number of periods saved")
