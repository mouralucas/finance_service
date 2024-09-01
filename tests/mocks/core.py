import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.core import get_country_mocked, get_tax_mocked, get_currency_mocked, get_bank_mocked, get_category_mocked, get_liquidity_mocked
from data_mock.core import get_index_mocked, get_index_type_mocked
from models.core import BankModel, CurrencyModel, CategoryModel, CountryModel, TaxModel, IndexTypeModel, IndexModel, LiquidityModel
from schemas.core import CurrencySchema, BankSchema, CountrySchema, TaxSchema, CategorySchema, IndexTypeSchema, IndexSchema, LiquiditySchema


@pytest_asyncio.fixture
async def create_bank(create_test_session) -> list[BankSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(BankModel, get_bank_mocked())
    banks: list[BankSchema] = [BankSchema.model_validate(data) for data in data_]

    return banks


@pytest_asyncio.fixture
async def create_currency(create_test_session) -> list[CurrencySchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(CurrencyModel, get_currency_mocked())
    currencies: list[CurrencySchema] = [CurrencySchema.model_validate(currency) for currency in data_]

    return currencies


@pytest_asyncio.fixture
async def create_index_type(create_test_session) -> list[IndexTypeSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(IndexTypeModel, get_index_type_mocked())
    index_type = [IndexTypeSchema.model_validate(data) for data in data_]

    return index_type


@pytest_asyncio.fixture
async def create_index(create_test_session) -> list[IndexSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(IndexModel, get_index_mocked())
    index = [IndexSchema.model_validate(data) for data in data_]

    return index


@pytest_asyncio.fixture
async def create_category(create_test_session) -> list[CategorySchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(CategoryModel, get_category_mocked())
    categories = [CategorySchema.model_validate(data) for data in data_]

    return categories


@pytest_asyncio.fixture
async def create_country(create_test_session) -> list[CountrySchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(CountryModel, get_country_mocked())
    countries: list[CountrySchema] = [CountrySchema.model_validate(data) for data in data_]

    return countries


@pytest_asyncio.fixture
async def create_tax(create_test_session, create_country) -> list[TaxSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(TaxModel, get_tax_mocked())
    tax_list = [TaxSchema.model_validate(data) for data in data_]

    return tax_list


@pytest_asyncio.fixture
async def create_liquidity(create_test_session):
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(LiquidityModel, get_liquidity_mocked())
    liquidity = [LiquiditySchema.model_validate(data) for data in data_]

    return liquidity
