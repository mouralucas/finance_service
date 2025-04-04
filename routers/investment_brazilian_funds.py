from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from uvicorn.config import resolve_reload_patterns

from backend.database import get_session
from schemas.request.investment import GetInvestmentRequest
from schemas.request.investment_brazilian_funds import CreateBrazilianFundInvestmentStatementRequest, CreateBrazilianFundInvestmentRequest
from schemas.response.investment import GetInvestmentResponse
from schemas.response.investment_brazilian_funds import CreateBrazilianFundInvestmentResponse, CreateBrazilianFundInvestmentStatementResponse
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
        # TODO: adjust schemas
        params: GetInvestmentRequest = Depends(),
        session: AsyncSession = Depends(get_session),
        user: RequiredUser = Security(get_user)
) -> GetInvestmentResponse:
    return await InvestmentBrazilianFundService(session=session, user=user).get_brazilian_fund_investments()


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
