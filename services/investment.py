from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.finance import FinanceManager
from managers.investment import InvestmentManager
from schemas.core import ChartSeriesSchemaV2
from schemas.request.investment import GetPerformanceRequest
from schemas.response.investment import (
    GetInvestmentPerformanceResponseV2,
)


class InvestmentService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.investment_manager = InvestmentManager(session=self.session)

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
            # TODO: add new schema response
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
