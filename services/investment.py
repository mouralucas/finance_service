import uuid
from decimal import Decimal
from typing import Any

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.finance import FinanceManager
from managers.investment import InvestmentManager
from models.investment import InvestmentModel, InvestmentStatementModel
from schemas.investment_deprecated import InvestmentSchema
from schemas.request.investment import (
    CreateStatementRequest,
    GetObjectiveRequest,
    GetPerformanceRequest,
    GetStatementsRequest,
    SettleInvestmentRequest,
    UpdateStatementRequest,
)
from schemas.response.investment import (
    SettleInvestmentResponse,
)
from services.utils.datetime import (
    get_last_business_day,
    get_period,
    get_previous_period,
)


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

    # Investment
    async def settle_investment(
        self, investment_settlement: SettleInvestmentRequest
    ) -> SettleInvestmentResponse:
        """
        Created by: Lucas Penha de Moura - 14/08/2024

            Update an investment with the values of a
                settlement (date, amount and taxes)
        :param investment_liquidate: The object of LiquidateInvestmentRequest
        :return:
        """
        current_investment: InvestmentModel | None = await InvestmentManager(
            self.session
        ).get_investment_by_id(investment_settlement.id)
        if not current_investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found"
            )
        investment_settlement_ = investment_settlement.model_dump()

        current_investment.is_settled = True
        current_investment.settlement_date = investment_settlement_["settlement_date"]
        current_investment.settlement_amount = investment_settlement_[
            "settlement_amount"
        ]

        response = SettleInvestmentResponse(
            investment=InvestmentSchema.model_validate(current_investment),
        )

        return response

    # Statement
    async def create_statement(
        self, input_statement: CreateStatementRequest
    ) -> dict[str, Any]:
        # Get the investment
        investment: InvestmentModel = (
            await self.investment_manager.get_investment_by_id(
                input_statement.investment_id, raise_exception=True
            )
        )

        # Get previous statement
        previous_statements = await self.investment_manager.get_statements(
            investment_id=investment.id
        )
        last_statement = previous_statements[0] if previous_statements else None

        # The first statement should be the same period as the transaction date
        if not last_statement and input_statement.period != get_period(
            investment.transaction_date
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="First statement period must be the sabe as transaction period",
            )

        # The statement should not be before the last statement
        if input_statement.period < get_period(investment.transaction_date):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Statement period cannot be before transaction period",
            )

        # The statement should be the following period of the last statement
        if last_statement and last_statement["period"] != get_previous_period(
            input_statement.period
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Statement must be the following period of the last statement",
            )

        # Set the model with the new statement
        new_statement = InvestmentStatementModel(
            **input_statement.model_dump(exclude={"tax_details", "fee_details"})
        )

        # The fist statement have the total invested as contribution
        if not last_statement:
            new_statement.contribution = investment.amount

        # Serialize the tax/fee information
        new_statement.tax_detail = (
            [tax.model_dump(mode="json") for tax in input_statement.tax_details]
            if input_statement.tax_details
            else []
        )
        new_statement.fee_detail = (
            [fee.model_dump(mode="json") for fee in input_statement.fee_details]
            if input_statement.fee_details
            else []
        )

        # Set the tax/fee totals
        new_statement.total_tax = (
            Decimal(sum(tax.amount for tax in input_statement.tax_details))
            if input_statement.tax_details
            else Decimal("0")
        )
        new_statement.total_fee = (
            Decimal(sum(fee.amount for fee in input_statement.fee_details))
            if input_statement.fee_details
            else Decimal("0")
        )

        # Persist data
        new_statement = await self.investment_manager.create_statement(new_statement)

        response = {
            "created": True,
            "statement_id": str(new_statement.id),
        }

        return response

    async def update_statement(
        self, input_statement: UpdateStatementRequest
    ) -> dict[str, Any]:
        changed_fields = input_statement.model_dump(exclude_unset=True, exclude={"id"})

        updated_statement = await self.investment_manager.update_statement(
            statement_id=input_statement.id, fields=changed_fields
        )

        # response = UpdateStatementResponse(
        #     updated=updated_statement is not None,
        #     statement_id=updated_statement.id if updated_statement else None,
        # )

        response = {
            "updated": updated_statement is not None,
            "statement_id": str(updated_statement.id) if updated_statement else None,
        }

        return response

    async def get_statement_by_id(self, statement_id: uuid.UUID) -> dict[str, Any]:
        statement = await self.investment_manager.get_statement_by_id(
            statement_id=statement_id
        )

        response = {"statement": statement.to_dict() if statement else None}

        return response

    async def get_statement(self, params: GetStatementsRequest) -> dict[str, Any]:
        """
        Created by: Lucas Penha de Moura - 28/08/2024

            Get investments statements based available params
        :param params: The object of GetStatementRequest with available parameters
        :return:
        """
        statements = await self.investment_manager.get_statements(
            investment_id=params.investment_id
        )

        response = {
            "quantity": len(statements) if statements else 0,
            "statements": statements,
        }

        return response

    async def get_statement_metadata(self, investment_id: uuid.UUID) -> dict[str, Any]:
        investment: InvestmentModel = (
            await self.investment_manager.get_investment_by_id(
                investment_id=investment_id
            )
        )
        previous_statements = await self.investment_manager.get_statements(
            investment_id=investment_id
        )
        last_statement = previous_statements[0] if previous_statements else None

        if not last_statement:
            return {
                "period": get_period(investment.transaction_date),
                "reference_date": get_last_business_day(investment.transaction_date),
                "contribution": float(investment.amount),
            }

        next_month = last_statement["reference_date"] + relativedelta(months=1)

        return {
            "period": get_period(next_month),
            "reference_date": get_last_business_day(next_month),
            "contribution": 0,
        }

    # Outro
    async def get_performance(self, params: GetPerformanceRequest) -> dict[str, Any]:
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
            return {
                "x_label": [],
                "data": [],
                "indexer_name": "",
            }

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

        # return GetInvestmentPerformanceResponseV2(
        #     x_label=x_value,
        #     data=[ChartSeriesSchemaV2.model_validate(item) for item in series],
        #     indexer_name=indexer.name,
        # )

        response = {"x_label": x_value, "data": series, "indexer_name": indexer.name}

        return response

    async def get_objectives(self, params: GetObjectiveRequest):
        """
        Created by: Lucas Penha de Moura - 02/09/2024

            Get investment objectives
        :param params: The object of GetObjectiveRequest with available parameters
        :return:
        """
        objectives = await InvestmentManager(self.session).get_objectives(
            owner_id=self.user["user_id"], objective_id=params.id
        )

        response = {
            "quantity": len(objectives) if objectives else 0,
            "objectives": objectives,
        }

        return response
