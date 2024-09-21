import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.investment import get_investment_type_mocked, get_investment_mocked, get_investment_statement_mock, get_open_investment_objective_mocked
from models.investment import InvestmentTypeModel, InvestmentModel, InvestmentStatementModel, InvestmentObjectiveModel
from schemas.investment import InvestmentTypeSchema, InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema


@pytest_asyncio.fixture
async def create_investment_type(test_session) -> list[InvestmentTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentTypeModel, get_investment_type_mocked())
    investment_types: list[InvestmentTypeSchema] = [InvestmentTypeSchema.model_validate(data) for data in data_]

    return investment_types


@pytest_asyncio.fixture
async def create_investment(test_session, create_open_account, create_investment_type, create_currency,
                            create_index_type, create_index, create_liquidity, create_country) -> list[InvestmentSchema]:

    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentModel, get_investment_mocked())
    investments = [InvestmentSchema.model_validate(data) for data in data_]

    return investments


@pytest_asyncio.fixture
async def create_investment_statement(test_session, create_investment) -> list[InvestmentStatementSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentStatementModel, get_investment_statement_mock())
    statements = [InvestmentStatementSchema.model_validate(data) for data in data_]

    return statements

@pytest_asyncio.fixture
async def create_open_investment_objectives(test_session) -> list[InvestmentObjectiveSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentObjectiveModel, get_open_investment_objective_mocked())
    open_objectives = [InvestmentObjectiveSchema.model_validate(data) for data in data_]

    return open_objectives