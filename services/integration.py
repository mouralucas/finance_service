import datetime

from dateutil.relativedelta import relativedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from managers.core import CoreManager
from managers.finance import FinanceManager
from models.core import IndexerSeriesModel
from schemas.request.integration import CreateIndexerSeriesRequest
from services.utils.datetime import get_period, get_period_dates


class BcbIntegrationService:
    def __init__(self, session):
        self.session: AsyncSession = session
        self.url_bcb = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{resource_code}/dados?{params}'

        self.core_manager = CoreManager(self.session)
        self.finance_manager = FinanceManager(self.session)

    async def create_indexer_data(self, params: CreateIndexerSeriesRequest):

        indexer = await self.finance_manager.get_indexer_by_id(indexer_id=params.indexer_id, raise_exception=True)
        periodicity = await self.finance_manager.get_periodicity_by_id(periodicity_id=params.periodicity_id, raise_exception=True)

        latest_period = await self.finance_manager.get_latest_finance_series_period(indexer_id=params.indexer_id,
                                                                                    periodicity_id=params.periodicity_id)

        # current_period = get_current_period()
        # previous_period = get_previous_period()
        if latest_period:
            last_date_available = get_period_dates(latest_period) if latest_period else None
            next_date = last_date_available[0] + relativedelta(months=1)

            sgs_param = 'dataInicial=' + next_date.strftime('%d/%m/%Y')
        else:
            sgs_param = ''

        if str(periodicity.id) == 'b9f83ad5-7701-4098-bdaf-ee092f3247eb':
            next_date = datetime.datetime.now() - relativedelta(years=5)
            sgs_param = 'dataInicial=' + next_date.strftime('%d/%m/%Y')

        async with AsyncClient() as client:
            response = await client.get(self.url_bcb.format(resource_code=params.indexer_code, params=sgs_param))
            data = response.json()

            data_list = []
            for i in data:
                date = datetime.datetime.strptime(i['data'], '%d/%m/%Y')

                new_input = IndexerSeriesModel(
                    indexer_id=params.indexer_id,
                    indexer_name=indexer.name,
                    date=date,
                    period=get_period(date),
                    value=float(i['valor']),
                    periodicity_id=params.periodicity_id,
                    periodicity_name=periodicity.name,
                    unit='in dev'
                )

                data_list.append(new_input)

            self.session.add_all(data_list)
            await self.session.flush()
