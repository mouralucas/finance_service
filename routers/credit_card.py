from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.credit_card import CreateCreditCardRequest, CreateCreditCardTransactionRequest, GetCreditCardRequest, CancelCreditCardRequest
from schemas.response.credit_card import CreateCreditCardResponse, CreateCreditCardTransactionResponse
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


@router.patch('/cancel', summary='Cancel a credit card', description='Cancel a credit card')
async def cancel_credit_card(credit_card: CancelCreditCardRequest,
                             session: AsyncSession = Depends(db_session),
                             user: RequiredUser = Security(get_user)):
    return await CreditCardService(session=session, user=user).cancel_credit_card(credit_card)


@router.get('', summary='Get credit cards', description='Get all credit cards for a user filter by params')
async def get_credit_cards(
        params: GetCreditCardRequest = Depends(),
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
):
    return await CreditCardService(session=session, user=user).get_credit_cards(params)


@router.post('/transaction',
             summary='Create a bill entry', description='Create a bill entry in selected credit card',
             status_code=status.HTTP_201_CREATED)
async def create_bill_entry(bill_entry: CreateCreditCardTransactionRequest,
                            session: AsyncSession = Depends(db_session),
                            user: RequiredUser = Security(get_user)) -> CreateCreditCardTransactionResponse:
    return await CreditCardService(session=session, user=user).create_bill_entry(bill_entry)
