import datetime
from decimal import Decimal

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from managers.finance import FinanceManager
from managers.investment import InvestmentManager
from models.investment import InvestmentModel, InvestmentStatementModel, InvestmentObjectiveModel
from schemas.core import ChartSeriesSchema
from schemas.investment import InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema, InvestmentTypeSchema, InvestmentAllocationSchema, InvestmentPerformanceDataSchema
from schemas.request.investment import CreateInvestmentRequest, GetInvestmentRequest, LiquidateInvestmentRequest, CreateStatementRequest, GetStatementRequest, CreateObjectiveRequest, GetObjectiveRequest, GetObjectiveSummaryRequest, \
    GetPerformanceRequest, UpdateInvestmentRequest
from schemas.response.investment import CreateInvestmentResponse, GetInvestmentResponse, LiquidateInvestmentResponse, CreateStatementResponse, GetStatementResponse, CreateObjectiveResponse, GetObjectiveResponse, GetInvestmentTypeResponse, \
    GetInvestmentWithoutObjectives, GetObjectiveSummaryResponse, GetInvestmentAllocationResponse, GetInvestmentPerformanceResponse, UpdateInvestmentResponse
from services.utils.datetime import get_period, get_previous_period


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Investments
    async def create_investment(self, investment: CreateInvestmentRequest) -> CreateInvestmentResponse:
        account = await AccountManager(session=self.session).get_account_by_id(account_id=investment.account_id)
        custodian_id = account.bank_id

        new_investment = InvestmentModel(**investment.model_dump())
        new_investment.owner_id = self.user['user_id']
        new_investment.custodian_id = custodian_id

        if investment.liquidation_date and investment.liquidation_date <= datetime.date.today() and investment.liquidation_amount:
            new_investment.is_liquidated = True

        new_investment = await self.investment_manager.create_investment(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def update_investment(self, investment: UpdateInvestmentRequest) -> UpdateInvestmentResponse:
        fields = investment.model_dump(exclude_unset=True)

        updated_investment: InvestmentModel = await self.investment_manager.update_investment(investment_id=fields['id'], fields=fields)

        response = UpdateInvestmentResponse(
            investment=InvestmentSchema.model_validate(updated_investment)
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> GetInvestmentResponse:
        investments = await InvestmentManager(self.session).get_investments(owner_id=self.user['user_id'])

        response = GetInvestmentResponse(
            quantity=len(investments) if investments else 0,
            investments=[InvestmentSchema.model_validate(investment) for investment in investments] if investments else [],
        )

        return response

    async def liquidate_investment(self, investment_liquidate: LiquidateInvestmentRequest) -> LiquidateInvestmentResponse:
        current_investment = await InvestmentManager(self.session).get_investment_by_id(investment_liquidate.id)
        investment_liquidate = investment_liquidate.model_dump()

        # Get previous statement
        previous_statements = await self.investment_manager.get_statement(investment_id=investment_liquidate['id'])
        last_statement = previous_statements[-1] if previous_statements else None

        # Check if the statement from last period exists
        liquidation_period = get_period(investment_liquidate['liquidation_date'])

        # TODO: check if the liquidation period exists in statement before add
        # if last_statement and last_statement.period >= liquidation_period:
        #     raise ValueError
        # elif last_statement:
        #     # Only insert final statement if there is other statement (does not make much sense)
        #     new_statement = InvestmentStatementModel(
        #         investment_id=investment_liquidate['id'],
        #         period=liquidation_period,
        #         previous_amount=last_statement.gross_amount,
        #         gross_amount=investment_liquidate['gross_amount'],
        #         tax_detail = [investment_liquidate['tax_detail'] for tax in investment_liquidate['tax_detail']] if investment_liquidate['tax_detail'] else None,
        #         fee_detail = [investment_liquidate['fee_detail'] for fee in investment_liquidate['fee_detail']] if investment_liquidate['fee_detail'] else None,
        #         net_amount=investment_liquidate['net_amount'],
        #         reference_date=investment_liquidate['liquidation_date'],
        #         at_maturity=True,
        #     )
        #     await self.investment_manager.create_statement(new_statement)

        current_investment.is_liquidated = True
        current_investment.liquidation_date = investment_liquidate['liquidation_date']
        current_investment.liquidation_amount = investment_liquidate['liquidation_amount']

        response = LiquidateInvestmentResponse(
            investment=InvestmentSchema.model_validate(current_investment),
        )

        return response

    # Investment Types
    async def create_investment_type(self):
        pass

    async def get_investment_types(self) -> GetInvestmentTypeResponse:
        investment_types: list[RowMapping] = await self.investment_manager.get_investment_type()

        response = GetInvestmentTypeResponse(
            quantity=len(investment_types) if investment_types else 0,
            investment_types=[InvestmentTypeSchema.model_validate(data['InvestmentTypeModel']) for data in investment_types] if investment_types else [],
        )

        return response

    # Statements
    async def create_statement(self, statement: CreateStatementRequest) -> CreateStatementResponse:
        # Get the investment
        investment = await self.investment_manager.get_investment_by_id(statement.investment_id, raise_exception=True)

        # Get previous statement
        previous_statements = await self.investment_manager.get_statement(investment_id=investment.id)
        last_statement = previous_statements[-1] if previous_statements else None

        # TODO: add check to verify if period already exists (if so return the values)

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
        new_statement.total_tax = sum(tax.amount for tax in statement.tax_detail) if statement.tax_detail else 0.0
        new_statement.total_fee = sum(fee.amount for fee in statement.fee_detail) if statement.fee_detail else 0.0

        # Set the statistics
        new_statement.value_change = new_statement.gross_amount - new_statement.previous_amount
        new_statement.percentage_change = new_statement.value_change / new_statement.previous_amount * Decimal('100')

        # Persist data in database
        new_statement = await self.investment_manager.create_statement(new_statement)

        response = CreateStatementResponse(
            investment_statement=InvestmentStatementSchema.model_validate(new_statement),
        )

        return response

    async def get_statement(self, params: GetStatementRequest) -> GetStatementResponse:
        statement = await InvestmentManager(self.session).get_statement(investment_id=params.id, period=params.period,
                                                                        start_period=params.start_period, end_period=params.end_period)

        response = GetStatementResponse(
            quantity=len(statement) if statement else 0,
            statement=[InvestmentStatementSchema.model_validate(data) for data in statement] if statement else []
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
        objectives = await InvestmentManager(self.session).get_objectives(params=params.model_dump())

        response = GetObjectiveResponse(
            objectives=[InvestmentObjectiveSchema.model_validate(data['InvestmentObjectiveModel']) for data in objectives]
        )

        return response

    async def get_investment_without_objective(self) -> GetInvestmentWithoutObjectives:
        investments: list[InvestmentModel] = await self.investment_manager.get_objective_investments(with_objective=False)

        response = GetInvestmentWithoutObjectives(
            quantity=len(investments),
            investments=[InvestmentSchema.model_validate(data) for data in investments],
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
        allocation_by_type = await self.investment_manager.get_allocation_by_investment_type(owner_id=self.user['user_id'])

        allocation_by_category = await self.investment_manager.get_allocation_by_category(owner_id=self.user['user_id'])

        response = GetInvestmentAllocationResponse(
            type_allocation=[InvestmentAllocationSchema.model_validate(allocation) for allocation in allocation_by_type] if allocation_by_type else [],
            category_allocation=[InvestmentAllocationSchema.model_validate(allocation) for allocation in allocation_by_category] if allocation_by_category else [],
        )

        return response

    async def get_performance(self, params: GetPerformanceRequest) -> GetInvestmentPerformanceResponse:
        performance_portfolio = await self.investment_manager.get_performance_portfolio(
            owner_id=self.user['user_id'],
            period_range=params.period_range,
            indexer_id=params.indexer_id
        )

        indexer = await FinanceManager(session=self.session).get_indexer_by_id(indexer_id=params.indexer_id, raise_exception=True)

        accumulated_indexer = 1.0
        accumulated_variation = 1.0

        period_performance = []
        for item in performance_portfolio:
            indexer_variation_decimal = float(item['indexer_variation'] / 100) if item['indexer_variation'] else 0
            variation_decimal = float(item['variation'] / 100)

            accumulated_indexer *= (1 + indexer_variation_decimal)
            accumulated_variation *= (1 + variation_decimal)


            period_performance.append(
                {
                    'period': item['period'],
                    'indexer_variation': (accumulated_indexer - 1) * 100,
                    'variation': (accumulated_variation - 1) * 100
                }
            )

        # TODO: check an better way to send the name without use camel in python code (indexerVariation)
        # For each key, except 'period', in period_performance, must have a key/value in series list
        series = [
            {
                'value': 'indexerVariation',
                'name': indexer.name
            },
            {
                'value': 'variation',
                'name': 'Carteira'
            }
        ]

        response = GetInvestmentPerformanceResponse(
            data=[InvestmentPerformanceDataSchema.model_validate(performance) for performance in period_performance],
            series=[ChartSeriesSchema.model_validate(serie) for serie in series],
        )

        return response
