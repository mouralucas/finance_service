import uuid
from typing import cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.core import CurrencyModel, BankModel, IndexerTypeModel, IndexerModel, LiquidityModel, PeriodicityModel, IndexerSeriesModel, TaxFeeModel


class FinanceManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_currencies(self) -> list[CurrencyModel] | None:
        query = select(CurrencyModel)

        currencies = await self.get_all(query)

        return [currency['CurrencyModel'] for currency in currencies] if currencies else None

    async def get_tax_fee(self, tax_fee_type: str) -> list[TaxFeeModel] | None:
        query = select(TaxFeeModel).where(TaxFeeModel.type == tax_fee_type)

        tax_fees = await self.get_all(query)

        return [tax_fee['TaxFeeModel'] for tax_fee in tax_fees] if tax_fees else None


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

    async def get_indexer_by_id(self, indexer_id: uuid.UUID, raise_exception=False) -> IndexerModel:
        indexer = await self.get_by_id(IndexerModel, indexer_id)

        if not indexer and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Indexer not found')

        return cast(IndexerModel, indexer)

    async def get_liquidity(self) -> list[LiquidityModel] | None:
        query = select(LiquidityModel)

        liquidity = await self.get_all(query)

        return [i['LiquidityModel'] for i in liquidity] if liquidity else None

    async def get_periodicity_by_id(self, periodicity_id: uuid.UUID, raise_exception=False) -> PeriodicityModel:
        periodicity = await self.get_by_id(PeriodicityModel, periodicity_id)

        if not periodicity and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Indexer not found')

        return cast(PeriodicityModel, periodicity)

    async def get_latest_finance_series_period(self, indexer_id: uuid.UUID, periodicity_id: uuid.UUID) -> int:
        """
        Created by: Lucas Penha de Moura - 05/12/2024
            Get the latest series period for an indexer and periodicity

        :param: indexer_id: the id of the indexer
        :param: periodicity_id: the id of the periodicity
        """
        sql_statement = (
            select(
                func.max(IndexerSeriesModel.period),
            )
            .where(
                IndexerSeriesModel.indexer_id == indexer_id,
                IndexerSeriesModel.periodicity_id == periodicity_id
            )
        )

        latest_period = await self.get_only_one(select_statement=sql_statement)

        return cast(int, latest_period) if latest_period else None