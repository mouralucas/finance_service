from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.credit_card import CreateCreditCardRequest, CreateCreditCardTransactionRequest, GetCreditCardRequest, CancelCreditCardRequest, GetCreditCardBillRequest, GetCreditCardTransactionsRequest, GetInstallmentsDueDatesRequest
from schemas.response.credit_card import CreateCreditCardResponse, CreateCreditCardTransactionResponse, GetCreditCardTransactionResponse, GetCreditCardBillConsolidatedResponse, GetCreditCardBillByCardResponse, \
    GetInstallmentsDueDatesResponse
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


@router.get('/bill/consolidated',
            summary='Get credit card bill consolidated',
            description='Get creditcard bill consolidated by period. All credit cards used in the period.')
async def get_bill(
        params: GetCreditCardBillRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCreditCardBillConsolidatedResponse:
    return await CreditCardService(session, user).get_credit_card_bill_consolidated(params=params)


@router.get('/bill/card', )
async def get_bill(
        params: GetCreditCardBillRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCreditCardBillByCardResponse:
    return await CreditCardService(session, user).get_credit_card_bill_by_card(params=params)
