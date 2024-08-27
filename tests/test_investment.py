import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_investment(client, create_open_account, create_investment_type, create_index_type,
                                 create_index, create_liquidity, create_currency):
    accounts = create_open_account
    account = accounts[0]
    investment_types = create_investment_type
    index_types = create_index_type
    indexes = create_index
    liquidity = create_liquidity
    currencies = create_currency

    custodian_id = account.bank_id
    name = 'Investment in an asset'
    type_id = investment_types[0].id
    transaction_date = '2024-08-10'
    maturity_date = '2025-08-09'
    quantity = 1.025
    price = 1021.32
    amount = quantity * price
    index_type_id = index_types[0].id
    index_id = indexes[0].id
    liquidity_id = liquidity[0].id
    currency_id = currencies[0].id
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
        'indexTypeId': str(index_type_id),
        'indexId': str(index_id),
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

    assert 'indexTypeId' in data['investment']
    assert data['investment']['indexTypeId'] == str(index_type_id)

    assert 'indexId' in data['investment']
    assert data['investment']['indexId'] == str(index_id)

    assert 'liquidityId' in data['investment']
    assert data['investment']['liquidityId'] == str(liquidity_id)

    assert 'currencyId' in data['investment']
    assert data['investment']['currencyId'] == str(currency_id)


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


async def test_investment_statement(client, create_investment, create_tax):
    investments = create_investment

    investment_id = str(investments[0].id)
    period = 202408
    gross_amount = 35.10
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
            'name': 'IR',
            'amount': total_tax
        }
    }

    response = client.post('/investment/statement', json=payload)

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