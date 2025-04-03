import uuid
from typing import Any

from data_mock.account import get_open_account_mock
from data_mock.core import get_brazilian_fund_mock, get_indexer_mock, get_fee_mock, get_bank_mock, get_currency_mock, get_country_mock
from data_mock.investment.base import get_funds_br_investment_type_mock
from tests.utils import random_date


def get_brazilian_fund_investment_mock():
    brazilian_funds = get_brazilian_fund_mock()
    investment_types = get_funds_br_investment_type_mock()
    accounts = get_open_account_mock()
    currencies = get_currency_mock()
    countries = get_country_mock()

    brazilian_fund_investment: list[dict[str, Any]] = [
        {
            'id': uuid.UUID('a8d5e2c1-5f7b-4e0b-9a6f-3b7b6e8c5f4d'),
            'owner_id': uuid.UUID('adf52a1e-7a19-11ed-a1eb-0242ac120002'),
            'name': 'Fundo de Investimento Teste',
            'custodian_id': accounts[2]['bank_id'],
            'account_id': accounts[2]['id'],  # XP
            'price': 150.65,
            'quantity': 1.02,
            'amount': 1.02 * 150.65,
            'type_id': investment_types[0]['id'],
            'currency_id': currencies[0]['id'],
            'country_id': countries[0]['id'],
            'fund_id': brazilian_funds[0]['id'],
            'transaction_date': random_date(),
            'investment_quotation_date': random_date(),
            'investment_settlement_date': random_date(),
        }
    ]

    return brazilian_fund_investment