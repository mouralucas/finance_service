import datetime
import uuid
from typing import Any

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from httpx import AsyncClient, Timeout
from sqlalchemy.ext.asyncio import AsyncSession

from managers.core import CoreManager
from managers.finance import FinanceManager
from models.core import IndexerSeriesModel
from services.utils.datetime import (
    get_period,
)


class BcbIntegrationService:
    def __init__(self, session):
        self.session: AsyncSession = session
        self.url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.\
            {resource_code}/dados?{params}"

        self.core_manager = CoreManager(self.session)
        self.finance_manager = FinanceManager(self.session)

    async def sync_monthly_data(self, indexer_id: uuid.UUID) -> dict[str, Any]:
        try:
            # Get indexer and periodicity objects
            indexer = await self.finance_manager.get_indexer_by_id(
                indexer_id=indexer_id, raise_exception=True
            )

            # Fetch information about indexer monthly
            indexer_periodicity_info = (
                await self.finance_manager.get_indexer_periodicity_info(
                    indexer_id=indexer_id,
                    periodicity_id=uuid.UUID("dc5b3bf8-2b84-423a-9a90-e7e194e355fa"),
                )
            )

            if not indexer_periodicity_info:
                raise HTTPException(
                    status_code=404, detail="Indexer periodicity information not found."
                )

            # Fetch last available period in database for this indexer and periodicity
            last_available_period = (
                await self.finance_manager.get_latest_finance_series_period(
                    indexer_id=indexer_id,
                    periodicity_id=uuid.UUID("dc5b3bf8-2b84-423a-9a90-e7e194e355fa"),
                )
            )

            # Build SGS parameters
            params_sgs = await self._build_monthly_sgs_params(
                latest_period=last_available_period
            )

            # Fetch data from SGS
            data = await self._get_from_sgs(
                resource_code=indexer_periodicity_info["sgs_code"],
                parameters=params_sgs,
            )

            data_list = []
            for record in data:
                date = datetime.datetime.strptime(record["data"], "%d/%m/%Y")
                period = get_period(date)

                if last_available_period is None or period > last_available_period:
                    new_series = IndexerSeriesModel(
                        indexer_id=indexer_id,
                        indexer_name=indexer.name,
                        date=date,
                        period=period,
                        value=float(record["valor"]),
                        periodicity_id=uuid.UUID(
                            "dc5b3bf8-2b84-423a-9a90-e7e194e355fa"
                        ),
                        periodicity_name="monthly",
                        unit=indexer_periodicity_info["unit"],
                    )
                    data_list.append(new_series)

            self.session.add_all(data_list)
            await self.session.flush()
        except Exception as e:
            return {
                "successful": False,
                "exception": e,
            }

        response = {
            "successful": True,
            "quantity": len(data_list),
        }

        return response

    async def sync_daily_data(self, indexer_id: uuid.UUID):
        try:
            indexer = await self.finance_manager.get_indexer_by_id(
                indexer_id=indexer_id, raise_exception=True
            )

            # Get info for daily periodicity
            indexer_periodicity_info = (
                await self.finance_manager.get_indexer_periodicity_info(
                    indexer_id=indexer_id,
                    periodicity_id=uuid.UUID("b9f83ad5-7701-4098-bdaf-ee092f3247eb"),
                )
            )

            if not indexer_periodicity_info:
                raise HTTPException(
                    status_code=404, detail="Indexer periodicity information not found."
                )

            # Fetch last available period in database for this indexer and periodicity
            last_available_date = (
                await self.finance_manager.get_latest_finance_series_date(
                    indexer_id=indexer_id,
                    periodicity_id=uuid.UUID("b9f83ad5-7701-4098-bdaf-ee092f3247eb"),
                )
            )

            # Build params for daily periodicity
            params_sgs = await self._build_daily_sgs_params(
                latest_saved_date=last_available_date
            )

            data = await self._get_from_sgs(
                resource_code=indexer_periodicity_info["sgs_code"],
                parameters=params_sgs,
            )
            data_list = []
            for record in data:
                date = datetime.datetime.strptime(record["data"], "%d/%m/%Y")
                period = get_period(date)

                if last_available_date is None or date.date() > last_available_date:
                    new_series = IndexerSeriesModel(
                        indexer_id=indexer_id,
                        indexer_name=indexer.name,
                        date=date,
                        period=period,
                        value=float(record["valor"]),
                        periodicity_id=uuid.UUID(
                            "b9f83ad5-7701-4098-bdaf-ee092f3247eb"
                        ),
                        periodicity_name="daily",
                        unit=indexer_periodicity_info["unit"],
                    )
                    data_list.append(new_series)

            self.session.add_all(data_list)
            await self.session.flush()
        except Exception as e:
            return {"successful": False, "exception": e}

        response = {
            "successful": True,
            "quantity": len(data_list),
        }

        return response

    async def _get_from_sgs(self, resource_code: int, parameters: str):
        timeout = Timeout(
            connect=5.0,
            read=30.0,
            write=10.0,
            pool=5.0,
        )
        async with AsyncClient(timeout=timeout) as client:
            response = await client.get(
                self.url_bcb.format(resource_code=resource_code, params=parameters)
            )
            response.raise_for_status()
            data = response.json()
            return data

    async def _build_daily_sgs_params(
        self, latest_saved_date: datetime.date | None
    ) -> str:
        """Build SGS query params to fetch missing daily data."""

        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        if latest_saved_date:
            start_date = latest_saved_date + relativedelta(days=1)
        else:
            start_date = datetime.date.today() - relativedelta(years=10)

        if start_date >= yesterday:
            raise ValueError("Latest date is already up-to-date or in the future")

        params = [
            f"dataInicial={start_date.strftime('%d/%m/%Y')}",
            f"dataFinal={yesterday.strftime('%d/%m/%Y')}",
        ]

        return "&".join(params)

    async def _build_monthly_sgs_params(self, latest_period: int | None) -> str:
        """Build SGS query params to fetch missing monthly data."""

        today = datetime.date.today()

        # Primeiro dia do mês atual
        current_month_start = today.replace(day=1)

        # Último dia do mês passado
        last_month_end = current_month_start - datetime.timedelta(days=1)

        # Período do mês passado (yyyymm)
        last_month_period = last_month_end.year * 100 + last_month_end.month

        start_date = None

        if latest_period:
            if latest_period >= last_month_period:
                raise ValueError("Latest period is already up-to-date or in the future")

            year = latest_period // 100
            month = latest_period % 100

            if not 1 <= month <= 12:
                raise ValueError("Invalid period format")

            latest_period_date = datetime.date(year, month, 1)

            # Primeiro dia do mês seguinte
            start_date = latest_period_date + relativedelta(months=1)

        params = []

        if start_date:
            params.append(f"dataInicial={start_date.strftime('%d/%m/%Y')}")

        params.append(f"dataFinal={last_month_end.strftime('%d/%m/%Y')}")

        return "&".join(params)
