import datetime
import uuid

from dateutil.relativedelta import relativedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from managers.core import CoreManager
from managers.investment import InvestmentManager
from models.core import IndexerSeriesModel
from services.utils.datetime import get_period, get_period_dates


class BcbIntegrationService:
    def __init__(self, session):
        self.session: AsyncSession = session
        self.url_bcb = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{resource_code}/dados?{params}'

        self.investment_manager = CoreManager(self.session)

    async def get_indexer(self, indexer_code: str, indexer_id: uuid.UUID | str, periodicity_id: uuid.UUID | str):

        indexer = await self.investment_manager.get_indexer_by_id(indexer_id=indexer_id, raise_exception=True)
        periodicity = await self.investment_manager.get_periodicity_by_id(periodicity_id=periodicity_id, raise_exception=True)

        # TODO: add validation to None in last_period
        latest_period = await self.investment_manager.get_latest_finance_series_period(indexer_id=indexer_id, periodicity_id=periodicity_id)
        # first_date = get_period_dates(latest_period)
        # a = first_date[0] + relativedelta(months=1)
        #
        # params = 'dataInicial=' + a.strftime('%d/%m/%Y')
        params = ''

        async with AsyncClient() as client:
            response = await client.get(self.url_bcb.format(resource_code=indexer_code, params=params))
            data = response.json()

            data_list = []
            for i in data:
                date = datetime.datetime.strptime(i['data'], '%d/%m/%Y')

                new_input = IndexerSeriesModel(
                    indexer_id=indexer_id,
                    indexer_name=indexer.name,
                    date=date,
                    period=get_period(date),
                    value=float(i['valor']),
                    periodicity_id=periodicity_id,
                    periodicity_name=periodicity.name,
                    unit='in dev'
                )

                data_list.append(new_input)

            self.session.add_all(data_list)
            await self.session.flush()