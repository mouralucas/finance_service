import uuid
from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.common import default_model_dict
from data_mock.core import get_fee_mock


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


def get_fixed_income_br_investment_type_mock() -> list[dict[str, Any]]:
    investment_category = get_investment_category_mock()

    investment_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('b9df5e2c-874b-4e7b-a68d-adfdb84dcbe6'),
            'name': 'CDB',
            'description': 'Certificado de Depósito Bancário',
            'investment_category_id': investment_category[0]['id']
        },
        {
            **default_model_dict,
            'id': uuid.UUID('fd47a9a3-cc13-497f-bc55-ef55648af816'),
            'name': 'Fundo de investimento multimercado',
            'description': 'Fundo de investimento multimercado',
            'investment_category_id': investment_category[2]['id']
        }
    ]

    return investment_types


def get_funds_br_investment_type_mock() -> list[dict[str, Any]]:
    investment_category = get_investment_category_mock()

    funds_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('fd47a9a3-cc13-497f-bc55-ef55648af816'),
            'name': 'Fundo de Investimento Multimercado',
            'description': 'Fundo de Investimento Multimercado',
            'investment_category_id': investment_category[2]['id']
        }
    ]

    return funds_types


def get_open_investment_objective_mock() -> list[dict[str, Any]]:
    open_objectives: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('97502c10-1dec-48b8-b0d7-0d5a3eef7020'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'title': 'Meu objetivo futuro',
            'description': 'Comprar casa na praia',
            'amount': 75500,
            'estimated_deadline': date.today() + relativedelta(years=4),
        },
        {
            **default_model_dict,
            'id': uuid.UUID('26c28396-4d6f-454f-bc00-3bb2933a6238'),
            'owner_id': uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            'title': 'Comprar um carro novo',
            'description': 'Comprar um carro melhor que meu carro atual',
            'amount': 25000,
            'estimated_deadline': date.today() + relativedelta(years=1, months=6),
        }
    ]

    return open_objectives


def get_brazilian_fund_mock() -> list[dict[str, Any]]:
    fees = get_fee_mock()

    brazilian_funds: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('7737aca8-3db0-4fbd-bcbd-32c732faba8b'),
            "name": "Fundo de Teste FIM",
            "fund_cnpj": "36.436.439/0001-09",
            "administrator": "Adm do Fundo de Teste",
            "administrator_cnpj": "10.309.888/0001-00",
            "status": "ATIVO",
            "start_date": date(year=2010, month=4, day=5),
            "minimum_balance": 150,
            "minimum_investment": 100,
            "minimum_withdraw": 100,
            "initial_investment": 200,
            "investment_quotation": "D+1",
            "redemption_quotation": "D+3",
            "redemption_settlement": "D+4 (dias úteis)",
            "fees": [
                {
                    "id": str(fees[0]['id']),
                    "percentage": "0,6% a.a"
                }
            ],
            "benchmark": "CDI"
        }
    ]

    return brazilian_funds
