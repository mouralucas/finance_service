import datetime
import uuid
from typing import Any

default_model_dict = {
    'created_at': datetime.datetime.utcnow(),
    'active': True
}


def get_currency_mocked() -> list[dict[str, Any]]:
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


def get_bank_mocked() -> list[dict[str, Any]]:
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
        }
    ]

    return banks


def get_country_mocked() -> list[dict[str, Any]]:
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
    country_list = get_country_mocked()

    tax_list: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('a6c45a5a-f75f-475c-afa1-1cf02cd3fd04'),
            'name': 'Imposto de renda',
            'acronyms': 'IR',
            'country_id': country_list[0]['id'],
        },
        {
            **default_model_dict,
            'id': uuid.UUID('526d29e0-7dd1-43f7-b451-4d01be6d0195'),
            'name': 'Imposto sobre Operações Financeiras',
            'acronyms': 'IOF',
            'country_id': country_list[1]['id'],
        }
    ]

    return tax_list


def get_category_mocked() -> list[dict[str, Any]]:
    categories: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('43bc5e7a-02c2-4173-b364-0abcb46950b9'),
            'name': 'Test category',
            'description': 'This is a test category',
        },
        {
            **default_model_dict,
            'id': uuid.UUID('dd6022bf-ff38-4b2a-8f82-4f645df97a5b'),
            'name': 'Second test category',
            'description': 'This is a second test category',
        }
    ]

    return categories


def get_index_type_mocked() -> list[dict[str, Any]]:
    index_types: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('7676d154-4384-4d84-9a17-6d951df80b66'),
            'name': 'Indexador variável',
            'description': 'O rendimento é variável de acordo com o mercado'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('ddacb442-a487-403b-9419-cab038e53373'),
            'name': 'Indexador fixo',
            'description': 'O rendimento é fixo independente de variações do mercado'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('14ece4c4-d168-45de-ad0c-a410e425c7ad'),
            'name': 'Indexador híbrido'
            'description' 'O rendimento é baseado em um indexador variável e um fixo. Ex: IPCA + 6%'
        }
    ]

    return index_types

def get_investment_category_mocked() -> list[dict[str, Any]]:
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
        }
    ]

    return index_types


def get_index_mocked() -> list[dict[str, Any]]:
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


def get_liquidity_mocked() -> list[dict[str, Any]]:
    liquidity: list[dict[str, Any]] = [
        {
            **default_model_dict,
            'id': uuid.UUID('465d74a7-941e-4dc9-b2db-c94a0e686e15'),
            'name': 'Diária',
            'description': 'Liquidez diária'
        },
        {
            **default_model_dict,
            'id': uuid.UUID('f2d08680-b523-46be-b7e7-d753de4437fd'),
            'name': 'No vencimento',
            'description': 'Liquidez no vencimento'
        }
    ]

    return liquidity
