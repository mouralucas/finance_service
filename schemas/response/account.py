from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.account import AccountSchema, StatementSchema, BalanceSchema


class CreateAccountResponse(SuccessResponseBase):
    account: AccountSchema = Field(..., serialization_alias='account', description='The new account created by the user')


class CloseAccountResponse(CreateAccountResponse):
    pass


class GetAccountResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of accounts fetched')
    accounts: list[AccountSchema] = Field(..., serialization_alias='accounts', description='The accounts of the user')


class CreateStatementResponse(SuccessResponseBase):
    account_statement_entry: StatementSchema = Field(..., serialization_alias='accountStatementEntry', description='The entry statement created by the user')


class CreateBalanceResponse(SuccessResponseBase):
    accountNickname: str = Field(..., description='The account nickname')
    periods_saved: int = Field(..., serialization_alias='periodsSaved', description='The number of periods saved')

class GetBalanceResponse(SuccessResponseBase):
    balance: list[BalanceSchema] = Field(..., serialization_alias='balance', description='The balance for the account in selected period range')
