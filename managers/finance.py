from rolf_common.managers import BaseDataManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import CurrencyModel, BankModel, IndexerTypeModel, IndexerModel, LiquidityModel


class FinanceManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_currencies(self) -> list[CurrencyModel] | None:
        query = select(CurrencyModel)

        currencies = await self.get_all(query)

        return [currency['CurrencyModel'] for currency in currencies] if currencies else None

    async def get_banks(self) -> list[BankModel] | None:
        query = select(BankModel)

        banks = await self.get_all(query)

        return [bank['BankModel'] for bank in banks] if banks else None

    async def get_indexer_types(self) -> list[IndexerTypeModel] | None:
        query = select(IndexerTypeModel)

        indexer_types = await self.get_all(query)

        return [indexer_type['IndexerTypeModel'] for indexer_type in indexer_types] if indexer_types else None

    async def get_indexers(self) -> list[IndexerTypeModel] | None:
        query = select(IndexerModel)

        indexers = await self.get_all(query)

        return [indexer_type['IndexerModel'] for indexer_type in indexers] if indexers else None

    async def get_liquidity(self) -> list[LiquidityModel] | None:
        query = select(LiquidityModel)

        liquidity = await self.get_all(query)

        return [i['LiquidityModel'] for i in liquidity] if liquidity else None