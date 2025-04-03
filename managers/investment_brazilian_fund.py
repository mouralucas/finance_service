import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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

    async def get_investment_fund_by_id(self, investment_id: uuid.UUID) -> InvestmentFundsBrazilModel:
        investment = await self.get_by_id(InvestmentFundsBrazilModel, investment_id)
        if not investment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

        return cast(InvestmentFundsBrazilModel, investment)