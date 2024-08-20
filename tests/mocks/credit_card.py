import uuid

import pytest_asyncio
import datetime

from rolf_common.managers import BaseDataManager

from models.credit_card import CreditCardModel


@pytest_asyncio.fixture
async def create_valid_credit_card(create_test_session, create_open_account, create_currency) -> list:
    credit_card_list = []

    accounts = create_open_account
    currencies = create_currency

    credit_card = CreditCardModel(owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
                                  nickname='My credit card', account_id=accounts[0].id,
                                  issue_date=datetime.date(2021, 1, 1),
                                  due_day=20, close_day=13, currency_id=currencies[0].id)
    credit_card_1 = await BaseDataManager(create_test_session).add_one(credit_card)

    credit_card_list.append(credit_card_1)

    return credit_card_list


@pytest_asyncio.fixture
async def create_cancelled_card(create_test_session, create_open_account, create_currency) -> list:
    cancelled_card_list = []

    accounts = create_open_account
    currencies = create_currency

    credit_card = CreditCardModel(active=False, owner_id=uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
                                  nickname='My cancelled credit card', account_id=accounts[1].id,
                                  issue_date=datetime.date(2017, 10, 23),
                                  due_day=5, close_day=27, currency_id=currencies[0].id)
    credit_card_1 = await BaseDataManager(create_test_session).add_one(credit_card)

    cancelled_card_list.append(credit_card_1)

    return cancelled_card_list

