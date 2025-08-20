
import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_investment(client, create_open_account, create_fixed_income_br_investment_type, create_indexer_type,
                                 create_indexer, create_liquidity, create_country):
    accounts = create_open_account
    account = accounts[0]
    investment_types = create_fixed_income_br_investment_type
    indexer_types = create_indexer_type
    indexers = create_indexer
    liquidity = create_liquidity
    currency_id = accounts[0].currency_id

    name = 'Investment in an asset'
    type_id = investment_types[0].id
    transaction_date = '2024-08-10'
    maturity_date = '2025-08-09'
    quantity = 1.025
    price = 1021.32
    amount = quantity * price
    contracted_rate = '10%'
    indexer_type_id = indexer_types[0].id
    indexer_id = indexers[0].id
    liquidity_id = liquidity[0].id
    currency_id = currency_id
    country_id = 'BR'

    payload = {
        'accountId': str(account.id),
        'name': name,
        'investmentTypeId': str(type_id),
        'transactionDate': transaction_date,
        'maturityDate': maturity_date,
        'quantity': quantity,
        'price': price,
        'amount': amount,
        'contractedRate': contracted_rate,
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

    assert 'investmentTypeId' in data['investment']
    assert data['investment']['investmentTypeId'] == str(type_id)

    assert 'transactionDate' in data['investment']
    assert data['investment']['transactionDate'] == transaction_date

    assert 'maturityDate' in data['investment']
    assert data['investment']['maturityDate'] == maturity_date

    assert 'quantity' in data['investment']
    assert float(data['investment']['quantity']) == quantity

    assert 'price' in data['investment']
    assert float(data['investment']['price']) == price

    assert 'amount' in data['investment']
    assert float(data['investment']['amount']) == amount

    assert 'indexerTypeId' in data['investment']
    assert data['investment']['indexerTypeId'] == str(indexer_type_id)

    assert 'indexerId' in data['investment']
    assert data['investment']['indexerId'] == str(indexer_id)

    assert 'liquidityId' in data['investment']
    assert data['investment']['liquidityId'] == str(liquidity_id)

    assert 'currencyId' in data['investment']
    assert data['investment']['currencyId'] == str(currency_id)

    assert 'isSettled' in data['investment']
    assert data['investment']['isSettled'] is False


@pytest.mark.asyncio
async def test_create_settled_investment(client, create_open_account, create_fixed_income_br_investment_type, create_indexer_type,
                                            create_indexer, create_liquidity, create_currency, create_country):
    accounts = create_open_account

    custodian_id = accounts[0].bank_id
    name = 'Investment already liquidated'
    type_id = create_fixed_income_br_investment_type[0].id
    transaction_date = '2022-07-04'
    maturity_date = '2024-08-01'
    quantity = 1
    price = 112.47
    amount = quantity * price
    contracted_rate = '115% do CDI'
    # TODO: add tax and fee details to the payload
    # tax_detail = [{
    #     'currencyId': 'BRL',
    #     'id': 'a6c45a5a-f75f-475c-afa1-1cf02cd3fd04',
    #     'amount': amount * 0.15
    # }]
    # fee_detail = [
    #     {
    #         'currencyId': 'BRL',
    #         'id': 'a187d754-73c9-46d3-ac57-7cc78ea01e6f',
    #         'amount': amount * 0.01
    #     }
    # ]
    indexer_type_id = create_indexer_type[0].id
    indexer_id = create_indexer[0].id
    liquidity_id = create_liquidity[0].id
    currency_id = create_currency[0].id
    country_id = 'BR'
    settlement_date = '2024-08-01'
    settlement_amount = price + (price * 0.2)  # (about 20%)

    payload = {
        'custodianId': str(custodian_id),
        'accountId': str(accounts[0].id),
        'name': name,
        'investmentTypeId': str(type_id),
        'transactionDate': transaction_date,
        'maturityDate': maturity_date,
        'quantity': quantity,
        'price': price,
        'amount': amount,
        'contractedRate': contracted_rate,
        'currencyId': str(currency_id),
        'indexerTypeId': str(indexer_type_id),
        'indexerId': str(indexer_id),
        'liquidityId': str(liquidity_id),
        'countryId': country_id,
        'settlementDate': settlement_date,
        'settlementAmount': settlement_amount
    }
    response = await client.post('/investment', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert 'investment' in data

    assert 'settlementDate' in data['investment']
    assert data['investment']['settlementDate'] == settlement_date
    assert 'settlementAmount' in data['investment']
    assert float(data['investment']['settlementAmount']) == settlement_amount
    assert 'isSettled' in data['investment']
    assert data['investment']['isSettled'] is True


@pytest.mark.asyncio
async def test_settle_investment(client, create_active_investment):
    investments = create_active_investment

    investment_id = investments[0].id
    settlement_date = '2025-08-09'
    gross_amount = 300.54
    net_amount = 250.32
    settlement_amount = 250.32
    tax_detail = [
        {
            'currencyId': 'BRL',
            'taxFeeId': 'a6c45a5a-f75f-475c-afa1-1cf02cd3fd04',
            'amount': settlement_amount * 0.15
        }
    ]
    fee_detail = [
        {
            'currencyId': 'BRL',
            'taxFeeId': 'a187d754-73c9-46d3-ac57-7cc78ea01e6f',
            'amount': settlement_amount * 0.01
        }
    ]

    payload = {
        'investmentId': str(investment_id),
        'settlementDate': settlement_date,
        'settlementAmount': settlement_amount,
        'grossAmount': gross_amount,
        'netAmount': net_amount,
        'taxDetail': tax_detail,
        'feeDetail': fee_detail
    }
    response = await client.post('/investment/settle', json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'investment' in data
    assert 'isSettled' in data['investment']
    assert data['investment']['isSettled'] is True
    assert 'settlementDate' in data['investment']
    assert data['investment']['settlementDate'] == settlement_date
    assert 'settlementAmount' in data['investment']
    assert float(data['investment']['settlementAmount']) == settlement_amount


@pytest.mark.asyncio
async def test_get_active_investments(client, create_active_investment, create_settled_investment):
    active_investments = create_active_investment
    len_active_investments = len(active_investments)
    len_settled_investments = len(create_settled_investment)
    len_all_investments = len_active_investments + len_settled_investments

    payload = {
        'isSettled': False
    }
    response = await client.get('/investment', params=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'investments' in data

    assert len(data['investments']) <= len_all_investments
    assert len(data['investments']) == len_active_investments

    for invstment in data['investments']:
        assert 'isSettled' in invstment
        assert invstment['isSettled'] is False
        assert 'settlementDate' in invstment
        assert invstment['settlementDate'] is None
        assert 'settlementAmount' in invstment
        assert invstment['settlementAmount'] is None

@pytest.mark.asyncio
async def test_get_settled_investments(client, create_active_investment, create_settled_investment):
    active_investments = create_active_investment
    len_active_investments = len(active_investments)
    len_settled_investments = len(create_settled_investment)
    len_all_investments = len_active_investments + len_settled_investments

    payload = {
        'isSettled': True
    }
    response = await client.get('/investment', params=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'investments' in data

    assert len(data['investments']) <= len_all_investments
    assert len(data['investments']) == len_settled_investments

    for invstment in data['investments']:
        assert 'isSettled' in invstment
        assert invstment['isSettled'] is True
        assert 'settlementDate' in invstment
        assert invstment['settlementDate'] is not None
        assert 'settlementAmount' in invstment
        assert invstment['settlementAmount'] is not None