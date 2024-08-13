from sqlalchemy import select
from typing import Any

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from models.investment import InvestmentModel


class InvestmentManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_investment(self, investment: InvestmentModel) -> SQLModel:
        await self.add_one(investment)

        return investment

    async def get_investments(self, params: dict[str, Any]) -> list[SQLModel]:
        stmt = select(InvestmentModel).order_by(InvestmentModel.transaction_date)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentModel, key) == value)

        investments: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return investments
