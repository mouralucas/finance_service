from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from rolf_common.schemas.auth import RequiredUser
from sqlalchemy.ext.asyncio import AsyncSession

from models.investment import InvestmentModel


class InvestmentManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_investment(self, investment: InvestmentModel) -> SQLModel:
        await self.add_one(investment)

        return investment
