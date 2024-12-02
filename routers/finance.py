from fastapi import APIRouter
from fastapi import Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from schemas.request.finance import GetSummaryRequest
from schemas.response.finance import GetCurrencyResponse, GetBankResponse, GetIndexerTypeResponse, GetIndexerResponse
from services.finance import FinanceService

router = APIRouter(prefix="/finance", tags=['Finance'])


@router.get('/currency', summary='Get currencies')
async def get_currencies(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCurrencyResponse:
    return await FinanceService(session=session, user=user).get_currencies()

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


@router.get('/summary')
async def get_summary(
        params: GetSummaryRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await FinanceService(session=session, user=user).get_summary(params=params)
