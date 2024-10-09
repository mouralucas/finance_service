import datetime
import uuid
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.account import get_open_account_mock
from data_mock.core import get_currency_mocked


default_model_dict = {
    'created_at': datetime.datetime.utcnow(),
    'active': True
}

def get_credit_card_mocked() -> list[dict[str, Any]]:
    accounts = get_open_account_mock()
    currencies = get_currency_mocked()

    credit_cards: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('7e5c0228-8704-48af-b48b-0e1f8a8cf057'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'nickname': 'My credit card',
            'account_id': accounts[0]['id'],
            'issue_date': accounts[0]['open_date'] + relativedelta(days=1),
            'due_day': 20, 'close_day': 13, 'currency_id': currencies[0]['id']
        }
    ]

    return credit_cards


def get_cancelled_credit_card_mocked() -> list[dict[str, Any]]:
    accounts = get_open_account_mock()
    currencies = get_currency_mocked()

    credit_cards: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'active': False,
            'id': uuid.UUID('d9bfdd4a-8717-4964-b1bc-bf9ca4b71234'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'nickname': 'My cancelled credit card',
            'account_id': accounts[0]['id'],
            'issue_date': accounts[0]['open_date'] + relativedelta(days=1),
            'cancellation_date': accounts[0]['open_date'] + relativedelta(days=3),
            'due_day': 20, 'close_day': 13, 'currency_id': currencies[0]['id']
        }
    ]

    return credit_cards