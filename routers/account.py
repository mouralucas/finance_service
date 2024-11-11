from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateAccountTransactionRequest, CloseAccountRequest, CreateBalanceRequest, GetBalanceRequest, UpdateAccountTransactionRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse, CloseAccountResponse, GetAccountTransactionResponse, CreateAccountTransactionResponse
from services.account import AccountService

router = APIRouter(prefix="/account", tags=['Account'])


@router.post('',
             summary='Create an account',
             description='Create a new bank account for the user',
             status_code=status.HTTP_201_CREATED)
async def create_account(
        account: CreateAccountRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateAccountResponse:
    return await AccountService(session=session, user=user).create_account(account=account)


@router.get('', summary='List all accounts', description='Get user accounts base on filters chosen')
async def get_account(
        params: GetAccountRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetAccountResponse:
    return await AccountService(session=session, user=user).get_accounts(params=params)


@router.patch('/close', summary='Close an account', description='Close an account and its relations (credit cards)')
async def close_account(
        account: CloseAccountRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CloseAccountResponse:
    return await AccountService(session=session, user=user).close_account(account=account)


@router.post('/transaction', status_code=status.HTTP_201_CREATED,
             summary='Create a transaction', description='Create a transaction for an account')
async def create_transaction(transaction: CreateAccountTransactionRequest,
                             session: AsyncSession = Depends(get_session),
                             user: RequiredUser = Security(get_user)) -> CreateAccountTransactionResponse:
    return await AccountService(session=session, user=user).create_transaction(statement_entry=transaction)


@router.patch('/transaction')
async def update_transaction(
        transaction: UpdateAccountTransactionRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    original_values = transaction.model_dump()
    setted_values = transaction.model_dump(exclude_unset=True)
    return


@router.get('/transaction',  summary='Get account transactions')
async def get_transactions(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetAccountTransactionResponse:
    return await AccountService(session=session, user=user).get_transactions()



@router.post('/balance', summary='Generate the balance for the account', status_code=status.HTTP_201_CREATED)
async def create_balance(
        params: CreateBalanceRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await AccountService(session=session, user=user).create_balance(params=params)


@router.get('/balance', summary='Get the balance', description='Get the balance for a account in the specified period range. If no period is specified, '
                                                               'the range is from the first period with transaction to close account or current period')
async def get_balance(
        params: GetBalanceRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await AccountService(session, user).get_balance(params=params)
