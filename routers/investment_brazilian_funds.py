from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.investment import GetBrazilianFundInvestmentsRequest
from schemas.request.investment_brazilian_funds import (
    CreateBrazilianFundInvestmentRequest,
    CreateBrazilianFundInvestmentStatementRequest,
    GetBrazilianFundInvestmentStatementRequest,
)
from schemas.response.investment_brazilian_funds import (
    CreateBrazilianFundInvestmentResponse,
    CreateBrazilianFundInvestmentStatementResponse,
    GetBrazilianFundInvestmentsResponse,
    GetBrazilianFundInvestmentStatementResponse,
)
from services.investment_brazilian_fund import InvestmentBrazilianFundService

router = APIRouter(prefix="/investment/funds/br", tags=['Investments'])


@router.post('',
             summary='Create a brazilian funds investment',
             status_code=status.HTTP_201_CREATED
             )
async def create_funds_br_investment(
        investment: CreateBrazilianFundInvestmentRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateBrazilianFundInvestmentResponse:
    return await InvestmentBrazilianFundService(session=session, user=user).create_brazilian_fund_investment(investment=investment)


@router.get('')
async def get_funds_br_investments(
        params: GetBrazilianFundInvestmentsRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetBrazilianFundInvestmentsResponse:
    return await InvestmentBrazilianFundService(session=session, user=user).get_brazilian_fund_investments(params=params)


@router.post('/statement',
             summary='Create a brazilian funds investment statement',
             status_code=status.HTTP_201_CREATED
             )
async def create_funds_br_investment_statement(
        statement: CreateBrazilianFundInvestmentStatementRequest,
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> CreateBrazilianFundInvestmentStatementResponse:
    return await InvestmentBrazilianFundService(session=session, user=user).create_brazilian_fund_investment_statement(statement=statement)



@router.get('/statement', summary='Get the statements for a brazilian fund investment')
async def get_funds_br_investment_statement(
        params: GetBrazilianFundInvestmentStatementRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetBrazilianFundInvestmentStatementResponse:
    return await InvestmentBrazilianFundService(session=session, user=user).get_brazilian_fund_statements(params=params)
