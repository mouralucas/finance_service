import asyncio
import datetime
import uuid

from rolf_common.managers import BaseDataManager

from backend.database import sessionmanager
import sqlalchemy.exc

from data_mock.core import get_mocked_countries
from models.core import TaxModel, CountryModel


async def insert_data():
    async with sessionmanager.session() as session:
        try:
            await BaseDataManager(session=session).add_all(get_mocked_countries())
        except sqlalchemy.exc.PendingRollbackError:
            print('Country data already inserted.')

        try:
            print('Inserting tax data...')
            await BaseDataManager(session=session).add_one(TaxModel(name='Imposto de Renda', acronyms='IR', description='Imposto aplicado sobre a renda', country_id='BR'))
            await BaseDataManager(session=session).add_one(TaxModel(name='Imposto sobre Operações Financeiras', acronyms='IOF', description='Imposto aplicado a toda operação financeira', country_id='BR'))
        except sqlalchemy.exc.PendingRollbackError:
            print('Tax data already inserted.')

if __name__ == "__main__":
    asyncio.run(insert_data())
