import datetime
from typing import Any

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from managers.investment import InvestmentManager
from models.investment import InvestmentModel
from models.investment_deprecated import (
    InvestmentObjectiveModel,
)
from schemas.investment_deprecated import (
    InvestmentAllocationSchema,
    InvestmentSchema,
    InvestmentTypeSchema,
)
from schemas.request.investment import (
    CreateInvestmentRequest,
    CreateObjectiveRequest,
    GetInvestmentRequest,
    GetObjectiveSummaryRequest,
    UpdateInvestmentRequest,
)
from schemas.response.investment import (
    CreateInvestmentResponse,
    CreateObjectiveResponse,
    GetInvestmentAllocationResponse,
    GetInvestmentTypeResponse,
    GetInvestmentWithoutObjectives,
    GetObjectiveSummaryResponse,
    UpdateInvestmentResponse,
)


class InvestmentServiceDeprecated(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Investments
    async def create_investment(
        self, investment: CreateInvestmentRequest
    ) -> CreateInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 12/08/2024

            Create a new investment
        :param investment: The object of CreateInvestmentRequest
        :return:
        """
        account = await AccountManager(session=self.session).get_account_by_id(
            account_id=investment.account_id
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )
        custodian_id = account.bank_id

        new_investment = InvestmentModel(**investment.model_dump())
        new_investment.owner_id = self.user["user_id"]
        new_investment.custodian_id = custodian_id

        if (
            investment.settlement_date
            and investment.settlement_date <= datetime.date.today()
            and investment.settlement_amount
        ):
            new_investment.is_settled = True

        new_investment = await self.investment_manager.create_investment(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def update_investment(
        self, investment: UpdateInvestmentRequest
    ) -> UpdateInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 04/12/2024

            Update the information about an investment
        :param investment: The object of UpdateInvestmentRequest
        :return:
        """
        fields = investment.model_dump(exclude_unset=True)

        updated_investment: InvestmentModel = (
            await self.investment_manager.update_investment(
                investment_id=fields["id"], fields=fields
            )
        )

        response = UpdateInvestmentResponse(
            investment=InvestmentSchema.model_validate(updated_investment)
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> dict[str, Any]:
        """
        Created by: Lucas Penha de Moura - 12/08/2024

            Get investment based on available filters
        :param params: The object of GetInvestmentRequest with available params
        :return:
        """
        investments = await InvestmentManager(self.session).get_investments(
            owner_id=self.user["user_id"], is_settled=params.is_settled
        )

        response = {
            "quantity": len(investments) if investments else 0,
            "investments": investments,
        }

        return response

    # Investment Types
    async def create_investment_type(self):
        pass

    async def get_investment_types(self) -> GetInvestmentTypeResponse:
        """
        Created by: Lucas Penha de Moura - 21/09/2024

            Get investments types
        :return: The list of investment types
        """
        investment_types: list[RowMapping] = (
            await self.investment_manager.get_investment_type()
        )

        response = GetInvestmentTypeResponse(
            quantity=len(investment_types) if investment_types else 0,
            investment_types=(
                [
                    InvestmentTypeSchema.model_validate(data["InvestmentTypeModel"])
                    for data in investment_types
                ]
                if investment_types
                else []
            ),
        )

        return response

    # Objectives
    async def create_objective(
        self, objective: CreateObjectiveRequest
    ) -> CreateObjectiveResponse:
        """
        Created by: Lucas Penha de Moura - 02/09/2024

            Create a new investment objective
        :param objective: The object of CreateObjectiveRequest
        :return: The objective created
        """
        new_objective_ = InvestmentObjectiveModel(**objective.model_dump())
        new_objective_.owner_id = self.user["user_id"]

        await self.investment_manager.create_objective(new_objective_)

        response = CreateObjectiveResponse(
            objective_created=True,
        )

        return response

    async def get_investment_without_objective(self) -> GetInvestmentWithoutObjectives:
        """
        Created by: Lucas Penha de Moura - 21/09/2024

            Get all investment without objectives related to it
        :return: The list of investment without objectives
        """
        investments: list[InvestmentModel] = (
            await self.investment_manager.get_objective_investments(
                with_objective=False
            )
        )

        response = GetInvestmentWithoutObjectives(
            quantity=len(investments),
            investments=[InvestmentSchema.model_validate(data) for data in investments],
        )
        return response

    async def get_objective_summary(
        self, params: GetObjectiveSummaryRequest
    ) -> GetObjectiveSummaryResponse:
        """
        Created by: Lucas Penha de Moura - 06/10/2024

            Get the summary of the objectives
        :param params: The object of GetObjectiveSummaryRequest
        :return: The summary of the objectives
        """
        # The summary contais:
        #   1 - All data available from the objective
        #       (title, description,amount and estimated deadline)
        #   2 - If amount is present, check with the latest statement for the
        #       investment the gross amount. if not statement get the amount invested.
        #   3 - If estimated deadline and amount is present, calculate the amount
        #           needed to invest monthly until the amount is the goal is reach.
        #       3.1 - If possíble, use the calculation for investments,
        #           how many I have to invest to reach my goal, considering the gains
        objective = await self.investment_manager.get_objective_by_id(
            objective_id=params.id
        )
        if not objective:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found"
            )

        investments = await self.investment_manager.get_investments(
            {"active": True, "objective_id": params.id}
        )
        if not investments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No investment for objective '{objective.title}'",
            )
        investment_ids = [
            investment["InvestmentModel"].id for investment in investments
        ]

        statements = await self.investment_manager.get_latest_investment_statements(
            investment_ids=investment_ids
        )
        amount_invested = sum(statement.gross_amount for statement in statements)
        amount_stipulated = objective.amount
        perc_completed = amount_invested / amount_stipulated * 100

        response = GetObjectiveSummaryResponse(
            objective_title=objective.title,
            amount_stipulated=amount_stipulated,
            amount_invested=amount_invested,
            perc_completed=perc_completed,
        )

        return response

    # Dashboard information
    async def get_investment_allocation(self) -> GetInvestmentAllocationResponse:
        """
        Created by: Lucas Penha de Moura - 16/10/2024

            Get the allocations of the investments
        :return: The allocations of the investments
        """
        type_allocation = (
            await self.investment_manager.get_allocation_by_investment_type(
                owner_id=self.user["user_id"]
            )
        )
        category_allocation = await self.investment_manager.get_allocation_by_category(
            owner_id=self.user["user_id"]
        )
        custodian_allocation = (
            await self.investment_manager.get_allocation_by_custodian(
                owner_id=self.user["user_id"]
            )
        )
        objectives_allocation = (
            await self.investment_manager.get_allocation_by_objectives(
                owner_id=self.user["user_id"]
            )
        )

        response = GetInvestmentAllocationResponse(
            type_allocation=(
                [
                    InvestmentAllocationSchema.model_validate(allocation)
                    for allocation in type_allocation
                ]
                if type_allocation
                else []
            ),
            category_allocation=(
                [
                    InvestmentAllocationSchema.model_validate(allocation)
                    for allocation in category_allocation
                ]
                if category_allocation
                else []
            ),
            custodian_allocation=(
                [
                    InvestmentAllocationSchema.model_validate(allocation)
                    for allocation in custodian_allocation
                ]
                if custodian_allocation
                else []
            ),
            objective_allocation=(
                [
                    InvestmentAllocationSchema.model_validate(allocation)
                    for allocation in objectives_allocation
                ]
                if objectives_allocation
                else []
            ),
        )

        return response
