import uuid
from typing import cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.core import IndexerModel, PeriodicityModel, IndexerSeriesModel, CategoryModel, CountryModel


class CoreManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_categories(self) -> list[CategoryModel]:
        query = select(CategoryModel)

        categories = await self.get_all(query)

        return [category['CategoryModel'] for category in categories]

    async def get_countries(self) -> list[CountryModel]:
        query = select(CountryModel)

        countries = await self.get_all(query)

        return [country['CountryModel'] for country in countries] if countries else None

    # TODO: this methods are finance methods
    async def get_indexer_by_id(self, indexer_id: uuid.UUID, raise_exception=False) -> IndexerModel:
        indexer = await self.get_by_id(IndexerModel, indexer_id)

        if not indexer and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Indexer not found')

        return cast(IndexerModel, indexer)

    async def get_periodicity_by_id(self, periodicity_id: uuid.UUID, raise_exception=False) -> PeriodicityModel:
        periodicity = await self.get_by_id(PeriodicityModel, periodicity_id)

        if not periodicity and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Indexer not found')

        return cast(PeriodicityModel, periodicity)

    async def get_latest_finance_series_period(self, indexer_id: uuid.UUID, periodicity_id: uuid.UUID) -> int:
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
