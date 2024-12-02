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