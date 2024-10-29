from fastapi import APIRouter
from fastapi import Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db_session
from schemas.request.finance import GetSummaryRequest
from services.finance import FinanceService

router = APIRouter(prefix="/finance", tags=['Finance'])


@router.get('/summary')
async def get_summary(
        params: GetSummaryRequest = Depends(),
        session: AsyncSession = Depends(db_session),
        # user: RequiredUser = Security(get_user)
):
    user = RequiredUser(user_id='adf52a1e-7a19-11ed-a1eb-0242ac120002')
    response = await FinanceService(session=session, user=user).get_summary(params=params)
