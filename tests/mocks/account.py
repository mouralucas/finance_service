import pytest_asyncio
from rolf_common.managers import BaseDataManager

from data_mock.account import get_open_account_mocked, get_mocked_account_type, get_closed_account_mocked, get_account_transaction_mock
from models.account import AccountTypeModel, AccountModel, AccountTransactionModel
from schemas.account import AccountSchema, AccountTypeSchema, AccountTransactionSchema


@pytest_asyncio.fixture
async def create_account_type(test_session) -> list[AccountTypeSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(AccountTypeModel, get_mocked_account_type())
    account_types = [AccountTypeSchema.model_validate(data["AccountTypeModel"]) for data in data_]

    return account_types


@pytest_asyncio.fixture
async def create_open_account(test_session, create_bank, create_account_type, create_currency) -> list[AccountSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(AccountModel, get_open_account_mocked())
    account_list = [AccountSchema.model_validate(data["AccountModel"]) for data in data_]

    return account_list


@pytest_asyncio.fixture
async def create_closed_account(test_session, create_account_type, create_bank, create_currency) -> list[AccountSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(AccountModel, get_closed_account_mocked())
    account_list = [AccountSchema.model_validate(data["AccountModel"]) for data in data_]

    return account_list


@pytest_asyncio.fixture
async def create_account_transaction(test_session, create_open_account, create_currency, create_category) -> list[AccountTransactionSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(AccountTransactionModel, get_account_transaction_mock())
    account_transaction_list = [AccountTransactionSchema.model_validate(data['AccountTransactionModel']) for data in data_]

    return account_transaction_list