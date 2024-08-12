import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_investment(client, create_open_account):
    accounts = create_open_account

    account = accounts[0]
    custodian_id = account.bank_id
    name = 'Investment in an asset'
    type_id = ''  # create type id mock
    transaction_date = '2024-08-10'
    maturity_date = '2025-08-09'
    quantity = 1.025
    price = 1021.32
    amount = quantity * price
    interest_rate = '' # maybe a table? If so, create mock
    index_id = ''
    liquidity_id = ''

    payload = {
        'custodianId': custodian_id,
        'accountId': account.id,
        'name': name,
        'typeId': type_id,
        'transactionDate': transaction_date,
        'maturityDate': maturity_date,
        'quantity': quantity,
        'price': price,
        'amount': amount,
        'interestRate': interest_rate,
        'indexId': index_id,
        'liquidityId': liquidity_id
    }
    response = await client.post('/investment', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
