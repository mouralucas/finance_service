from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.investment import CreateInvestmentRequest
from schemas.response.investment import CreateInvestmentResponse
from services.investment import InvestmentService

router = APIRouter(prefix="/investment", tags=['Investments'])


@router.post('', status_code=status.HTTP_201_CREATED,
             summary='Create an investment', description='Create an new investment for the user')
async def create_investment(
        investment: CreateInvestmentRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> CreateInvestmentResponse:
    response = await InvestmentService(session=session, user=user).create_investment(investment)

    return response
