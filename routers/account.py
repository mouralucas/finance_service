from fastapi import APIRouter, Depends, Security

# from rolf_common.backend.logger import logger
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.account import (
    CloseAccountRequest,
    CreateAccountRequest,
    CreateBalanceRequest,
    UpdateAccountTransactionRequest,
)
from schemas.response.account import (
    CloseAccountResponse,
    CreateAccountResponse,
)
from services.account import AccountService

router = APIRouter(prefix="/account", tags=["Account"])


@router.post(
    "",
    summary="Create an account",
    description="Create a new bank account for the user",
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    account: CreateAccountRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> CreateAccountResponse:
    return await AccountService(session=session, user=user).create_account(
        account=account
    )


@router.patch(
    "/close",
    summary="Close an account",
    description="Close an account and its relations (credit cards)",
)
async def close_account(
    account: CloseAccountRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> CloseAccountResponse:
    return await AccountService(session=session, user=user).close_account(
        account=account
    )


@router.patch("/transaction")
async def update_transaction(
    transaction: UpdateAccountTransactionRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
):
    return await AccountService(session=session, user=user).update_transaction(
        transaction=transaction
    )
