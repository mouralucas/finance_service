import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models.base import SQLModel
from sqlalchemy import RowMapping, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.core import (
    BankModel,
    CurrencyModel,
    IndexerModel,
    IndexerPeriodicityInformationModel,
    IndexerSeriesModel,
    IndexerTypeModel,
    LiquidityModel,
    PeriodicityModel,
    TaxFeeModel,
)
from models.investment_deprecated import FundsBrModel


class FinanceManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_fund(self, fund: FundsBrModel) -> SQLModel:
        await self.add_one(fund)

        return fund

    async def get_brazilian_funds(self) -> list[FundsBrModel] | None:
        query = select(FundsBrModel)

        funds = await self.get_all(query)

        return [fund["FundsBrModel"] for fund in funds] if funds else None

    async def get_brazilian_fund_by_id(self, fund_id: uuid.UUID) -> FundsBrModel:
        fund = await self.get_by_id(FundsBrModel, fund_id)

        if not fund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fund not found"
            )

        return cast(FundsBrModel, fund)

    async def get_currencies(self) -> list[RowMapping] | None:
        query = select(
            CurrencyModel.id.label("currency_id"),
            CurrencyModel.name,
            CurrencyModel.symbol,
        )

        currencies = await self.get_all(query)

        return currencies

    async def get_tax_fee(
        self, country_id: str, tax_fee_type: str
    ) -> list[TaxFeeModel] | None:
        query = select(TaxFeeModel).where(
            TaxFeeModel.country_id == country_id, TaxFeeModel.type == tax_fee_type
        )

        tax_fees = await self.get_all(query)

        return [tax_fee["TaxFeeModel"] for tax_fee in tax_fees] if tax_fees else None

    async def get_banks(self) -> list[BankModel] | None:
        query = select(BankModel).order_by(BankModel.name)

        banks = await self.get_all(query)

        return [bank["BankModel"] for bank in banks] if banks else None

    async def get_indexer_types(self) -> list[IndexerTypeModel] | None:
        query = select(IndexerTypeModel)

        indexer_types = await self.get_all(query)

        return (
            [indexer_type["IndexerTypeModel"] for indexer_type in indexer_types]
            if indexer_types
            else None
        )

    async def get_indexers(self) -> list[IndexerTypeModel] | None:
        query = select(IndexerModel)

        indexers = await self.get_all(query)

        return (
            [indexer_type["IndexerModel"] for indexer_type in indexers]
            if indexers
            else None
        )

    async def get_indexer_by_id(
        self, indexer_id: uuid.UUID, raise_exception=False
    ) -> IndexerModel:
        indexer = await self.get_by_id(IndexerModel, indexer_id)

        if not indexer and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Indexer not found")

        return cast(IndexerModel, indexer)

    async def get_liquidity(self) -> list[LiquidityModel] | None:
        query = select(LiquidityModel)

        liquidity = await self.get_all(query)

        return [i["LiquidityModel"] for i in liquidity] if liquidity else None

    async def get_periodicity(self) -> list[dict[str, Any]] | None:
        query = select(
            PeriodicityModel.id,
            PeriodicityModel.name,
            PeriodicityModel.description,
            PeriodicityModel.order,
        ).order_by(PeriodicityModel.order)

        periodicity = await self.get_all(query)

        return [dict(i) for i in periodicity] if periodicity else None

    async def get_periodicity_by_id(
        self, periodicity_id: uuid.UUID, raise_exception=False
    ) -> PeriodicityModel:
        periodicity = await self.get_by_id(PeriodicityModel, periodicity_id)

        if not periodicity and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Indexer not found")

        return cast(PeriodicityModel, periodicity)

    async def get_latest_finance_series_period(
        self, indexer_id: uuid.UUID, periodicity_id: uuid.UUID
    ) -> int | None:
        """
        Created by: Lucas Penha de Moura - 05/12/2024
            Get the latest series period for an indexer and periodicity

        :param: indexer_id: the id of the indexer
        :param: periodicity_id: the id of the periodicity
        """
        sql_statement = select(
            func.max(IndexerSeriesModel.period),
        ).where(
            IndexerSeriesModel.indexer_id == indexer_id,
            IndexerSeriesModel.periodicity_id == periodicity_id,
        )

        latest_period = await self.get_only_one(select_statement=sql_statement)

        return cast(int, latest_period) if latest_period else None

    async def get_indexer_series(
        self,
        indexer_id: uuid.UUID,
        periodicity_id: uuid.UUID,
        start_period: int | None = None,
        end_period: int | None = None,
    ) -> list[dict[str, Any]] | None:
        query = (
            select(
                IndexerSeriesModel.id,
                IndexerSeriesModel.indexer_id,
                IndexerSeriesModel.indexer_name,
                IndexerSeriesModel.date,
                IndexerSeriesModel.period,
                IndexerSeriesModel.periodicity_id,
                IndexerSeriesModel.periodicity_name,
                IndexerSeriesModel.value,
                IndexerSeriesModel.unit,
            )
            .where(
                IndexerSeriesModel.indexer_id == indexer_id,
                IndexerSeriesModel.periodicity_id == periodicity_id,
            )
            .order_by(IndexerSeriesModel.period.desc(), IndexerSeriesModel.date.desc())
        )

        if start_period is not None:
            query = query.where(IndexerSeriesModel.period >= start_period)

        if end_period is not None:
            query = query.where(IndexerSeriesModel.period <= end_period)

        indexer_series = await self.get_all(query)

        return [dict(i) for i in indexer_series] if indexer_series else None

    async def get_indexer_periodicity_info(
        self, indexer_id: uuid.UUID, periodicity_id: str
    ) -> dict[str, Any] | None:
        query = select(
            IndexerPeriodicityInformationModel.sgs_code,
            IndexerPeriodicityInformationModel.unit,
        ).where(
            IndexerPeriodicityInformationModel.indexer_id == indexer_id,
            IndexerPeriodicityInformationModel.periodicity_id == periodicity_id,
        )

        info = await self.session.execute(query)
        info = info.mappings().one_or_none()

        return dict(info) if info else None
