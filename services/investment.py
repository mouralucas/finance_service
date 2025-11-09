from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.finance import FinanceManager
from managers.investment import InvestmentManager
from models.investment import InvestmentModel
from schemas.core import ChartSeriesSchemaV2
from schemas.request.investment import GetPerformanceRequest
from schemas.response.investment import (
    GetInvestmentPerformanceResponseV2,
)
from starlette import status

from services.utils.datetime import get_period


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Statement
    async def create_statement(self, statement: dict):
        # Get the investment
        investment: InvestmentModel = (
            await self.investment_manager.get_investment_by_id(
                statement["investment_id"], raise_exception=True
            )
        )

        # Get previous statement
        previous_statements = await self.investment_manager.get_statement(
            investment_id=investment.id
        )
        last_statement = previous_statements[0] if previous_statements else None

        # TODO: add check to verify if period already exists (if so return the values)

        # If it is the first statement period must be the same as the investment
        if (
            not previous_statements
            and get_period(investment.transaction_date) != statement.period
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="First statement period must be the sabe as transaction period",
            )

        # check if the statement period is less then investment
        if statement.period < get_period(investment.transaction_date):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Statement period cannot be before transaction period",
            )

        # Check if the statement from last period exists
        if last_statement and last_statement.period != get_previous_period(
            statement.period
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Statement must be the following period of the last statement",
            )

        # Set the model with the new statement
        new_statement = InvestmentStatementModel(
            **statement.model_dump(exclude={"tax_details", "fee_details"})
        )

        # Serialize the tax/fee information
        new_statement.tax_detail = (
            [tax.model_dump(mode="json") for tax in statement.tax_details]
            if statement.tax_details
            else None
        )
        new_statement.fee_detail = (
            [fee.model_dump(mode="json") for fee in statement.fee_details]
            if statement.fee_details
            else None
        )

        # Link the statement with the user
        new_statement.owner_id = self.user["user_id"]

        # Set previous amount
        new_statement.previous_amount = (
            last_statement.gross_amount if last_statement else investment.amount
        )

        # Set the tax/fee totals
        new_statement.total_tax = (
            sum(tax.amount for tax in statement.tax_details)
            if statement.tax_details
            else 0.0
        )
        new_statement.total_fee = (
            sum(fee.amount for fee in statement.fee_details)
            if statement.fee_details
            else 0.0
        )

        # Set the statistics
        new_statement.value_change = (
            new_statement.gross_amount - new_statement.previous_amount
        )
        new_statement.percentage_change = (
            new_statement.value_change / new_statement.previous_amount * Decimal("100")
        )

        # Persist data in database
        new_statement = await self.investment_manager.create_statement(new_statement)

        response = CreateStatementResponse(
            investment_statement=InvestmentStatementSchema.model_validate(
                new_statement
            ),
        )

        return response

    # Dashboard
    async def get_performance(
        self, params: GetPerformanceRequest
    ) -> GetInvestmentPerformanceResponseV2:
        """
        Created by: Lucas Penha de Moura - 22/09/2025

            Get investments performance.
        :param params: The object of PerformanceRequest with available parameters
        :return: The performance of the investments
        """
        performance_portfolio = await self.investment_manager.get_performance_portfolio(
            owner_id=self.user["user_id"],
            investment_id=params.investment_id,
            period_range=params.period_range,
            indexer_id=params.indexer_id,
        )

        if not performance_portfolio:
            return GetInvestmentPerformanceResponseV2(
                x_label=[],
                data=[],
                indexer_name="",
            )

        indexer = await FinanceManager(session=self.session).get_indexer_by_id(
            indexer_id=params.indexer_id, raise_exception=True
        )
        # investment = None
        # if params.investment_id:
        #     investment = await self.investment_manager.get_investment_by_id(
        #         investment_id=params.investment_id
        #     )

        accumulated_indexer = 1.0
        accumulated_variation = 1.0

        period_performance = []
        for item in performance_portfolio:
            indexer_variation_decimal = (
                float(item["indexer_variation"] / 100)
                if item["indexer_variation"]
                else 0
            )
            variation_decimal = float(item["variation"] / 100)

            accumulated_indexer *= 1 + indexer_variation_decimal
            accumulated_variation *= 1 + variation_decimal

            period_performance.append(
                {
                    "period": item["period"],
                    "indexer_variation": (accumulated_indexer - 1) * 100,
                    "variation": (accumulated_variation - 1) * 100,
                }
            )

        x_value = [item["period"] for item in period_performance]
        indexer_variation_data = [
            item["indexer_variation"] for item in period_performance
        ]
        variation_data = [item["variation"] for item in period_performance]

        # montar series
        series = [
            {"data": indexer_variation_data, "label": "Variação do indexer"},
            {"data": variation_data, "label": "Variação"},
        ]

        return GetInvestmentPerformanceResponseV2(
            x_label=x_value,
            data=[ChartSeriesSchemaV2.model_validate(item) for item in series],
            indexer_name=indexer.name,
        )
