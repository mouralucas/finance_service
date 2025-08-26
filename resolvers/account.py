

from ariadne import MutationType, QueryType
from schemas.request.account import GetAccountRequest
from schemas.response.account import GetAccountResponse
from services.account import AccountService


async def get_accounts_resolver(_, info, params):
    params_ = GetAccountRequest.model_validate(params)

    accounts = await AccountService(session=info.context['session'], user=info.context['user']).get_accounts(params=params_)

    return accounts.model_dump(by_alias=True)


def bind_account_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getAccounts", resolver=get_accounts_resolver)