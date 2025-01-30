from alembic.util import status
from fastapi import APIRouter
from fastapi import Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from schemas.request.finance import GetSummaryRequest, GetTaxFeeRequest, GetBankRequest
from schemas.response.finance import GetCurrencyResponse, GetBankResponse, GetIndexerTypeResponse, GetIndexerResponse, GetLiquidityResponse, GetExpensesByCategoryResponse, GetTaxFeeResponse
from services.finance import FinanceService
from starlette import status

router = APIRouter(prefix="/finance", tags=['Finance'])


@router.get('/currency', summary='Get currencies')
async def get_currencies(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCurrencyResponse:
    return await FinanceService(session=session, user=user).get_currencies()


@router.post('/bank', summary='Create a new bank', status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_bank(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user, scopes=['admin'])
):
    pass

@router.get('/bank', summary='Get banks')
async def get_banks(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetBankResponse:
    return await FinanceService(session, user).get_banks()


@router.get('/indexer-type', summary='Get indexer type')
async def get_indexer_type(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetIndexerTypeResponse:
    return await FinanceService(session, user).get_indexer_types()


@router.get('/indexer', summary='Get indexers')
async def get_indexer_type(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetIndexerResponse:
    return await FinanceService(session, user).get_indexers()


@router.get('/liquidity', summary='Gey liquidity options')
async def get_liquidity(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetLiquidityResponse:
    return await FinanceService(session, user).get_liquidity()


@router.get('/tax-fee', summary='Get taxes and fees')
async def get_tax_fee(
        params: GetTaxFeeRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetTaxFeeResponse:
    return await FinanceService(session=session, user=user).get_tax_fee(params=params)


# Dashboard endpoints
@router.get('/summary')
async def get_summary(
        params: GetSummaryRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await FinanceService(session=session, user=user).get_summary(params=params)


@router.get('/expenses/category')
async def get_expenses_by_category(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetExpensesByCategoryResponse:
    return await FinanceService(session=session, user=user).get_expenses_by_category()
