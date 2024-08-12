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
        'liquidityId': str(liquidity_id)
    }
    response = await client.post('/investment', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
