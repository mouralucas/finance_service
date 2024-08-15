import pytest_asyncio
import datetime

from rolf_common.managers import BaseDataManager

from models.credit_card import CreditCardModel


@pytest_asyncio.fixture
async def create_credit_card(create_test_session, create_open_account) -> list:
    credit_card_list = []

    accounts = create_open_account

    credit_card = CreditCardModel(nickname='My credit card', account_id=accounts[0].id,
                                  issue_date=datetime.date(2021, 1, 1),
                                  due_day=20, close_day=13)
    credit_card_1 = BaseDataManager(create_test_session).add_one(credit_card)

    credit_card_list.append(credit_card_1)

    return credit_card_list
