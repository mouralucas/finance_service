import datetime
import uuid
from typing import Any

default_model_dict = {
    'created_at': datetime.datetime.now(datetime.timezone.utc),
    'active': True
}


def get_currency_mock() -> list[dict[str, Any]]:
    currencies = [
        {
            **default_model_dict,
            'id': 'BRL',
            'name': 'Real Brasileiro',
            'symbol': 'R$',
        },
        {
            **default_model_dict,
            'id': 'USD',
            'name': 'Dólar dos Estados Unidos',
            'symbol': '$',
        },
        {
            **default_model_dict,
            'id': 'EUR',
            'name': 'Euro',
            'symbol': '$',
        }
    ]

    return currencies


def get_bank_mock() -> list[dict[str, Any]]:
    banks = [
        {
            **default_model_dict,
            'id': uuid.UUID('79cafbd3-47f4-4ec3-b65a-a2e6b6dcce4c'),
            'name': 'Banco do Brasil',
            'code': 1
        },
        {
            **default_model_dict,
            'id': uuid.UUID('2abd8bee-ab6b-489f-b898-5fc1cc40c576'),
            'name': 'Nubank',
            'code': 260
        },
        {
            **default_model_dict,
            'id': uuid.UUID('5c8297d2-f791-422f-ab37-91b32ea35272'),
            'name': 'XP Investimentos',
            'code': 102
        },
        {
            **default_model_dict,
            'id': uuid.UUID('81be97b5-bff5-47bf-a2d4-82ccb35a6126'),
            'name': 'Itaú',
        }
    ]

    return banks


def get_country_mock() -> list[dict[str, Any]]:
    country_list: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': 'BR',
            'name': 'Brasil',
        },
        {
            **default_model_dict,
            'id': 'US',
            'name': 'Estados Unidos',
        },
        {
            **default_model_dict,
            'id': 'DE',
            'name': 'Alemanha',
        },
        {
            **default_model_dict,
            'id': 'AU',
            'name': 'Austrália',
        }
    ]
    return country_list


def get_tax_mocked() -> list[dict[str, Any]]:
    country_list = get_country_mock()

    tax_list: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('a6c45a5a-f75f-475c-afa1-1cf02cd3fd04'),
            'name': 'Imposto de renda',
            'acronyms': 'IR',
            'country_id': country_list[0]['id'],
            'type': 'tax',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('526d29e0-7dd1-43f7-b451-4d01be6d0195'),
            'name': 'Imposto sobre Operações Financeiras',
            'acronyms': 'IOF',
            'country_id': country_list[1]['id'],
            'type': 'tax',
        }
    ]

    return tax_list


def get_category_parent_mock() -> list[dict[str, Any]]:
    categories_parent: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('43bc5e7a-02c2-4173-b364-0abcb46950b9'),
            'name': 'Transporte',
            'description': 'Transações referentes a transporte',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('dd6022bf-ff38-4b2a-8f82-4f645df97a5b'),
            'name': 'Habitação',
            'description': 'Transações referentes a habitação',
        },
    ]

    return categories_parent


def get_category_mock() -> list[dict[str, Any]]:
    parents = get_category_parent_mock()

    categories: list[dict[str, Any]] = [
        # Transport categories
        {
            **default_model_dict,
            'id': uuid.UUID('8bb4afce-d8eb-4c15-bc24-78ace6c3faac'),
            'name': 'Estacionamento',
            'parent_id': parents[0]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('f320ee65-6610-4c1b-a6f4-7ca91cff45d0'),
            'name': 'Financiamento',
            'parent_id': parents[0]['id']
        },
        {
            **default_model_dict,
            'id': uuid.UUID('dd805d44-fd7a-4af2-adb4-39173f6f677f'),
            'name': 'Transporte público',
            'parent_id': parents[0]['id']
        },
        # Home
        {
            **default_model_dict,
            'id': uuid.UUID('013c9461-876f-4660-bec9-f6e7aba51807'),
            'name': 'Aluguel',
            'parent_id': parents[1]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('d6e660a9-3c00-4fde-b978-4439cfcd1209'),
            'name': 'Limpeza',
            'parent_id': parents[1]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('e0c5afab-a677-45cc-aa74-97bdd703d74b'),
            'name': 'Energia',
            'parent_id': parents[1]['id']
        },
    ]

    return categories


def get_index_type_mock() -> list[dict[str, Any]]:
    index_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('7676d154-4384-4d84-9a17-6d951df80b66'),
            'name': 'Variável',
            'description': 'O rendimento é variável de acordo com o mercado'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('ddacb442-a487-403b-9419-cab038e53373'),
            'name': 'Fixo',
            'description': 'O rendimento é fixo independente de variações do mercado'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('14ece4c4-d168-45de-ad0c-a410e425c7ad'),
            'name': 'Híbrido',
            'description': 'O rendimento é baseado em um indexador variável e um fixo. Ex: IPCA + 6%'
        }
    ]

    return index_types


def get_index_mock() -> list[dict[str, Any]]:
    index_list: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('4448e544-54bb-418f-b8d3-4d58513c0b58'),
            'name': 'Não especificado',
            'description': 'Sem índice especificado',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('373c2e30-321c-4590-9187-3e816e40c224'),
            'name': 'SELIC',
            'description': 'Taxa de juros SELIC'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('bfcfb9d4-b4d4-4fc9-993b-7516c44f47e4'),
            'name': 'CDI',
            'description': 'Certificado de depósito interbancário'
        }
    ]

    return index_list


def get_liquidity_mock() -> list[dict[str, Any]]:
    liquidity: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('465d74a7-941e-4dc9-b2db-c94a0e686e15'),
            'name': 'Diária',
            'description': 'Liquidez diária'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('d9d6b647-7ec1-4e6c-83e4-de3688a7ce4f'),
            'name': 'D+1',
            'description': 'Liquidez em D+1',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('f2d08680-b523-46be-b7e7-d753de4437fd'),
            'name': 'No vencimento',
            'description': 'Liquidez no vencimento'
        }
    ]

    return liquidity


def get_expense_type_mock() -> list[dict[str, Any]]:
    expense_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('425394a1-35c9-40ad-bcab-ab53bf024517'),
            'name': 'Fixo',
            'description': 'Gastos fixos',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('984a27e9-50e0-44a0-8737-7a87bb5d50a5'),
            'name': 'Recorrente',
            'description': 'Gastos recorrentes',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('196a9d3c-faf5-4dc6-bd5d-d101367a4d2f'),
            'name': 'Variável',
            'description': 'Gastos variáveis',
        }
    ]

    return expense_types
