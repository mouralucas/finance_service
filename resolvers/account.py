from ariadne import MutationType, QueryType

from schemas.request.account import (
    CreateAccountTransactionRequest,
    GetAccountRequest,
    GetAccountTransactionRequest,
    GetBalanceRequest,
    UpdateAccountTransactionRequest,
)
from services.account import AccountService


async def get_accounts_resolver(_, info, params):
    params_ = GetAccountRequest.model_validate(params)

    accounts = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_accounts(params=params_)

    return accounts.model_dump(by_alias=True)


async def get_account_transactions(_, info, params):
    params = GetAccountTransactionRequest.model_validate(params)
    
    transactions = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_transactions(params=params)
    
    return transactions.model_dump(by_alias=True)


async def create_account_transactions_resolver(_, info, transaction):
    transaction_ = CreateAccountTransactionRequest.model_validate(transaction)

    new_transaction = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).create_transaction(transaction=transaction_)

    return new_transaction.model_dump(by_alias=True)


async def update_account_transactions_resolver(_, info, transaction):
    transaction_ = UpdateAccountTransactionRequest.model_validate(transaction)

    new_transaction = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).update_transaction(transaction=transaction_)

    return new_transaction.model_dump(by_alias=True)


async def get_account_balance_resolver(_, info, params):
    params_ = GetBalanceRequest.model_validate(params)

    balance = await AccountService(
        session=info.context["session"], user=info.context["user"]
    ).get_balance(params=params_)

    return balance.model_dump(by_alias=True)


def bind_account_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getAccounts", resolver=get_accounts_resolver)
    query.set_field("getAccountTransactions", resolver=get_account_transactions)
    query.set_field("getAccountBalance", resolver=get_account_balance_resolver)

    mutation.set_field(
        "createAccountTransaction", resolver=create_account_transactions_resolver
    )

    mutation.set_field(
        "updateAccountTransaction", resolver=update_account_transactions_resolver
    )
