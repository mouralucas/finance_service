from rolf_common.managers import BaseDataManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import CurrencyModel


class FinanceManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_currencies(self) -> list[CurrencyModel]:
        query = select(CurrencyModel)

        currencies = await self.get_all(query)

        return [currency['CurrencyModel'] for currency in currencies]
