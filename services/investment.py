import datetime

from rolf_common.models import SQLModel
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from managers.investment import InvestmentManager
from models.investment import InvestmentModel, InvestmentStatementModel, InvestmentObjectiveModel
from schemas.investment import InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema, InvestmentTypeSchema
from schemas.request.investment import CreateInvestmentRequest, GetInvestmentRequest, LiquidateInvestmentRequest, CreateStatementRequest, GetStatementRequest, CreateObjectiveRequest, GetObjectiveRequest
from schemas.response.investment import CreateInvestmentResponse, GetInvestmentResponse, LiquidateInvestmentResponse, CreateStatementResponse, GetStatementResponse, CreateObjectiveResponse, GetObjectiveResponse, GetInvestmentTypeResponse, GetInvestmentWithoutObjectives
from services.utils.datetime import get_period, get_previous_period


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Investments
    async def create_investment(self, investment: CreateInvestmentRequest) -> CreateInvestmentResponse:
        new_investment = InvestmentModel(**investment.model_dump())
        new_investment.owner_id = self.user['user_id']

        if investment.liquidation_date and investment.liquidation_date <= datetime.date.today() and investment.liquidation_amount:
            new_investment.is_liquidated = True

        # TODO: if liquidation date <= today and liquidation amount set is_liquidated to true
        new_investment = await self.investment_manager.create(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> GetInvestmentResponse:
        investments = await InvestmentManager(self.session).get(params.model_dump())

        response = GetInvestmentResponse(
            quantity=len(investments),
            investments=InvestmentSchema.model_validate(investments),
        )

        return response

    async def liquidate_investment(self, investment: LiquidateInvestmentRequest) -> LiquidateInvestmentResponse:
        current_investment = await InvestmentManager(self.session).get_investment_by_id(investment.id)

        fields = investment.model_dump()
        fields['is_liquidated'] = True

        liquidated_investment = await self.investment_manager.update(current_investment, fields)

        response = LiquidateInvestmentResponse(
            investment=InvestmentSchema.model_validate(liquidated_investment),
        )

        return response

    # Investment Types
    async def create_investment_type(self):
        pass

    async def get_investment_types(self) -> GetInvestmentTypeResponse:
        investment_types: list[RowMapping] = await self.investment_manager.get_investment_type()

        response = GetInvestmentTypeResponse(
            investment_type=[InvestmentTypeSchema.model_validate(data['InvestmentTypeModel']) for data in investment_types],
        )

        return response

    # Statements
    async def create_statement(self, statement: CreateStatementRequest) -> CreateStatementResponse:
        new_statement = InvestmentStatementModel(**statement.model_dump())
        new_statement.owner_id = self.user['user_id']

        investment = await self.investment_manager.get_investment_by_id(statement.investment_id)
        previous_statements = await self.investment_manager.get_statement({'investment_id': investment.id})
        last_statement = previous_statements[0] if previous_statements else None

        # If it is the first statement period must be the sabe as the investment
        if not previous_statements and get_period(investment.transaction_date) != statement.period:
            raise

        # check if the statement period is less then investment
        if statement.period < get_period(investment.transaction_date):
            raise

        # Check if the statement from last period exists
        if last_statement and last_statement.period != get_previous_period(statement.period):
            pass

        # TODO: rules to add
        # The period must not be less then the investment transaction period
        # If the period is the same of investment transaction:
        #   The previous_amount is the amount invested
        # If period greater then investment transaction period:
        #   Check if the previous period is available in statement
        #       If not warn the user
        #   If exist, get the gross amount and set the previous amount from adding period

        new_statement = await self.investment_manager.create_statement(new_statement)

        response = CreateStatementResponse(
            investment_statement=InvestmentStatementSchema.model_validate(new_statement),
        )

        return response

    async def get_statement(self, params: GetStatementRequest) -> GetStatementResponse:
        statement = await InvestmentManager(self.session).get_statement(params=params.model_dump())

        response = GetStatementResponse(
            statement=[InvestmentStatementSchema.model_validate(data["InvestmentStatementModel"]) for data in statement]
        )

        return response

    # Objectives
    async def create_objective(self, objective: CreateObjectiveRequest) -> CreateObjectiveResponse:
        new_objective_ = InvestmentObjectiveModel(**objective.model_dump())
        new_objective_.owner_id = self.user['user_id']

        new_objective = await self.investment_manager.create_objective(new_objective_)

        response = CreateObjectiveResponse(
            objective=InvestmentObjectiveSchema.model_validate(new_objective)
        )

        return response

    async def get_objectives(self, params: GetObjectiveRequest):
        objectives = await InvestmentManager(self.session).get_investment_objectives(params=params.model_dump())

        response = GetObjectiveResponse(
            objectives=[InvestmentObjectiveSchema.model_validate(data['InvestmentObjectiveModel']) for data in objectives]
        )

        return response

    async def get_investment_without_objective(self) -> GetInvestmentWithoutObjectives:
        investments: list[RowMapping] = await self.investment_manager.get_investment_by_objective({})

        response = GetInvestmentWithoutObjectives(
            quantity=len(investments),
            investments=[InvestmentSchema.model_validate(data["InvestmentModel"]) for data in investments],
        )
        return response
