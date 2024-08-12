import pytest_asyncio
from rolf_common.managers import BaseDataManager

from models.core import IndexTypeModel, IndexModel, LiquidityModel
from models.investment import InvestmentTypeModel


@pytest_asyncio.fixture
async def create_investment_type(create_test_session):
    investment_type_list = []

    investment_type = InvestmentTypeModel(name="Test Investment Type", description="Test Investment Type")
    investment_type_1 = await BaseDataManager(session=create_test_session).add_one(investment_type)

    investment_type = InvestmentTypeModel(name="Other Test Investment Type", description="Other Test Investment Type")
    investment_type_2 = await BaseDataManager(session=create_test_session).add_one(investment_type)

    investment_type_list.append(investment_type_1)
    investment_type_list.append(investment_type_2)

    return investment_type_list


@pytest_asyncio.fixture
async def create_index_type(create_test_session):
    index_type_list = []

    index_type = IndexTypeModel(name="Test Index Type", description="Test Index Type")
    index_type_1 = await BaseDataManager(session=create_test_session).add_one(index_type)

    index_type = IndexTypeModel(name="Other Index Type", description="Other Index Type")
    index_type_2 = await BaseDataManager(session=create_test_session).add_one(index_type)

    index_type = IndexTypeModel(name="Third Test Index Type", description="Third Test Index Type")
    index_type_3 = await BaseDataManager(session=create_test_session).add_one(index_type)

    index_type_list.append(index_type_1)
    index_type_list.append(index_type_2)
    index_type_list.append(index_type_3)

    return index_type_list


@pytest_asyncio.fixture
async def create_index(create_test_session):
    index_list = []

    index = IndexModel(name="Test Index", description="Test Index")
    index_1 = await BaseDataManager(session=create_test_session).add_one(index)

    index = IndexModel(name="Other Index", description="Other Index")
    index_2 = await BaseDataManager(session=create_test_session).add_one(index)

    index_list.append(index_1)
    index_list.append(index_2)

    return index_list


@pytest_asyncio.fixture
async def create_liquidity(create_test_session):
    liquidity_list = []

    liquidity = LiquidityModel(name="Test Liquidity", description="Test Liquidity")
    liquidity_1 = await BaseDataManager(session=create_test_session).add_one(liquidity)

    liquidity = LiquidityModel(name='Other Test Liquidity', description='Other Test Liquidity')
    liquidity_2 = await BaseDataManager(session=create_test_session).add_one(liquidity)

    liquidity_list.append(liquidity_1)
    liquidity_list.append(liquidity_2)

    return liquidity_list
