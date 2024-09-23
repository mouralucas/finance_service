import datetime

import pytest
from dateutil.relativedelta import relativedelta
from starlette import status

from services.utils.datetime import get_period


@pytest.mark.asyncio
async def test_create_investment(client, create_open_account, create_investment_type, create_index_type,
                                 create_index, create_liquidity):
    accounts = create_open_account
    account = accounts[0]
    investment_types = create_investment_type
    indexer_types = create_index_type
    indexers = create_index
    liquidity = create_liquidity
    currency_id = accounts[0].currency_id

    custodian_id = account.bank_id
    name = 'Investment in an asset'
    type_id = investment_types[0].id
    transaction_date = '2024-08-10'
    maturity_date = '2025-08-09'
    quantity = 1.025
    price = 1021.32
    amount = quantity * price
    indexer_type_id = indexer_types[0].id
    indexer_id = indexers[0].id
    liquidity_id = liquidity[0].id
    currency_id = currency_id
    country_id = 'BR'

    payload = {
        'custodianId': str(custodian_id),
        'accountId': str(account.id),
        'name': name,
        'typeId': str(type_id),
        'transactionDate': transaction_date,
        'maturityDate': maturity_date,
        'quantity': quantity,
        'price': price,
        'amount': amount,
        'currencyId': str(currency_id),
        'indexerTypeId': str(indexer_type_id),
        'indexerId': str(indexer_id),
        'liquidityId': str(liquidity_id),
        'countryId': country_id,
    }
    response = await client.post('/investment', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert 'investment' in data

    assert 'investmentId' in data['investment']

    assert 'accountId' in data['investment']
    assert data['investment']['accountId'] == str(account.id)

    assert 'name' in data['investment']
    assert data['investment']['name'] == name

    assert 'typeId' in data['investment']
    assert data['investment']['typeId'] == str(type_id)

    assert 'transactionDate' in data['investment']
    assert data['investment']['transactionDate'] == transaction_date

    assert 'maturityDate' in data['investment']
    assert data['investment']['maturityDate'] == maturity_date

    assert 'quantity' in data['investment']
    assert data['investment']['quantity'] == quantity

    assert 'price' in data['investment']
    assert data['investment']['price'] == price

    assert 'amount' in data['investment']
    assert data['investment']['amount'] == amount

    assert 'indexerTypeId' in data['investment']
    assert data['investment']['indexerTypeId'] == str(indexer_type_id)

    assert 'indexerId' in data['investment']
    assert data['investment']['indexerId'] == str(indexer_id)

    assert 'liquidityId' in data['investment']
    assert data['investment']['liquidityId'] == str(liquidity_id)

    assert 'currencyId' in data['investment']
    assert data['investment']['currencyId'] == str(currency_id)

    assert 'isLiquidated' in data['investment']
    assert data['investment']['isLiquidated'] is False


@pytest.mark.asyncio
async def test_create_liquidated_investment(client, create_open_account, create_investment_type, create_index_type,
                                            create_index, create_liquidity, create_currency):
    accounts = create_open_account

    custodian_id = accounts[0].bank_id
    name = 'Investment already liquidated'
    type_id = create_investment_type[0].id
    transaction_date = '2022-07-04'
    maturity_date = '2024-08-01'
    quantity = 1
    price = 112.47
    amount = quantity * price
    indexer_type_id = create_index_type[0].id
    indexer_id = create_index[0].id
    liquidity_id = create_liquidity[0].id
    currency_id = create_currency[0].id
    country_id = 'BR'
    liquidation_date = '2024-08-01'
    liquidation_amount = price + (price * 0.2)  # (about 20%)

    payload = {
        'custodianId': str(custodian_id),
        'accountId': str(accounts[0].id),
        'name': name,
        'typeId': str(type_id),
        'transactionDate': transaction_date,
        'maturityDate': maturity_date,
        'quantity': quantity,
        'price': price,
        'amount': amount,
        'currencyId': str(currency_id),
        'indexerTypeId': str(indexer_type_id),
        'indexerId': str(indexer_id),
        'liquidityId': str(liquidity_id),
        'countryId': country_id,
        'liquidationDate': liquidation_date,
        'liquidationAmount': liquidation_amount
    }
    response = await client.post('/investment', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert 'investment' in data

    assert 'liquidationDate' in data['investment']
    assert data['investment']['liquidationDate'] == liquidation_date
    assert 'liquidationAmount' in data['investment']
    assert data['investment']['liquidationAmount'] == liquidation_amount
    assert 'isLiquidated' in data['investment']
    assert data['investment']['isLiquidated'] is True


@pytest.mark.asyncio
async def test_liquidate_investment(client, create_investment):
    investments = create_investment

    investment_id = investments[0].id
    liquidation_date = '2025-08-09'
    liquidation_amount = 250.32

    payload = {
        'investmentId': str(investment_id),
        'liquidationDate': liquidation_date,
        'liquidationAmount': liquidation_amount
    }
    response = await client.post('/investment/liquidate', json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'investment' in data
    assert 'isLiquidated' in data['investment']
    assert data['investment']['isLiquidated'] is True
    assert 'liquidationDate' in data['investment']
    assert data['investment']['liquidationDate'] == liquidation_date
    assert 'liquidationAmount' in data['investment']
    assert data['investment']['liquidationAmount'] == liquidation_amount






