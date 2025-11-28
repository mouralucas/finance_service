from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.account import (
    CreateAccountTransactionRequest,
    GetAccountRequest,
    GetAccountTransactionRequest,
    GetBalanceRequest,
    UpdateAccountTransactionRequest,
)
from services.account import AccountService
from utils.graphql_input_validation import validate_graphql_input


@validate_graphql_input(GetAccountRequest)
async def get_accounts_resolver(_, info: GraphQLResolveInfo, params: GetAccountRequest):
    accounts = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_accounts(params=params)

    return accounts


@validate_graphql_input(GetAccountTransactionRequest)
async def get_account_transactions_resolver(
    _, info: GraphQLResolveInfo, params: GetAccountTransactionRequest
):
    transactions = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_transactions(params=params)

    return transactions


@validate_graphql_input(CreateAccountTransactionRequest)
async def create_account_transactions_resolver(
    _, info: GraphQLResolveInfo, transaction: CreateAccountTransactionRequest
):
    new_transaction = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).create_transaction(transaction=transaction)

    return new_transaction


@validate_graphql_input(UpdateAccountTransactionRequest)
async def update_account_transactions_resolver(
    _, info: GraphQLResolveInfo, transaction: UpdateAccountTransactionRequest
):
    new_transaction = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).update_transaction(transaction=transaction)

    return new_transaction


async def get_account_balance_resolver(_, info: GraphQLResolveInfo, params):
    params_ = GetBalanceRequest.model_validate(params)

    balance = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_balance(params=params_)

    return balance


def bind_account_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getAccounts", resolver=get_accounts_resolver)
    query.set_field(
        "getAccountTransactions", resolver=get_account_transactions_resolver
    )
    query.set_field("getAccountBalance", resolver=get_account_balance_resolver)

    mutation.set_field(
        "createAccountTransaction", resolver=create_account_transactions_resolver
    )

    mutation.set_field(
        "updateAccountTransaction", resolver=update_account_transactions_resolver
    )
