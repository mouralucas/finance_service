from pydantic import Field
from rolf_common.schemas import SuccessResponseBase

from schemas.account import AccountSchema


class CreateAccountResponse(SuccessResponseBase):
    account: AccountSchema = Field(..., alias='account', description='The new account created by the user')


class GetAccountResponse(SuccessResponseBase):
    quantity: int = Field(..., alias='quantity', description='The number of accounts fetched')
    account: list[AccountSchema] = Field(..., alias='account', description='The accounts of the user')
