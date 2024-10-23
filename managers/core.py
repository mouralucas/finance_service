import uuid
from typing import cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.core import IndexerModel, PeriodicityModel, IndexerSeriesModel


class CoreManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    # TODO: indexer and periodicity is not investment but core in Finance
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
