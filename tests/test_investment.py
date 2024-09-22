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


@pytest.mark.asyncio
async def test_get_investment_type(client, create_investment_type):
    response = await client.get('/investment/type')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert type(data) is dict
    assert 'investmentType' in data
    assert type(data['investmentType']) is list

    for investmentType in data['investmentType']:
        assert 'name' in investmentType


@pytest.mark.asyncio
async def test_create_investment_statement(client, create_investment, create_tax):
    investments = create_investment
    taxes = create_tax

    investment_id = str(investments[0].id)
    period = 202408
    gross_amount = 35.10
    tax_id = str(create_tax[0].id)
    tax_name = create_tax[0].name
    total_tax = 0.2
    total_fee = 0
    net_amount = gross_amount - total_tax - total_fee

    payload = {
        'investmentId': investment_id,
        'period': period,
        'grossAmount': gross_amount,
        'totalTax': total_tax,
        'totalFee': total_fee,
        'netAmount': net_amount,
        'taxDetail': {
            'taxId': tax_id,
            'name': tax_name,
            'amount': total_tax
        }
    }

    response = await client.post('/investment/statement', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'investmentStatement' in data
    assert 'investmentId' in data['investmentStatement']
    assert data['investmentStatement']['investmentId'] == str(investment_id)
    assert 'period' in data['investmentStatement']
    assert data['investmentStatement']['period'] == period
    assert 'grossAmount' in data['investmentStatement']
    assert data['investmentStatement']['grossAmount'] == gross_amount
    assert 'totalTax' in data['investmentStatement']
    assert data['investmentStatement']['totalTax'] == total_tax
    assert 'totalFee' in data['investmentStatement']
    assert data['investmentStatement']['totalFee'] == total_fee
    assert 'netAmount' in data['investmentStatement']
    assert data['investmentStatement']['netAmount'] == net_amount
    # TODO: add test to tax and fee details


@pytest.mark.asyncio
async def test_get_statement(client, create_investment_statement):
    print('')
    payload = {
        'period': get_period(datetime.date.today())
    }
    response = await client.get('/investment/statement', params=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()


@pytest.mark.asyncio
async def test_create_objective(client):
    payload = {
        'title': 'Meu objetivo',
        'description': 'Comprar um apartamento na praia',
        'amount': 50000,
        'estimatedDeadline': (datetime.datetime.utcnow() + relativedelta(years=1, months=6)).strftime('%Y-%m-%d'),
    }
    response = await client.post('/investment/objective', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert 'objective' in data
    assert 'objectiveId' in data['objective']

    assert 'title' in data['objective']
    assert data['objective']['title'] == payload['title']
    assert 'description' in data['objective']
    assert data['objective']['description'] == payload['description']
    assert 'amount' in data['objective']
    assert data['objective']['amount'] == payload['amount']
    assert 'estimatedDeadline' in data['objective']
    assert data['objective']['estimatedDeadline'] == payload['estimatedDeadline']


@pytest.mark.asyncio
async def test_get_open_objectives(client, create_open_investment_objectives):
    response = await client.get('/investment/objective')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'objectives' in data


@pytest.mark.asyncio
async def test_check_investments_for_objectives(client, create_investment):
    """
    Created by: Lucas Penha de Moura - 21/09/2024
        This test checks the function that looks for an investment without an objective
    """
    response = await client.get('/investment/objective/not-set')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'investments' in data
    assert type(data['investments']) is list
