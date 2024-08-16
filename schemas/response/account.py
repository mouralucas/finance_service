from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.account import AccountSchema


class CreateAccountResponse(SuccessResponseBase):
    account: AccountSchema = Field(..., serialization_alias='account', description='The new account created by the user')


class GetAccountResponse(SuccessResponseBase):
    quantity: int = Field(..., serialization_alias='quantity', description='The number of accounts fetched')
    accounts: list[AccountSchema] = Field(..., serialization_alias='accounts', description='The accounts of the user')
