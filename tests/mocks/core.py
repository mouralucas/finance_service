import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.core import (
    get_bank_mock,
    get_category_mock,
    get_category_parent_mock,
    get_country_mock,
    get_currency_mock,
    get_fee_mock,
    get_index_type_mock,
    get_indexer_mock,
    get_liquidity_mock,
    get_periodocity_mock,
    get_tax_mock,
)
from data_mock.investment.base import get_brazilian_fund_mock
from models.core import (
    BankModel,
    CategoryModel,
    CountryModel,
    CurrencyModel,
    IndexerModel,
    IndexerTypeModel,
    LiquidityModel,
    PeriodicityModel,
    TaxFeeModel,
)
from models.investment import FundsBrModel
from schemas.core import (
    BankSchema,
    CategorySchema,
    CountrySchema,
    CurrencySchema,
    IndexerSchema,
    IndexerTypeSchema,
    LiquiditySchema,
    PeriodicitySchema,
    TaxSchema,
)
from schemas.finance import FundsBrSchema


@pytest_asyncio.fixture
async def create_bank(test_session) -> list[BankSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        BankModel, get_bank_mock()
    )
    banks: list[BankSchema] = (
        [BankSchema.model_validate(data["BankModel"]) for data in data_]
        if data_
        else []
    )

    return banks


@pytest_asyncio.fixture
async def create_currency(test_session) -> list[CurrencySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        CurrencyModel, get_currency_mock()
    )
    currencies: list[CurrencySchema] = (
        [CurrencySchema.model_validate(data["CurrencyModel"]) for data in data_]
        if data_
        else []
    )

    return currencies


@pytest_asyncio.fixture
async def create_indexer_type(test_session) -> list[IndexerTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        IndexerTypeModel, get_index_type_mock()
    )
    index_type = (
        [IndexerTypeSchema.model_validate(data["IndexerTypeModel"]) for data in data_]
        if data_
        else []
    )

    return index_type


@pytest_asyncio.fixture
async def create_indexer(test_session) -> list[IndexerSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        IndexerModel, get_indexer_mock()
    )
    index = (
        [IndexerSchema.model_validate(data["IndexerModel"]) for data in data_]
        if data_
        else []
    )

    return index


@pytest_asyncio.fixture
async def create_category(test_session) -> list[CategorySchema]:
    # Insert the base categories (this categories cannot be set to any transaction)
    await BaseDataManager(test_session).add_or_ignore_all(
        CategoryModel, get_category_parent_mock()
    )
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        CategoryModel, get_category_mock()
    )
    categories = (
        [CategorySchema.model_validate(data["CategoryModel"]) for data in data_]
        if data_
        else []
    )

    return categories


@pytest_asyncio.fixture
async def create_country(test_session) -> list[CountrySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        CountryModel, get_country_mock()
    )
    countries: list[CountrySchema] = (
        [CountrySchema.model_validate(data["CountryModel"]) for data in data_]
        if data_
        else []
    )

    return countries


@pytest_asyncio.fixture
async def create_tax(test_session, create_country) -> list[TaxSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        TaxFeeModel, get_tax_mock()
    )
    tax_list = (
        [TaxSchema.model_validate(data["TaxFeeModel"]) for data in data_]
        if data_
        else []
    )

    return tax_list


@pytest_asyncio.fixture
async def create_fee(test_session, create_country):
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        TaxFeeModel, get_fee_mock()
    )
    fee_list = (
        [TaxSchema.model_validate(data["TaxFeeModel"]) for data in data_]
        if data_
        else []
    )

    return fee_list


@pytest_asyncio.fixture
async def create_liquidity(test_session):
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        LiquidityModel, get_liquidity_mock()
    )
    liquidity = (
        [LiquiditySchema.model_validate(data["LiquidityModel"]) for data in data_]
        if data_
        else []
    )

    return liquidity


@pytest_asyncio.fixture
async def create_brazilian_funds(test_session):
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        FundsBrModel, get_brazilian_fund_mock()
    )
    brazilian_funds = (
        [FundsBrSchema.model_validate(data["FundsBrModel"]) for data in data_]
        if data_
        else []
    )

    return brazilian_funds


@pytest_asyncio.fixture
async def create_periodicity(test_session):
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        PeriodicityModel, get_periodocity_mock()
    )

    periodicity = (
        [PeriodicitySchema.model_validate(data["PeriodicityModel"]) for data in data_]
        if data_
        else []
    )

    return periodicity
