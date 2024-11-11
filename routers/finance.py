from fastapi import APIRouter
from fastapi import Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from schemas.request.finance import GetSummaryRequest
from schemas.response.finance import GetCurrencyResponse
from services.finance import FinanceService

router = APIRouter(prefix="/finance", tags=['Finance'])


@router.get('/currency', summary='Get currencies')
async def get_currencies(
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetCurrencyResponse:
    return await FinanceService(session=session, user=user).get_currencies()


@router.get('/summary')
async def get_summary(
        params: GetSummaryRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
):
    return await FinanceService(session=session, user=user).get_summary(params=params)
