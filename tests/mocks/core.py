import pytest_asyncio
from rolf_common.managers import BaseDataManager

from models.core import BankModel, CurrencyModel, CategoryModel, CountryModel, TaxModel


@pytest_asyncio.fixture
async def create_bank(create_test_session) -> list:
    bank_list = []

    bank = BankModel(name='Bank 1', code=123)
    bank_1 = await BaseDataManager(session=create_test_session).add_one(bank)

    bank = BankModel(name='Bank 2', code=345)
    bank_2 = await BaseDataManager(session=create_test_session).add_one(bank)

    bank_list.append(bank_1)
    bank_list.append(bank_2)

    return bank_list


@pytest_asyncio.fixture
async def create_currency(create_test_session) -> list:
    currency_list = []

    currency = CurrencyModel(id='BRL', name='Real', symbol='R$')
    currency_1 = await BaseDataManager(session=create_test_session).add_one(currency)

    currency = CurrencyModel(id='USD', name='Dollar', symbol='$')
    currency_2 = await BaseDataManager(session=create_test_session).add_one(currency)

    currency = CurrencyModel(id='EUR', name='Euro', symbol='$')
    currency_3 = await BaseDataManager(session=create_test_session).add_one(currency)

    currency_list.append(currency_1)
    currency_list.append(currency_2)
    currency_list.append(currency_3)

    return currency_list


@pytest_asyncio.fixture
async def create_category(create_test_session) -> list:
    category_list = []

    category = CategoryModel(name='Test category', description='This is a test category')
    category_1 = await BaseDataManager(session=create_test_session).add_one(category)

    category = CategoryModel(name='Second test category', description='This is another test category')
    category_2 = await BaseDataManager(session=create_test_session).add_one(category)

    category_list.append(category_1)
    category_list.append(category_2)

    return category_list


@pytest_asyncio.fixture
async def create_country(create_test_session) -> list:
    country_list = []

    country = CountryModel(id='BR', name='Brasil')
    country_1 = await BaseDataManager(session=create_test_session).add_one(country)

    country = CountryModel(id='US', name='United States')
    country_2 = await BaseDataManager(session=create_test_session).add_one(country)

    country_list.append(country_1)
    country_list.append(country_2)

    return country_list

@pytest_asyncio.fixture
async def create_tax(create_test_session, create_investment):
    tax_list = []

    tax = TaxModel(name='Imposto de Renda', acronyms='IR', description='Imposto aplicado sobre a renda', country_id='BR')
    tax_1 = await BaseDataManager(session=create_test_session).add_one(tax)

    tax = TaxModel(name='Imposto sobre Operações Financeiras', acronyms='IOF', description='Imposto aplicado a toda operação financeira', country_id='BR')
    tax_2 = await BaseDataManager(session=create_test_session).add_one(tax)

    tax_list.append(tax_1)
    tax_list.append(tax_2)

    return tax_list