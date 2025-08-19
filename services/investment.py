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
from models.investment import InvestmentModel, InvestmentObjectiveModel, InvestmentStatementModel
from schemas.core import ChartSeriesSchema
from schemas.investment import (
    InvestmentAllocationSchema,
    InvestmentObjectiveSchema,
    InvestmentPerformanceDataSchema,
    InvestmentSchema,
    InvestmentStatementSchema,
    InvestmentTypeSchema,
)
from schemas.request.investment import (
    CreateInvestmentRequest,
    CreateObjectiveRequest,
    CreateStatementRequest,
    GetInvestmentRequest,
    GetObjectiveRequest,
    GetObjectiveSummaryRequest,
    GetPerformanceRequest,
    GetStatementRequest,
    SettleInvestmentRequest,
    UpdateInvestmentRequest,
)
from schemas.request.investment_brazilian_fixed_income import CreateFixedIncomeInvestmentBrazilRequest
from schemas.response.investment import (
    CreateInvestmentResponse,
    CreateObjectiveResponse,
    CreateStatementResponse,
    GetInvestmentAllocationResponse,
    GetInvestmentPerformanceResponse,
    GetInvestmentResponse,
    GetInvestmentTypeResponse,
    GetInvestmentWithoutObjectives,
    GetObjectiveResponse,
    GetObjectiveSummaryResponse,
    GetStatementResponse,
    SettleInvestmentResponse,
    UpdateInvestmentResponse,
)
from services.utils.datetime import get_period, get_previous_period


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Investments
    async def create_investment(self, investment: CreateInvestmentRequest) -> CreateInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 12/08/2024

            Create a new investment
        :param investment: The object of CreateInvestmentRequest
        :return:
        """
        account = await AccountManager(session=self.session).get_account_by_id(account_id=investment.account_id)
        custodian_id = account.bank_id

        new_investment = InvestmentModel(**investment.model_dump())
        new_investment.owner_id = self.user['user_id']
        new_investment.custodian_id = custodian_id

        if investment.settlement_date and investment.settlement_date <= datetime.date.today() and investment.settlement_amount:
            new_investment.is_settled = True

        new_investment = await self.investment_manager.create_investment(new_investment)

        response = CreateInvestmentResponse(
            investment=InvestmentSchema.model_validate(new_investment),
        )

        return response

    async def create_fixed_incoming_br_investment(self, investment: CreateFixedIncomeInvestmentBrazilRequest):
        pass

    async def update_investment(self, investment: UpdateInvestmentRequest) -> UpdateInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 04/12/2024

            Update the information about an investment
        :param investment: The object of UpdateInvestmentRequest
        :return:
        """
        fields = investment.model_dump(exclude_unset=True)

        updated_investment: InvestmentModel = await self.investment_manager.update_investment(investment_id=fields['id'], fields=fields)

        response = UpdateInvestmentResponse(
            investment=InvestmentSchema.model_validate(updated_investment)
        )

        return response

    async def get_investments(self, params: GetInvestmentRequest) -> GetInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 12/08/2024

            Get investment based on available filters
        :param params: The object of GetInvestmentRequest with available params
        :return:
        """
        investments = await InvestmentManager(self.session).get_investments(owner_id=self.user['user_id'], is_settled=params.is_settled)

        response = GetInvestmentResponse(
            quantity=len(investments) if investments else 0,
            investments=[InvestmentSchema.model_validate(investment) for investment in investments] if investments else [],
        )

        return response

    async def settle_investment(self, investment_settlement: SettleInvestmentRequest) -> SettleInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 14/08/2024

            Update an investment with the values of a settlement (date, amount and taxes)
        :param investment_liquidate: The object of LiquidateInvestmentRequest
        :return:
        """
        current_investment: InvestmentModel | None = await InvestmentManager(self.session).get_investment_by_id(investment_settlement.id)
        if not current_investment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Investment not found')
        investment_settlement_ = investment_settlement.model_dump()

        current_investment.is_settled = True
        current_investment.settlement_date = investment_settlement_['settlement_date']
        current_investment.settlement_amount = investment_settlement_['settlement_amount']

        response = SettleInvestmentResponse(
            investment=InvestmentSchema.model_validate(current_investment),
        )

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
        investment_types: list[RowMapping] = await self.investment_manager.get_investment_type()

        response = GetInvestmentTypeResponse(
            quantity=len(investment_types) if investment_types else 0,
            investment_types=[InvestmentTypeSchema.model_validate(data['InvestmentTypeModel']) for data in investment_types] \
                if investment_types else [],
        )

        return response

    # Statements
    async def create_statement(self, statement: CreateStatementRequest) -> CreateStatementResponse:
        """
        Created by: Lucas Penha de Moura - 23/09/2024

            Create an investment statement
        :param statement: The object of CreateStatementRequest
        :return: The statement created
        """
        # Get the investment
        investment = await self.investment_manager.get_investment_by_id(statement.investment_id, raise_exception=True)

        # Get previous statement
        previous_statements = await self.investment_manager.get_statement(investment_id=investment.id)
        last_statement = previous_statements[0] if previous_statements else None

        # TODO: add check to verify if period already exists (if so return the values)

        # If it is the first statement period must be the same as the investment
        if not previous_statements and get_period(investment.transaction_date) != statement.period:
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail='First statement period must be the sabe as transaction period')

        # check if the statement period is less then investment
        if statement.period < get_period(investment.transaction_date):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail='Statement period cannot be before transaction period')

        # Check if the statement from last period exists
        if last_statement and last_statement.period != get_previous_period(statement.period):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail='Statement must be the following period of the last statement')

        # Set the model with the new statement
        new_statement = InvestmentStatementModel(**statement.model_dump(exclude={'tax_details', 'fee_details'}))

        # Serialize the tax/fee information
        new_statement.tax_detail = [tax.model_dump(mode='json') for tax in statement.tax_details] if statement.tax_details else None
        new_statement.fee_detail = [fee.model_dump(mode='json') for fee in statement.fee_details] if statement.fee_details else None

        # Link the statement with the user
        new_statement.owner_id = self.user['user_id']

        # Set previous amount
        new_statement.previous_amount = last_statement.gross_amount if last_statement else investment.amount

        # Set the tax/fee totals
        new_statement.total_tax = sum(tax.amount for tax in statement.tax_details) if statement.tax_details else 0.0
        new_statement.total_fee = sum(fee.amount for fee in statement.fee_details) if statement.fee_details else 0.0

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
        """
        Created by: Lucas Penha de Moura - 28/08/2024

            Get investments statements based available params
        :param params: The object of GetStatementRequest with available parameters
        :return:
        """
        statement = await InvestmentManager(self.session).get_statement(investment_id=params.investment_id, period=params.period,
                                                                        start_period=params.start_period, end_period=params.end_period)

        response = GetStatementResponse(
            quantity=len(statement) if statement else 0,
            statement=[InvestmentStatementSchema.model_validate(data) for data in statement] if statement else []
        )

        return response

    # Objectives
    async def create_objective(self, objective: CreateObjectiveRequest) -> CreateObjectiveResponse:
        """
        Created by: Lucas Penha de Moura - 02/09/2024

            Create a new investment objective
        :param objective: The object of CreateObjectiveRequest
        :return: The objective created
        """
        new_objective_ = InvestmentObjectiveModel(**objective.model_dump())
        new_objective_.owner_id = self.user['user_id']

        new_objective = await self.investment_manager.create_objective(new_objective_)

        response = CreateObjectiveResponse(
            objective=InvestmentObjectiveSchema.model_validate(new_objective)
        )

        return response

    async def get_objectives(self, params: GetObjectiveRequest):
        """
        Created by: Lucas Penha de Moura - 02/09/2024

            Get investment objectives
        :param params: The object of GetObjectiveRequest with available parameters
        :return:
        """
        objectives = await InvestmentManager(self.session).get_objectives(owner_id=self.user['user_id'], objective_id=params.id)

        response = GetObjectiveResponse(
            quantity=len(objectives) if objectives else 0,
            objectives=[InvestmentObjectiveSchema.model_validate(data['InvestmentObjectiveModel']) for data in objectives] if objectives else []
        )

        return response

    async def get_investment_without_objective(self) -> GetInvestmentWithoutObjectives:
        """
        Created by: Lucas Penha de Moura - 21/09/2024

            Get all investment without objectives related to it
        :return: The list of investment without objectives
        """
        investments: list[InvestmentModel] = await self.investment_manager.get_objective_investments(with_objective=False)

        response = GetInvestmentWithoutObjectives(
            quantity=len(investments),
            investments=[InvestmentSchema.model_validate(data) for data in investments],
        )
        return response

    async def get_objective_summary(self, params: GetObjectiveSummaryRequest) -> GetObjectiveSummaryResponse:
        """
        Created by: Lucas Penha de Moura - 06/10/2024

            Get the summary of the objectives
        :param params: The object of GetObjectiveSummaryRequest
        :return: The summary of the objectives
        """
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No investment for objective '{objective.title}'")
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
        """
        Created by: Lucas Penha de Moura - 16/10/2024

            Get the allocations of the investments
        :return: The allocations of the investments
        """
        type_allocation = await self.investment_manager.get_allocation_by_investment_type(owner_id=self.user['user_id'])
        category_allocation = await self.investment_manager.get_allocation_by_category(owner_id=self.user['user_id'])
        custodian_allocation = await self.investment_manager.get_allocation_by_custodian(owner_id=self.user['user_id'])
        objectives_allocation = await self.investment_manager.get_allocation_by_objectives(owner_id=self.user['user_id'])

        response = GetInvestmentAllocationResponse(
            type_allocation=[InvestmentAllocationSchema.model_validate(allocation) \
                for allocation in type_allocation] if type_allocation else [],
            category_allocation=[InvestmentAllocationSchema.model_validate(allocation) \
                for allocation in category_allocation] if category_allocation else [],
            custodian_allocation=[InvestmentAllocationSchema.model_validate(allocation)\
                for allocation in custodian_allocation] if custodian_allocation else [],
            objective_allocation=[InvestmentAllocationSchema.model_validate(allocation) \
                for allocation in objectives_allocation] if objectives_allocation else []
        )

        return response

    async def get_performance(self, params: GetPerformanceRequest) -> GetInvestmentPerformanceResponse:
        """
        Created by: Lucas Penha de Moura - 04/12/2024

            Get investments performance.
        :param params: The object of PerformanceRequest with available parameters
        :return: The performance of the investments
        """
        performance_portfolio = await self.investment_manager.get_performance_portfolio(
            owner_id=self.user['user_id'],
            investment_id=params.investment_id,
            period_range=params.period_range,
            indexer_id=params.indexer_id
        )

        if not performance_portfolio:
            return GetInvestmentPerformanceResponse(
                indexer_name='',
                total_invested=0,
                data=[],
                series=[],
            )

        indexer = await FinanceManager(session=self.session).get_indexer_by_id(indexer_id=params.indexer_id, raise_exception=True)
        investment = None
        if params.investment_id:
            investment = await self.investment_manager.get_investment_by_id(investment_id=params.investment_id)

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
                'name': investment.name if investment else 'Carteira'
            }
        ]

        total_invested = await self.investment_manager.get_total_invested(owner_id=self.user['user_id'])

        response = GetInvestmentPerformanceResponse(
            indexer_name=indexer.name,
            data=[InvestmentPerformanceDataSchema.model_validate(performance) for performance in period_performance],
            series=[ChartSeriesSchema.model_validate(serie) for serie in series],
            total_invested=total_invested,
        )

        return response
