from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.credit_card import CreateCreditCardRequest
from schemas.response.credit_card import CreateCreditCardResponse
from services.credit_card import CreditCardService

router = APIRouter(prefix="/creditcard", tags=['Credit cards'])


@router.post('',
             summary='Create a credit card', description='Create a new credit card for the user',
             status_code=status.HTTP_201_CREATED)
async def create_credit_card(
        credit_card: CreateCreditCardRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> CreateCreditCardResponse:
    return await CreditCardService(session=session, user=user).create_credit_card(credit_card)
