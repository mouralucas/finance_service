import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_credit_card(client, create_open_account):
    accounts = create_open_account

    account_id = accounts[0].id

    payload = {
        'nickname': 'My new credit card',
        'accountId': str(account_id),
        'issueDate': '2020-02-20',
        'dueDate': 20,
        'closeDate': 13
    }
    response = await client.post('/creditcard', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert 'creditCard' in data
    assert 'accountId' in data['creditCard']
    assert data['creditCard']['accountId'] == str(account_id)
