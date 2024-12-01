import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.investment import get_investment_type_mock, get_investment_mock, get_investment_statement_mock, get_open_investment_objective_mocked, get_investment_category_mock
from models.investment import InvestmentTypeModel, InvestmentModel, InvestmentStatementModel, InvestmentObjectiveModel, InvestmentCategoryModel
from schemas.investment import InvestmentTypeSchema, InvestmentSchema, InvestmentStatementSchema, InvestmentObjectiveSchema, InvestmentCategorySchema


@pytest_asyncio.fixture
async def create_investment_category(test_session) -> list[InvestmentCategorySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentCategoryModel, get_investment_category_mock())
    investment_categories: list[InvestmentCategorySchema] = [InvestmentCategorySchema.model_validate(data['InvestmentCategoryModel']) for data in data_]

    return investment_categories

@pytest_asyncio.fixture
async def create_investment_type(test_session, create_investment_category) -> list[InvestmentTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentTypeModel, get_investment_type_mock())
    investment_types: list[InvestmentTypeSchema] = [InvestmentTypeSchema.model_validate(data["InvestmentTypeModel"]) for data in data_]

    return investment_types


@pytest_asyncio.fixture
async def create_investment(test_session, create_open_account, create_investment_type, create_currency,
                            create_index_type, create_index, create_liquidity, create_country) -> list[InvestmentSchema]:

    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentModel, get_investment_mock())
    investments = [InvestmentSchema.model_validate(data["InvestmentModel"]) for data in data_]

    return investments


@pytest_asyncio.fixture
async def create_investment_statement(test_session, create_investment) -> list[InvestmentStatementSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentStatementModel, get_investment_statement_mock())
    statements = [InvestmentStatementSchema.model_validate(data["InvestmentStatementModel"]) for data in data_]

    return statements

@pytest_asyncio.fixture
async def create_open_investment_objectives(test_session) -> list[InvestmentObjectiveSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(InvestmentObjectiveModel, get_open_investment_objective_mocked())
    open_objectives = [InvestmentObjectiveSchema.model_validate(data["InvestmentObjectiveModel"]) for data in data_]

    return open_objectives