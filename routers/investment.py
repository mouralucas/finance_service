from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.database import get_session
from schemas.request.investment import (
    CreateInvestmentRequest,
    CreateObjectiveRequest,
    GetObjectiveSummaryRequest,
    SettleInvestmentRequest,
    UpdateInvestmentRequest,
)
from schemas.request.investment_brazilian_fixed_income import (
    CreateFixedIncomeInvestmentBrazilRequest,
)
from schemas.response.investment import (
    CreateInvestmentResponse,
    CreateObjectiveResponse,
    GetInvestmentAllocationResponse,
    GetInvestmentWithoutObjectives,
    GetObjectiveSummaryResponse,
    SettleInvestmentResponse,
    UpdateInvestmentResponse,
)
from services.investment import InvestmentService
from services.investment_deprecated import InvestmentServiceDeprecated

router = APIRouter(prefix="/investment", tags=["Investments"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create an investment",
    description="Create an new investment for the user",
    deprecated=True,
)
async def create_investment(
    investment: CreateInvestmentRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> CreateInvestmentResponse:
    response = await InvestmentServiceDeprecated(
        session=session, user=user
    ).create_investment(investment)

    return response


@router.post(
    "/fixed-income/br",
    summary="Create a brazilian fixed income investment",
    description="Create a brazilian fixed income investment such as CDB, LCA, etc",
    status_code=status.HTTP_201_CREATED,
)
async def create_fixed_income_br_investment(
    investment: CreateFixedIncomeInvestmentBrazilRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
):
    return await InvestmentServiceDeprecated(
        session=session, user=user
    ).create_fixed_incoming_br_investment(investment=investment)


@router.patch("", summary="Update an investment")
async def update_investment(
    investment: UpdateInvestmentRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> UpdateInvestmentResponse:
    return await InvestmentServiceDeprecated(
        session=session, user=user
    ).update_investment(investment=investment)


@router.post(
    "/settle", summary="Settle an investment", description="Settle an investment"
)
async def settle(
    investment: SettleInvestmentRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> SettleInvestmentResponse:
    response = await InvestmentService(session=session, user=user).settle_investment(
        investment
    )

    return response


# @router.get("/type", summary="Get investment types")
# async def get_investment_types(
#     session: AsyncSession = Depends(get_session),
#     user: RequiredUser = Security(get_user),
# ) -> GetInvestmentTypeResponse:
#     return await InvestmentServiceDeprecated(
#         session=session, user=user
#     ).get_investment_types()


@router.post(
    "/objective",
    status_code=status.HTTP_201_CREATED,
    summary="Create a investment objective",
    description="",
)
async def create_objective(
    objective: CreateObjectiveRequest,
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> CreateObjectiveResponse:
    return await InvestmentServiceDeprecated(session, user).create_objective(objective)


@router.get(
    "/objective/summary",
    summary="Objective summary",
    description="Get all information for a single objective",
)
async def get_objective_summary(
    params: GetObjectiveSummaryRequest = Depends(),
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetObjectiveSummaryResponse:
    response = await InvestmentServiceDeprecated(
        session=session, user=user
    ).get_objective_summary(params=params)

    return response


@router.get("/objective/not-set")
async def get_investments_without_objectives(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetInvestmentWithoutObjectives:
    return await InvestmentServiceDeprecated(
        session=session, user=user
    ).get_investment_without_objective()


@router.get(
    "/allocation",
    summary="Get investment allocation",
    description="Get the investment distribution between investment types",
)
async def get_allocation(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetInvestmentAllocationResponse:
    return await InvestmentServiceDeprecated(
        session=session, user=user
    ).get_investment_allocation()


# @router.get(
#     "/performance",
#     summary="Get investment performance",
#     description="Get investment performance",
# )
# async def get_performance(
#     params: GetPerformanceRequest = Depends(),
#     session: AsyncSession = Depends(get_session),
#     user: RequiredUser = Security(get_user),
# ) -> GetInvestmentPerformanceResponseV2:
#     return await InvestmentService(session=session, user=user).get_performance(
#         params=params
#     )
