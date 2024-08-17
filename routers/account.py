from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateStatementRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse
from services.account import AccountService

router = APIRouter(prefix="/account", tags=['Account'])


@router.post('',
             summary='Create an account',
             description='Create a new bank account for the user',
             status_code=status.HTTP_201_CREATED)
async def create_account(
        account: CreateAccountRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> CreateAccountResponse:
    return await AccountService(session=session, user=user).create_account(account=account)


@router.get('', summary='List all accounts', description='Get user accounts base on filters chosen')
async def get_accounts(
        params: GetAccountRequest = Depends(),
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> GetAccountResponse:
    return await AccountService(session=session, user=user).get_accounts(params=params)


@router.post('/statement', status_code=status.HTTP_201_CREATED,
             summary='Create a statement entry', description='Create a statement entry for an account')
async def create_statement(statement_entry: CreateStatementRequest,
                           session: AsyncSession = Depends(db_session),
                           user: RequiredUser = Security(get_user)):
    return await AccountService(session=session, user=user).create_statement(statement_entry=statement_entry)
