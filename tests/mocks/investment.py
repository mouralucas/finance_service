import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.investment.base import (
    get_funds_br_investment_type_mock,
    get_investment_category_mock,
    get_open_investment_objective_mock,
)
from data_mock.investment.brazilian_funds import (
    get_brazilian_fund_investment_mock,
    get_brazilian_fund_investment_statement_mock,
)
from data_mock.investment.investment import (
    get_active_investment_mock,
    get_fixed_income_br_investment_type_mock,
    get_investment_statement_mock,
    get_settled_investment_mock,
)
from models.investment_deprecated import (
    InvestmentCategoryModel,
    InvestmentObjectiveModel,
    InvestmentTypeModel,
)
from models.investment import InvestmentModel, InvestmentStatementModel
from models.investment_brazilian_fund import (
    InvestmentBrazilianFundsModel,
    InvestmentBrazilianFundsStatementModel,
)
from schemas.investment_brazilian_fund import (
    InvestmentBrazilianFundSchema,
    InvestmentBrazilianFundStatementSchema,
)
from schemas.investment_deprecated import (
    InvestmentCategorySchema,
    InvestmentObjectiveSchema,
    InvestmentSchema,
    InvestmentStatementSchema,
    InvestmentTypeSchema,
)


@pytest_asyncio.fixture
async def create_investment_category(test_session) -> list[InvestmentCategorySchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentCategoryModel, get_investment_category_mock()
    )
    investment_categories: list[InvestmentCategorySchema] = (
        [
            InvestmentCategorySchema.model_validate(data["InvestmentCategoryModel"])
            for data in data_
        ]
        if data_
        else []
    )

    return investment_categories


@pytest_asyncio.fixture
async def create_fixed_income_br_investment_type(
    test_session, create_investment_category
) -> list[InvestmentTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentTypeModel, get_fixed_income_br_investment_type_mock()
    )
    investment_types: list[InvestmentTypeSchema] = (
        [
            InvestmentTypeSchema.model_validate(data["InvestmentTypeModel"])
            for data in data_
        ]
        if data_
        else []
    )

    return investment_types


@pytest_asyncio.fixture
async def create_funds_br_investment_type(
    test_session, create_investment_category
) -> list[InvestmentStatementSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentTypeModel, get_funds_br_investment_type_mock()
    )
    investment_types: list[InvestmentTypeSchema] = (
        [
            InvestmentTypeSchema.model_validate(data["InvestmentTypeModel"])
            for data in data_
        ]
        if data_
        else []
    )

    return investment_types


@pytest_asyncio.fixture
async def create_active_investment(
    test_session,
    create_open_account,
    create_fixed_income_br_investment_type,
    create_currency,
    create_indexer_type,
    create_indexer,
    create_liquidity,
    create_country,
) -> list[InvestmentSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentModel, get_active_investment_mock()
    )
    active_investments = (
        [InvestmentSchema.model_validate(data["InvestmentModel"]) for data in data_]
        if data_
        else []
    )

    return active_investments


@pytest_asyncio.fixture
async def create_settled_investment(
    test_session,
    create_open_account,
    create_fixed_income_br_investment_type,
    create_currency,
    create_indexer_type,
    create_indexer,
    create_liquidity,
    create_country,
) -> list[InvestmentSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentModel, get_settled_investment_mock()
    )
    investments = (
        [InvestmentSchema.model_validate(data["InvestmentModel"]) for data in data_]
        if data_
        else []
    )

    settled_investments = list(filter(lambda inv: inv.is_settled, investments))
    return settled_investments


@pytest_asyncio.fixture
async def create_brazilian_fund_investment(
    test_session,
    create_open_account,
    create_brazilian_funds,
    create_funds_br_investment_type,
    create_currency,
    create_country,
) -> list[InvestmentBrazilianFundSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentBrazilianFundsModel, get_brazilian_fund_investment_mock()
    )
    br_funds_investment = (
        [
            InvestmentBrazilianFundSchema.model_validate(
                data["InvestmentBrazilianFundsModel"]
            )
            for data in data_
        ]
        if data_
        else []
    )

    return br_funds_investment


@pytest_asyncio.fixture
async def create_brazilian_fund_investment_statement(
    test_session,
    create_open_account,
    create_brazilian_funds,
    create_funds_br_investment_type,
    create_currency,
    create_country,
    create_brazilian_fund_investment,
) -> list[InvestmentBrazilianFundStatementSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentBrazilianFundsStatementModel,
        get_brazilian_fund_investment_statement_mock(),
    )
    br_funds_investment_statement = (
        [
            InvestmentBrazilianFundStatementSchema.model_validate(
                data["InvestmentBrazilianFundsStatementModel"]
            )
            for data in data_
        ]
        if data_
        else []
    )

    return br_funds_investment_statement


@pytest_asyncio.fixture
async def create_investment_statement(
    test_session, create_active_investment
) -> list[InvestmentStatementSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentStatementModel, get_investment_statement_mock()
    )
    statements = (
        [
            InvestmentStatementSchema.model_validate(data["InvestmentStatementModel"])
            for data in data_
        ]
        if data_
        else []
    )

    return statements


@pytest_asyncio.fixture
async def create_open_investment_objectives(
    test_session,
    create_currency,
) -> list[InvestmentObjectiveSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(
        InvestmentObjectiveModel, get_open_investment_objective_mock()
    )
    open_objectives = (
        [
            InvestmentObjectiveSchema.model_validate(data["InvestmentObjectiveModel"])
            for data in data_
        ]
        if data_
        else []
    )

    return open_objectives
