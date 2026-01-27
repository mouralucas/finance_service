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
from schemas.request.integration import SyncIndexerSeriesRequest
from services.utils.datetime import (
    get_current_period,
    get_period,
    get_period_dates,
    get_previous_period,
)


class BcbIntegrationService:
    def __init__(self, session):
        self.session: AsyncSession = session
        self.url_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.\
            {resource_code}/dados?{params}"

        self.core_manager = CoreManager(self.session)
        self.finance_manager = FinanceManager(self.session)

    async def sync_indexer_data(
        self, params: SyncIndexerSeriesRequest
    ) -> dict[str, Any]:
        # Get indexer and periodicity objects
        indexer = await self.finance_manager.get_indexer_by_id(
            indexer_id=params.indexer_id, raise_exception=True
        )
        periodicity = await self.finance_manager.get_periodicity_by_id(
            periodicity_id=params.periodicity_id, raise_exception=True
        )

        # Fetch information about indexer and periodicity
        indexer_periodicity_info = (
            await self.finance_manager.get_indexer_periodicity_info(
                indexer_id=params.indexer_id, periodicity_id=params.periodicity_id
            )
        )

        if not indexer_periodicity_info:
            raise HTTPException(
                status_code=404, detail="Indexer periodicity information not found."
            )

        # Fetch last available period in database for this indexer and periodicity
        last_available_period = (
            await self.finance_manager.get_latest_finance_series_period(
                indexer_id=params.indexer_id, periodicity_id=params.periodicity_id
            )
        )

        # Build SGS parameters
        params_sgs = await self._build_sgs_params(
            periodicity_id=params.periodicity_id, latest_period=last_available_period
        )

        # Fetch data from SGS
        data = await self._get_from_sgs(
            resource_code=indexer_periodicity_info["sgs_code"], parameters=params_sgs
        )

        data_list = []
        for record in data:
            date = datetime.datetime.strptime(record["data"], "%d/%m/%Y")
            period = get_period(date)

            if last_available_period is None or period > last_available_period:
                new_series = IndexerSeriesModel(
                    indexer_id=params.indexer_id,
                    indexer_name=indexer.name,
                    date=date,
                    period=period,
                    value=float(record["valor"]),
                    periodicity_id=params.periodicity_id,
                    periodicity_name=periodicity.name,
                    unit=indexer_periodicity_info["unit"],
                )
                data_list.append(new_series)

        self.session.add_all(data_list)
        await self.session.flush()

        response = {
            "quantity": len(data_list),
            "indexer_series": data_list,
        }

        return response

    async def sync_daily_data(self, indexer_id: uuid.UUID):
        indexer = await self.finance_manager.get_indexer_by_id(
            indexer_id=indexer_id, raise_exception=True
        )

        # Get info for daily periodicity
        indexer_periodicity_info = (
            await self.finance_manager.get_indexer_periodicity_info(
                indexer_id=indexer_id,
                periodicity_id="b9f83ad5-7701-4098-bdaf-ee092f3247eb",
            )
        )

        if not indexer_periodicity_info:
            raise HTTPException(
                status_code=404, detail="Indexer periodicity information not found."
            )

        print(indexer)

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

    async def _build_sgs_params(
        self, periodicity_id: uuid.UUID, latest_period: int | None
    ) -> str:
        sgs_param = ""

        if latest_period == get_previous_period():
            # TODO: should not raise exception, just return empty data
            raise HTTPException(status_code=400, detail="Data is already up to date.")

        if latest_period:
            last_date_available = get_period_dates(latest_period)
            start_date = last_date_available[0] + relativedelta(months=1)

            sgs_param = "dataInicial=" + start_date.strftime("%d/%m/%Y")

        if str(periodicity_id) == "b9f83ad5-7701-4098-bdaf-ee092f3247eb":
            start_date = datetime.datetime.now() - relativedelta(years=5)
            sgs_param = "dataInicial=" + start_date.strftime("%d/%m/%Y")

        end_date = get_period_dates(get_previous_period(get_current_period()))[1]

        connector = ""
        if sgs_param:
            connector = "&"

        sgs_param = (
            sgs_param + "{connector}dataFinal=" + end_date.strftime("%d/%m/%Y")
        ).format(connector=connector)

        return "dataInicial=01/01/2020&dataFinal=31/12/2029"
