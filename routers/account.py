from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from models.account import Account
from schemas.request.account import CreateAccountRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse

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
    return CreateAccountResponse()


@router.get('', summary='List all accounts', description='Get user accounts base on filters chosen')
async def get_accounts(
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> GetAccountResponse:
    return GetAccountResponse()
