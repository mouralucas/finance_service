from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.finance import (
    CreateBrazilianFundRequest,
    GetCurrencyAveragePrice,
    GetSummaryRequest,
    GetTaxFeeRequest,
)
from schemas.response.finance import (
    CreateBrazilianFundResponse,
    GetBankResponse,
    GetBrazilianFundsResponse,
    GetCurrencyResponse,
    GetExpensesByCategoryResponse,
    GetIndexerResponse,
    GetIndexerTypeResponse,
    GetLiquidityResponse,
    GetTaxFeeResponse,
)
from services.finance import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.get("/currency", summary="Get currencies")
async def get_currencies(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetCurrencyResponse:
    return await FinanceService(session=session, user=user).get_currencies()


@router.get("/currency/average-price")
async def get_currency_cost_average(
    params: GetCurrencyAveragePrice = Depends(),
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
):
    pass


@router.post(
    "/bank", summary="Create a new bank", status_code=status.HTTP_501_NOT_IMPLEMENTED
)
async def create_bank(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user, scopes=["admin"]),
):
    pass


@router.get("/bank", summary="Get banks")
async def get_banks(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetBankResponse:
    return await FinanceService(session, user).get_banks()


@router.get("/indexer-type", summary="Get indexer type")
async def get_indexer_type(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetIndexerTypeResponse:
    return await FinanceService(session, user).get_indexer_types()


@router.get("/indexer", summary="Get indexers")
async def get_indexer(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetIndexerResponse:
    return await FinanceService(session, user).get_indexers()


@router.get("/liquidity", summary="Gey liquidity options")
async def get_liquidity(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetLiquidityResponse:
    return await FinanceService(session, user).get_liquidity()


@router.get("/tax-fee", summary="Get taxes and fees")
async def get_tax_fee(
    params: GetTaxFeeRequest = Depends(),
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetTaxFeeResponse:
    return await FinanceService(session=session, user=user).get_tax_fee(params=params)


# Dashboard endpoints
@router.get("/summary")
async def get_summary(
    params: GetSummaryRequest = Depends(),
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
):
    return await FinanceService(session=session, user=user).get_summary(params=params)


@router.get("/expenses/category")
async def get_expenses_by_category(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetExpensesByCategoryResponse:
    return await FinanceService(session=session, user=user).get_expenses_by_category()


@router.post(
    "/funds/br",
    summary="Create a new Brazilian Fund",
    status_code=status.HTTP_201_CREATED,
)
async def create_brazilian_fund(
    fund: CreateBrazilianFundRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> CreateBrazilianFundResponse:
    return await FinanceService(session=session, user=user).create_br_fund(fund=fund)


@router.get("/funds/br", summary="Get all available brazilian funds")
async def get_brazilian_funds(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetBrazilianFundsResponse:
    return await FinanceService(session=session, user=user).get_brazilian_funds()
