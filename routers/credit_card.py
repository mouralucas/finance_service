from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.credit_card import (
    CancelCreditCardRequest,
    CreateCreditCardRequest,
    CreateCreditCardTransactionRequest,
    GetCreditCardBillRequest,
    GetCreditCardRequest,
    GetCreditCardTransactionsRequest,
    GetInstallmentsDueDatesRequest,
)
from schemas.response.credit_card import (
    CreateCreditCardResponse,
    CreateCreditCardTransactionResponse,
    GetCreditCardBillConsolidatedResponse,
    GetCreditCardBillHistoryResponse,
    GetCreditCardTransactionResponse,
    GetInstallmentsDueDatesResponse,
)
from services.credit_card import CreditCardService

router = APIRouter(prefix="/creditcard", tags=['Credit cards'])


@router.post('',
             summary='Create a credit card', description='Create a new credit card for the user',
             status_code=status.HTTP_201_CREATED)
async def create_credit_card(
        credit_card: CreateCreditCardRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateCreditCardResponse:
    return await CreditCardService(session=session, user=user).create_credit_card(credit_card)


@router.patch('/cancel', summary='Cancel a credit card', description='Cancel a credit card')
async def cancel_credit_card(
        credit_card: CancelCreditCardRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await CreditCardService(session=session, user=user).cancel_credit_card(credit_card)


@router.get('', summary='Get credit cards', description='Get all credit cards for a user filter by params')
async def get_credit_cards(
        params: GetCreditCardRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await CreditCardService(session=session, user=user).get_credit_cards(params)


@router.post('/transaction',
             summary='Create a transaction', description='Create a transaction for the selected credit card',
             status_code=status.HTTP_201_CREATED)
async def create_transaction(
        transaction: CreateCreditCardTransactionRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateCreditCardTransactionResponse:
    return await CreditCardService(session=session, user=user).create_transaction(transaction)


@router.patch('/transaction')
async def update_transaction(
        transaction: CreateCreditCardTransactionRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateCreditCardTransactionResponse:
    pass


@router.get('/transaction',
            summary='Get credit card transactions',
            description='Get all credit card transactions for a user filter by params')
async def get_transactions(
        params: GetCreditCardTransactionsRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCreditCardTransactionResponse:
    return await CreditCardService(session=session, user=user).get_transactions(params)


@router.get('/transaction/installment/due-date', summary='Get due date', description='Get due date for every installment')
async def get_installments_due_dates(
        params: GetInstallmentsDueDatesRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetInstallmentsDueDatesResponse:
    return await CreditCardService(session=session, user=user).get_installments_due_date(params=params)


@router.get('/bill/evolution',
            summary='Get credit card bill evolution',
            description='Get creditcard bill evolution in the period range.')
async def get_bill(
        params: GetCreditCardBillRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCreditCardBillConsolidatedResponse:
    return await CreditCardService(session, user).get_credit_card_bill_evolution(params=params)


@router.get('/bill/history', summary='Get credit card bill', description='Get credit card bill for all cards available for the period range')
async def get_bill_history(
        params: GetCreditCardBillRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCreditCardBillHistoryResponse:
    return await CreditCardService(session, user).get_credit_card_bill_history(params=params)
