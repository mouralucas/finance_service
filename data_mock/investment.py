import datetime
import uuid
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.account import get_open_account_mock
from data_mock.core import get_currency_mock, get_index_type_mock, get_index_mock, get_liquidity_mock, get_country_mocked
from models.core import LiquidityModel
from models.investment import InvestmentModel
from services.utils.datetime import get_period

default_model_dict = {
    'created_at': datetime.datetime.now(datetime.timezone.utc),
    'active': True
}


def get_investment_category_mock() -> list[dict[str, Any]]:
    index_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('f001458a-251f-4f82-9846-a14834e82c68'),
            'name': 'Renda Fixa',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('954d50fc-3e0b-458f-92b5-fe00f163b3d2'),
            'name': 'Renda variável'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('bc94b55d-0041-42cf-9b03-2b9e1faabdab'),
            'name': 'Multimercado'
        }
    ]

    return index_types


def get_investment_type_mock() -> list[dict[str, Any]]:
    investment_category = get_investment_category_mock()

    investment_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('b9df5e2c-874b-4e7b-a68d-adfdb84dcbe6'),
            'name': 'CDB',
            'description': 'Certificado de Depósito Bancário',
            'investment_category_id': investment_category[0]['id']
        }
    ]

    return investment_types


def get_investment_mock() -> list[dict[str, Any]]:
    accounts = get_open_account_mock()
    investment_types = get_investment_type_mock()
    currencies = get_currency_mock()
    index_types = get_index_type_mock()
    indexer = get_index_mock()
    liquidity = get_liquidity_mock()
    countries = get_country_mocked()

    investments: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('a14f064a-c4fb-4b2a-bef3-17b163ed7261'),
            'owner_id': uuid.UUID('adf52a1e-7a19-11ed-a1eb-0242ac120002'),
            'custodian_id': accounts[0]['bank_id'],
            'account_id': accounts[2]['id'],  # XP
            'name': 'CDB Banco XP 12%',
            'description': 'Pré fixado 12%',
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
            'description': '110% do CDI',
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
            'period': get_period(investments[0]['transaction_date']),
            'previous_amount': investments[0]['amount'],
            'gross_amount': investments[0]['amount'] + investments[0]['amount'] * 0.01,
            'total_tax': 0.25,
            'total_fee': 0,
            'net_amount': (investments[0]['amount'] + investments[0]['amount'] * 0.001) - 0.25
        }
    ]

    return statements


def get_open_investment_objective_mocked() -> list[dict[str, Any]]:
    open_objectives: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('97502c10-1dec-48b8-b0d7-0d5a3eef7020'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'title': 'Meu objetivo futuro',
            'description': 'Comprar casa na praia',
            'amount': 75500,
            'estimated_deadline': datetime.date.today() + relativedelta(years=4),
        },
        {
            **default_model_dict,
            'id': uuid.UUID('26c28396-4d6f-454f-bc00-3bb2933a6238'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'title': 'Compra um carro novo',
            'description': 'Comprar um carro melhor que meu carro atual',
            'amount': 25000,
            'estimated_deadline': datetime.date.today() + relativedelta(years=1, months=6),
        }
    ]

    return open_objectives
