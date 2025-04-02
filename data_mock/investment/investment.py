import datetime
import uuid
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.account import get_open_account_mock
from data_mock.common import default_model_dict
from data_mock.core import get_currency_mock, get_index_type_mock, get_indexer_mock, get_liquidity_mock, get_country_mock
from data_mock.investment.base import get_investment_category_mock, get_fixed_income_br_investment_type_mock
from services.utils.datetime import get_period


def get_investment_mock() -> list[dict[str, Any]]:
    accounts = get_open_account_mock()
    investment_types = get_fixed_income_br_investment_type_mock()
    currencies = get_currency_mock()
    index_types = get_index_type_mock()
    indexer = get_indexer_mock()
    liquidity = get_liquidity_mock()
    countries = get_country_mock()

    investments: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('a14f064a-c4fb-4b2a-bef3-17b163ed7261'),
            'owner_id': uuid.UUID('adf52a1e-7a19-11ed-a1eb-0242ac120002'),
            'custodian_id': accounts[2]['bank_id'],
            'account_id': accounts[2]['id'],  # XP
            'name': 'CDB Banco XP 12%',
            'type_id': investment_types[0]['id'],
            'transaction_date': datetime.date.today() - relativedelta(years=1, months=2, days=5),
            'maturity_date': datetime.date.today() + relativedelta(years=1, months=0, days=17),
            'quantity': 1.02,
            'price': 150.65,
            'amount': 1.02 * 150.65,
            'contracted_rate': 'Pré fixado 12%',
            'currency_id': currencies[0]['id'],
            'indexer_type_id': index_types[1]['id'],
            'indexer_id': indexer[0]['id'],
            'liquidity_id': liquidity[0]['id'],
            'country_id': countries[0]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('54eaabe7-7e7b-4bd6-95f4-e361e34e989f'),
            'owner_id': uuid.UUID('adf52a1e-7a19-11ed-a1eb-0242ac120002'),
            'custodian_id': accounts[1]['bank_id'],
            'account_id': accounts[1]['id'],
            'name': "CDB Banco Outro",
            'type_id': investment_types[0]['id'],
            'transaction_date': datetime.date.today() - relativedelta(years=4, months=7, days=28),
            'maturity_date': datetime.date.today() + relativedelta(years=0, months=11, days=9),
            'quantity': 998.3,
            'price': 1.50,
            'amount': 998.3 * 1.50,
            'contracted_rate': '110% do CDI',
            'currency_id': currencies[0]['id'],
            'indexer_type_id': index_types[0]['id'],
            'indexer_id': indexer[1]['id'],
            'liquidity_id': liquidity[0]['id'],
            'country_id': countries[0]['id'],
        }
    ]

    return investments


def get_investment_statement_mock() -> list[dict[str, Any]]:
    investments = get_investment_mock()

    statements: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'investment_id': investments[0]['id'],
            'reference_date': investments[0]['transaction_date'],
            'period': get_period(investments[0]['transaction_date']),
            'previous_amount': investments[0]['amount'],
            'gross_amount': investments[0]['amount'] + investments[0]['amount'] * 0.01,
            'total_tax': 0.25,
            'total_fee': 0,
            'net_amount': (investments[0]['amount'] + investments[0]['amount'] * 0.01) - 0.25
        }
    ]

    return statements



