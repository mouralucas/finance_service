from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.account import AccountSchema, AccountTransactionSchema, BalanceSchema


class CreateAccountResponse(SuccessResponseBase):
    account: AccountSchema = Field(..., serialization_alias='account', description='The new account created by the user')


class CloseAccountResponse(CreateAccountResponse):
    pass


class GetAccountResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of accounts fetched')
    accounts: list[AccountSchema] = Field(..., serialization_alias='accounts', description='The accounts of the user')


class CreateAccountTransactionResponse(SuccessResponseBase):
    transaction: AccountTransactionSchema = Field(..., serialization_alias='transaction', description='The entry statement created by the user')


class CreateBalanceResponse(SuccessResponseBase):
    accountNickname: str = Field(..., description='The account nickname')
    periods_saved: int = Field(..., serialization_alias='periodsSaved', description='The number of periods saved')


class GetBalanceResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of periods fetched for the account')
    account_name: str = Field(..., serialization_alias='accountName', description='The account name')
    balance: list[BalanceSchema] = Field(..., serialization_alias='balance', description='The balance for the account in selected period range')
