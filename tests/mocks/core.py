import pytest_asyncio
from rolf_common.managers import BaseDataManager

from models.core import BankModel


@pytest_asyncio.fixture
async def create_bank(create_test_session) -> list:
    bank_list = []

    bank = BankModel(name='Bank 1', code=123)
    bank_1 = await BaseDataManager(session=create_test_session).add_one(bank)

    bank = BankModel(name='Bank 2', code=345)
    bank_2 = await BaseDataManager(session=create_test_session).add_one(bank)

    bank_list.append(bank_1)
    bank_list.append(bank_2)

    return bank_list
