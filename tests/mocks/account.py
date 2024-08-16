import datetime
import uuid

import pytest_asyncio
from rolf_common.managers import BaseDataManager

from models.account import AccountTypeModel, AccountModel


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


@pytest_asyncio.fixture
async def create_open_account(create_test_session, create_account_type, create_bank) -> list:
    account_types = create_account_type
    banks = create_bank
    account_list = []

    account = AccountModel(owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"), bank_id=banks[0].id, nickname='Account 1',
                           description='Checking account description', branch='1212-1',
                           number='123654', open_date=datetime.date(2024, 8, 9),
                           type_id=account_types[0].id)
    account_1 = await BaseDataManager(session=create_test_session).add_one(account)

    account = AccountModel(owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"), bank_id=banks[1].id, nickname='Account 1',
                           description='Checking account description of second account', branch='7896-2',
                           number='987456', open_date=datetime.date(2023, 2, 19),
                           type_id=account_types[1].id)
    account_2 = await BaseDataManager(session=create_test_session).add_one(account)

    account = AccountModel(owner_id=uuid.uuid4(), bank_id=banks[0].id, nickname='Account from another user',
                           description='This account should not appear in tests for the user', branch='1212-1',
                           number='7549653', open_date=datetime.date(2014, 9, 27),
                           type_id=account_types[0].id)
    account_3 = await BaseDataManager(session=create_test_session).add_one(account)

    account_list.append(account_1)
    account_list.append(account_2)
    account_list.append(account_3)

    return account_list
