from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateAccountTransactionRequest, CloseAccountRequest, CreateBalanceRequest, GetBalanceRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse, CloseAccountResponse
from services.account import AccountService

router = APIRouter(prefix="/account", tags=['Account'])


@router.post('',
             summary='Create an account',
             description='Create a new bank account for the user',
             status_code=status.HTTP_201_CREATED)
async def create(
        account: CreateAccountRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> CreateAccountResponse:
    return await AccountService(session=session, user=user).create_account(account=account)


@router.patch('/close', summary='Close an account', description='Close an account and its relations (credit cards)')
async def close(
        account: CloseAccountRequest,
        session: AsyncSession = Depends(db_session),
        # user: RequiredUser = Security(get_user)
) -> CloseAccountResponse:
    user = RequiredUser(
        user_id='adf52a1e-7a19-11ed-a1eb-0242ac120002',
    )
    return await AccountService(session=session, user=user).close_account(account=account)


@router.get('', summary='List all accounts', description='Get user accounts base on filters chosen')
async def get(
        params: GetAccountRequest = Depends(),
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> GetAccountResponse:
    return await AccountService(session=session, user=user).get_accounts(params=params)


@router.post('/statement', status_code=status.HTTP_201_CREATED,
             summary='Create a statement entry', description='Create a statement entry for an account')
async def create_statement(statement_entry: CreateAccountTransactionRequest,
                           session: AsyncSession = Depends(db_session),
                           user: RequiredUser = Security(get_user)):
    return await AccountService(session=session, user=user).create_statement(statement_entry=statement_entry)


@router.post('/balance', summary='Generate the balance for the account')
async def create_balance(
        params: CreateBalanceRequest,
        session: AsyncSession = Depends(db_session),
        # user: RequiredUser = Security(get_user)
):
    user = RequiredUser(user_id = 'adf52a1e-7a19-11ed-a1eb-0242ac120002')
    return await AccountService(session=session, user=user).create_balance(params=params)


@router.get('/balance', summary='Get the balance', description='Get the balance for a account in the specified period range. If no period is specified, '
                                                               'the range is from the first period with transaction to close account or current period')
async def get_balance(
        params: GetBalanceRequest = Depends(),
        session: AsyncSession = Depends(db_session),
        # user: RequiredUser = Security(get_user)
):
    user = RequiredUser(user_id='adf52a1e-7a19-11ed-a1eb-0242ac120002')
    return await AccountService(session, user).get_balance(params=params)
