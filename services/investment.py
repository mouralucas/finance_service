import datetime
import uuid

from fastapi import HTTPException

from rolf_common.models import SQLModel
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.investment import InvestmentManager
from models.investment import InvestmentModel, InvestmentStatementModel, InvestmentObjectiveModel
from schemas.investment import InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema, InvestmentTypeSchema
from schemas.request.investment import CreateInvestmentRequest, GetInvestmentRequest, LiquidateInvestmentRequest, CreateStatementRequest, GetStatementRequest, CreateObjectiveRequest, GetObjectiveRequest, GetObjectiveSummaryRequest
from schemas.response.investment import CreateInvestmentResponse, GetInvestmentResponse, LiquidateInvestmentResponse, CreateStatementResponse, GetStatementResponse, CreateObjectiveResponse, GetObjectiveResponse, GetInvestmentTypeResponse, GetInvestmentWithoutObjectives, GetObjectiveSummaryResponse
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
        # TODO: Maybe when creating a new investment, create the first line of the statement, with zero tax/fee and the invested value, when set the first statement just update
        new_investment = await self.investment_manager.create(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> GetInvestmentResponse:
        investments = await InvestmentManager(self.session).get_investments(params.model_dump())

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
        # Get the investment
        investment = await self.investment_manager.get_investment_by_id(statement.investment_id, raise_exception=True)

        # Get previous statement
        previous_statements = await self.investment_manager.get_statement({'investment_id': investment.id})
        last_statement = previous_statements[-1]['InvestmentStatementModel'] if previous_statements else None

        # If it is the first statement period must be the same as the investment
        if not previous_statements and get_period(investment.transaction_date) != statement.period:
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='First statement period must be the sabe as transaction period')

        # check if the statement period is less then investment
        if statement.period < get_period(investment.transaction_date):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='Statement period cannot be before transaction period')

        # Check if the statement from last period exists
        if last_statement and last_statement.period != get_previous_period(statement.period):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='Statement must be the following period of the last statement')

        # Set the model with the new statement
        new_statement = InvestmentStatementModel(**statement.model_dump())

        # Serialize the tax/fee information
        new_statement.tax_detail = [tax.model_dump(mode='json') for tax in statement.tax_detail] if statement.tax_detail else None
        new_statement.fee_detail = [fee.model_dump(mode='json') for fee in statement.fee_detail] if statement.fee_detail else None

        # Link the statement with the user
        new_statement.owner_id = self.user['user_id']

        # Set previous amount
        new_statement.previous_amount = last_statement.gross_amount if last_statement else investment.amount

        # Set the tax/fee totals
        new_statement.total_tax = sum(tax.amount for tax in statement.tax_detail) if statement.tax_detail else 0
        new_statement.total_fee = sum(fee.amount for fee in statement.fee_detail) if statement.fee_detail else 0

        # Set the statistics
        new_statement.value_change = new_statement.gross_amount - new_statement.previous_amount
        new_statement.percentage_change = new_statement.value_change / new_statement.previous_amount * 100

        # Persist data in database
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
        investments: list[RowMapping] = await self.investment_manager.get_investments({'objective_id': None})

        response = GetInvestmentWithoutObjectives(
            quantity=len(investments),
            investments=[InvestmentSchema.model_validate(data["InvestmentModel"]) for data in investments],
        )
        return response

    async def get_objective_summary(self, params: GetObjectiveSummaryRequest) -> GetObjectiveSummaryResponse:
        # The summary contais:
        #   1 - All data available from the objective (title, description,amount and estimated deadline)
        #   2 - If amount is present, check with the latest statement for the investment the gross amount. if not statement get the amount invested.
        #   3 - If estimated deadline and amount is present, calculate the amount needed to invest monthly until the amount is the goal is reach.
        #       3.1 - If possíble, use the calculation for investments, how many I have to invest to reach my goal, considering the gains
        objective = await self.investment_manager.get_objective_by_id(objective_id=params.id)
        if not objective:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")

        investments = await self.investment_manager.get_investments({'active': True, 'objective_id': params.id})
        if not investments:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No investment for objective '{objective_title}'".format(objective_title=objective.title))
        investment_ids = [investment['InvestmentModel'].id for investment in investments]

        statements = await self.investment_manager.get_latest_investment_statements(investment_ids=investment_ids)
        amount_invested = sum(statement.gross_amount for statement in statements)
        amount_stipulated = objective.amount
        perc_completed = amount_invested/amount_stipulated*100

        response = GetObjectiveSummaryResponse(
            objective_title=objective.title,
            amount_stipulated=amount_stipulated,
            amount_invested=amount_invested,
            perc_completed=perc_completed,
        )

        return response

