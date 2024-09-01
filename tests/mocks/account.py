import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.account import get_open_account_mocked, get_mocked_account_type, get_closed_account_mocked
from models.account import AccountTypeModel, AccountModel
from schemas.account import AccountSchema, AccountTypeSchema


@pytest_asyncio.fixture
async def create_account_type(create_test_session) -> list[AccountTypeSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(AccountTypeModel, get_mocked_account_type())
    account_types = [AccountTypeSchema.model_validate(data) for data in data_]

    return account_types


@pytest_asyncio.fixture
async def create_open_account(create_test_session, create_bank, create_account_type, create_currency) -> list[AccountSchema]:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(AccountModel, get_open_account_mocked())
    account_list = [AccountSchema.model_validate(data) for data in data_]

    return account_list


@pytest_asyncio.fixture
async def create_closed_account(create_test_session, create_account_type, create_bank, create_currency) -> list:
    data_ = await BaseDataManager(create_test_session).add_or_ignore_all(AccountModel, get_closed_account_mocked())
    account_list = [AccountSchema.model_validate(data) for data in data_]

    return account_list
