from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import db_session
from schemas.request.investment import CreateInvestmentRequest, GetInvestmentRequest, CreateStatementRequest, GetStatementRequest, LiquidateInvestmentRequest
from schemas.response.investment import CreateInvestmentResponse, GetInvestmentResponse, CreateStatementResponse, GetStatementResponse, LiquidateInvestmentResponse
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


@router.get('', summary='Get investments', description='Get investment base on filters')
async def get_investments(
        params: GetInvestmentRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> GetInvestmentResponse:
    pass


@router.post('/liquidate', summary='Liquidate an investment', description='Liquidate an investment')
async def liquidate(
        investment: LiquidateInvestmentRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> LiquidateInvestmentResponse:
    pass


@router.post('/statement', status_code=status.HTTP_201_CREATED,
             summary='Create a statement for an investment', description='Create a statement for an investment')
async def create_statement(
        statement: CreateStatementRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> CreateStatementResponse:
    pass


@router.get('/statement', summary='Get statement for an investment', description='Get statement base on filters')
async def get_statement(
        params: GetStatementRequest,
        session: AsyncSession = Depends(db_session),
        user: RequiredUser = Security(get_user)
) -> GetStatementResponse:
    pass
