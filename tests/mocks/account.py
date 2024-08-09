import pytest_asyncio
from rolf_common.managers import BaseDataManager

from managers.account import AccountManager
from models.account import AccountTypeModel


@pytest_asyncio.fixture
async def create_account_type(create_test_session) -> list:
    type_list = []

    account_type = AccountTypeModel(type='Checking account', description='Checking account description')
    type_1 = await BaseDataManager(session=create_test_session).add_one(account_type)

    account_type = AccountTypeModel(type='Investment account', description='Investment account description')
    type_2 = await BaseDataManager(session=create_test_session).add_one(account_type)

    type_list.append(type_1)
    type_list.append(type_2)

    return type_list
