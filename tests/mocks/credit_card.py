import uuid

import pytest_asyncio
import datetime

from rolf_common.managers import BaseDataManager

from data_mock.credit_card import get_credit_card_mocked, get_cancelled_credit_card_mocked
from models.credit_card import CreditCardModel
from schemas.credit_card import CreditCardSchema


@pytest_asyncio.fixture
async def create_valid_credit_card(test_session, create_open_account, create_currency) -> list[CreditCardSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(CreditCardModel, get_credit_card_mocked())
    credit_cards: list[CreditCardSchema] = [CreditCardSchema.model_validate(data["CreditCardModel"]) for data in data_]

    return credit_cards


@pytest_asyncio.fixture
async def create_cancelled_card(test_session, create_open_account, create_currency) -> list[CreditCardSchema]:
    data_ = await BaseDataManager(test_session).add_or_ignore_all(CreditCardModel, get_cancelled_credit_card_mocked())
    cancelled_card_list: list[CreditCardSchema] = [CreditCardSchema.model_validate(data["CreditCardModel"]) for data in data_]

    return cancelled_card_list

