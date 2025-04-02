from typing import Any

from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from managers.investment import InvestmentManager
from models.investment_brazilian_fund import InvestmentFundsBrazilModel


class InvestmentBrazilianFundManager(InvestmentManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create_brazilian_fund(self, investment: InvestmentFundsBrazilModel) -> SQLModel:
        new_investment_fund = await self.add_one(investment)

        return new_investment_fund


    async def get_investment_funds(self):
        # In this case, if one fund have more than one investment it will be aggregated in only one register and the total is added
        pass