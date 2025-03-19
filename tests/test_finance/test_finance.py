import uuid

import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_currency(client, create_currency):
    currencies = create_currency
    currencies_len = len(currencies)

    response = await client.get('/finance/currency')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'currencies' in data
    assert type(data['currencies']) == list
    assert len(data['currencies']) == currencies_len


@pytest.mark.asyncio
async def test_get_bank(client, create_bank):
    banks = create_bank
    banks_len = len(banks)

    response = await client.get('/finance/bank')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'banks' in data
    assert type(data['banks']) == list
    assert len(data['banks']) == banks_len


@pytest.mark.asyncio
async def test_get_indexer_types(client, create_indexer_type):
    types = create_indexer_type

    response = await client.get('/finance/indexer-type')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'indexerTypes' in data
    assert type(data['indexerTypes']) == list


@pytest.mark.asyncio
async def test_get_indexer_types(client, create_indexer):
    indexers = create_indexer

    response = await client.get('/finance/indexer')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'indexers' in data
    assert type(data['indexers']) == list


@pytest.mark.asyncio
async def test_get_tax_fee(client, create_tax, create_fee):
    payload = {
        'countryId': 'BR',
        'type': 'fee'
    }
    response = await client.get('/finance/tax-fee', params=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'taxFee' in data
    assert type(data['taxFee']) is list
    for tax_fee in data['taxFee']:
        assert 'type' in tax_fee
        assert tax_fee['type'] == 'fee'

        assert 'countryId' in tax_fee
        assert tax_fee['countryId'] == 'BR'


@pytest.mark.asyncio
async def test_create_brazilian_fund(client):
    name = 'Novo Fundo de Investimento FIM'
    fund_cnpj = '25.487.141/0001-01'
    admin = 'Banco Adm'
    admin_cnpj = '34.651.458/0001-22'
    fund_status = 'EM FUNCIONAMENTO NORMAL'
    start_date = '2015-05-01'
    minimum_balance = 150
    minimum_investment = 100
    minimum_withdraw = 100
    initial_investment = 500
    investment_quotation = 'D+1'
    redemption_quotation = 'D+3'
    redemption_settlement = 'D+4 (dias úteis)'

    payload = {
        'name': name,
        'fundCnpj': fund_cnpj,
        'administrator': admin,
        'administratorCnpj': admin_cnpj,
        'status': fund_status,
        'startDate': start_date,
        'minimumBalance': minimum_balance,
        'minimumInvestment': minimum_investment,
        'minimumWithdraw': minimum_withdraw,
        'initialInvestment': initial_investment,
        'investmentQuotation': investment_quotation,
        'redemptionQuotation': redemption_quotation,
        'redemptionSettlement': redemption_settlement,
    }
    response = await client.post('/finance/funds/br', json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'fund' in data
    assert type(data['fund']) is dict

    assert 'fundId' in data['fund']

