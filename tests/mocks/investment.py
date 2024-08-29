import datetime
import uuid
from datetime import timedelta

import pytest_asyncio
from dateutil.relativedelta import relativedelta
from rolf_common.managers import BaseDataManager

from models.core import IndexTypeModel, IndexModel, LiquidityModel
from models.investment import InvestmentTypeModel, InvestmentModel, InvestmentStatementModel
from services.utils.datetime import get_period


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


@pytest_asyncio.fixture
async def create_investment(create_test_session, create_open_account, create_investment_type, create_index_type,
                            create_index, create_liquidity, create_currency) -> list:
    investment_list = []

    accounts = create_open_account
    account = accounts[0]
    investment_types = create_investment_type
    index_types = create_index_type
    indexes = create_index
    liquidity = create_liquidity
    currencies = create_currency

    investment = InvestmentModel(owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
                                 custodian_id=account.bank_id,
                                 account_id=account.id,
                                 name="Test Investment",
                                 description="Test Investment",
                                 type_id=investment_types[0].id,
                                 transaction_date=datetime.date.today() - relativedelta(years=1, months=2, days=5),
                                 maturity_date=datetime.date.today() + relativedelta(years=1, months=0, days=17),
                                 quantity=1.02,
                                 price=150.65,
                                 amount=1.02 * 150.65,
                                 currency_id=currencies[0].id,
                                 index_type_id=index_types[0].id,
                                 index_id=indexes[0].id,
                                 liquidity_id=liquidity[0].id,
                                 country_id='BR')

    investment_1 = await BaseDataManager(session=create_test_session).add_one(investment)

    investment = InvestmentModel(owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
                                 custodian_id=accounts[1].bank_id,
                                 account_id=accounts[1].id,
                                 name="Test Investment 2",
                                 description="Test Investment 2",
                                 type_id=investment_types[1].id,
                                 transaction_date=datetime.date.today() - relativedelta(years=4, months=7, days=28),
                                 maturity_date=datetime.date.today() + relativedelta(years=0, months=11, days=9),
                                 quantity=998.3,
                                 price=1.50,
                                 amount=998.3 * 1.50,
                                 currency_id=currencies[0].id,
                                 index_type_id=index_types[0].id,
                                 index_id=indexes[0].id,
                                 liquidity_id=liquidity[0].id,
                                 country_id='BR')
    investment_2 = await BaseDataManager(session=create_test_session).add_one(investment)

    investment_list.append(investment_1)
    investment_list.append(investment_2)

    return investment_list


@pytest_asyncio.fixture
async def create_investment_statement(create_test_session, create_investment):
    investments = create_investment

    statement_list = []
    period = get_period(datetime.date.today())

    statement = InvestmentStatementModel(investment=investments[0],
                                         period=period,
                                         start_amount=0,
                                         gross_amount=investments[0].amount + investments[0].amount * 0.001,
                                         total_tax=0.25,
                                         total_fee=0,
                                         net_amount=(investments[0].amount + investments[0].amount * 0.001) - 0.25
                                         )
    statement_1 = await BaseDataManager(create_test_session).add_one(statement)

    statement_list.append(statement_1)

    return statement_list