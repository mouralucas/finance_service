import datetime
import uuid
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.core import get_bank_mocked, get_currency_mocked
from models.account import AccountModel, AccountTypeModel
from models.core import BankModel, CurrencyModel

default_model_dict = {
    'created_at': datetime.datetime.utcnow(),
    'active': True
}


def get_mocked_account_type() -> list[dict[str, Any]]:
    account_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('3937eaa1-0d10-43c9-bce2-180ddf4d8944'),
            'type': 'Checking account',
            'description': 'Checking account description'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('c1eb07bc-9b0b-4997-8f74-2f41b9a887ba'),
            'type': 'Investment account',
            'description': 'Investment account description'
        }
    ]

    return account_types


def get_open_account_mocked() -> list[dict[str, Any]]:
    account_types = get_mocked_account_type()
    banks = get_bank_mocked()
    currencies = get_currency_mocked()

    accounts: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('aa7f0639-de9a-4968-b9d4-484a0871568c'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'bank_id': banks[0]['id'],
            'nickname': 'My account 1',
            'description': 'My account 1 description',
            'branch': '123-4',
            'number': '123456',
            'open_date': datetime.datetime.utcnow() - relativedelta(years=5, months=7, days=21),
            'type_id': account_types[0]['id'],
            'currency_id': currencies[0]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('ee471c3c-970c-429d-b8cb-e68b3761a533'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'bank_id': banks[1]['id'],
            'nickname': 'My account 2',
            'description': 'My second account description',
            'branch': '567-8',
            'number': '789123',
            'open_date': datetime.datetime.utcnow() - relativedelta(years=2, months=8, days=0),
            'type_id': account_types[0]['id'],
            'currency_id': currencies[0]['id'],
        }
    ]

    return accounts


def get_closed_account_mocked() -> list[dict[str, Any]]:
    account_types = get_mocked_account_type()
    banks = get_bank_mocked()
    currencies = get_currency_mocked()

    closed_accounts: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'bank_id': banks[0]['id'],
            'nickname': 'Account 1',
            'active': False,
            'description': 'Checking account description',
            'branch': '1212-1',
            'number': '123654',
            'open_date': datetime.datetime.utcnow() - relativedelta(years=15, months=3, days=11),
            'close_date': datetime.datetime.utcnow() - relativedelta(years=0, months=3, days=1),
            'type_id': account_types[0]['id'],
            'currency_id': currencies[0]['id']
        }
    ]

    return closed_accounts
