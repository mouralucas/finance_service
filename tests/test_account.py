from datetime import datetime

import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_account(client, create_bank, create_account_type):
    account_types = create_account_type
    banks = create_bank

    bank_id = banks[0].id
    nickname = 'Minha conta 1'
    branch = '2033-2'
    number = '123654897'
    open_date = '2024-08-09'
    type_id = account_types[0].id

    payload = {
        'bankId': str(bank_id),
        'nickname': nickname,
        'branch': branch,
        'number': number,
        'openDate': open_date,
        'accountTypeId': str(type_id),
    }
    response = await client.post('/account', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'account' in data

    assert 'bankId' in data['account']
    assert data['account']['bankId'] == str(bank_id)
    assert 'nickname' in data['account']
    assert data['account']['nickname'] == nickname
    assert 'branch' in data['account']
    assert data['account']['branch'] == branch
    assert 'number' in data['account']
    assert data['account']['number'] == number
    assert 'openDate' in data['account']
    assert data['account']['openDate'] == open_date
    assert 'typeId' in data['account']
    assert data['account']['typeId'] == str(type_id)
