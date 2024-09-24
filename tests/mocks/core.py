import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.core import get_country_mocked, get_tax_mocked, get_currency_mocked, get_bank_mocked, get_category_mocked, get_liquidity_mocked
from data_mock.core import get_index_mocked, get_index_type_mocked
from models.core import BankModel, CurrencyModel, CategoryModel, CountryModel, TaxFeeModel, IndexerTypeModel, IndexerModel, LiquidityModel
from schemas.core import CurrencySchema, BankSchema, CountrySchema, TaxSchema, CategorySchema, IndexerTypeSchema, IndexerSchema, LiquiditySchema


@pytest_asyncio.fixture
async def create_bank(test_session) -> list[BankSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(BankModel, get_bank_mocked())
    banks: list[BankSchema] = [BankSchema.model_validate(data) for data in data_]

    return banks


@pytest_asyncio.fixture
async def create_currency(test_session) -> list[CurrencySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(CurrencyModel, get_currency_mocked())
    currencies: list[CurrencySchema] = [CurrencySchema.model_validate(currency) for currency in data_]

    return currencies


@pytest_asyncio.fixture
async def create_index_type(test_session) -> list[IndexerTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(IndexerTypeModel, get_index_type_mocked())
    index_type = [IndexerTypeSchema.model_validate(data) for data in data_]

    return index_type


@pytest_asyncio.fixture
async def create_index(test_session) -> list[IndexerSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(IndexerModel, get_index_mocked())
    index = [IndexerSchema.model_validate(data) for data in data_]

    return index


@pytest_asyncio.fixture
async def create_category(test_session) -> list[CategorySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(CategoryModel, get_category_mocked())
    categories = [CategorySchema.model_validate(data) for data in data_]

    return categories


@pytest_asyncio.fixture
async def create_country(test_session) -> list[CountrySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(CountryModel, get_country_mocked())
    countries: list[CountrySchema] = [CountrySchema.model_validate(data) for data in data_]

    return countries


@pytest_asyncio.fixture
async def create_tax(test_session, create_country) -> list[TaxSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(TaxFeeModel, get_tax_mocked())
    tax_list = [TaxSchema.model_validate(data) for data in data_]

    return tax_list


@pytest_asyncio.fixture
async def create_liquidity(test_session):
    data_ = await BaseDataManager(test_session).add_or_ignore_all(LiquidityModel, get_liquidity_mocked())
    liquidity = [LiquiditySchema.model_validate(data) for data in data_]

    return liquidity
