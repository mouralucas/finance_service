import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_account(client, create_bank, create_account_type, create_currency):
    account_types = create_account_type
    banks = create_bank
    currencies = create_currency

    bank_id = banks[0].id
    nickname = 'Minha conta 1'
    branch = '2033-2'
    number = '123654897'
    open_date = '2024-08-09'
    type_id = account_types[0].id
    currency_id = currencies[0].id

    payload = {
        'bankId': str(bank_id),
        'nickname': nickname,
        'branch': branch,
        'number': number,
        'openDate': open_date,
        'accountTypeId': str(type_id),
        'currencyId': str(currency_id),
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
    assert 'currencyId' in data['account']
    assert data['account']['currencyId'] == str(currency_id)


@pytest.mark.asyncio
async def test_close_account_with_credit_card(client, create_valid_credit_card):
    """
        This test should validate the cancellation date if the account and if the attr 'active' is false
        While an account may have a credit card associated with it, the card also need to be cancelled and tested, the fields
        to validate are the same as the account
    :param client:
    :param create_valid_credit_card
    :return:
    """
    account_id = str(create_valid_credit_card[0].account_id)
    close_date = '2024-12-21'

    payload = {
        'accountId': account_id,
        'closeDate': close_date,
    }
    response = await client.patch('/account/close', json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Test the account itself
    assert 'account' in data
    assert 'accountId' in data['account']
    assert data['account']['accountId'] == account_id
    assert 'closeDate' in data['account']
    assert data['account']['closeDate'] == close_date
    assert 'active' in data['account']
    assert not data['account']['active']

    # Test the credit card
    assert 'creditCards' in data['account']
    credit_cards = data['account']['creditCards']
    for i in credit_cards:
        assert 'creditCardId' in i
        assert 'accountId' in i
        assert i['accountId'] == account_id
        assert 'cancellationDate' in i
        assert i['cancellationDate'] == close_date
        assert 'active' in i
        assert not i['active']


@pytest.mark.asyncio
async def test_get_account(client, create_open_account):
    response = await client.get('/account')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'accounts' in data
    assert type(data['accounts']) is list
    assert 'quantity' in data
    assert data['quantity'] > 0

    assert 'accountId' in data['accounts'][0]
    assert 'bankId' in data['accounts'][0]


@pytest.mark.asyncio
async def test_create_transaction(client, create_open_account, create_category, create_currency):
    accounts = create_open_account
    categories = create_category
    currencies = create_currency

    # Data only for local transaction, that means in the same currency as the account
    user_account = accounts[0]
    currency_id = currencies[0].id
    amount = 12.37
    transaction_date = '2024-08-15'
    category_id = categories[0].id
    description = 'My transaction that I made'
    operation_type = 'INCOMING'

    payload = {
        'accountId': str(user_account.id),
        'amount': amount,
        'transactionDate': transaction_date,
        'categoryId': str(category_id),
        'description': description,
        'operationType': operation_type,
    }
    response = await client.post('/account/transaction', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert 'transaction' in data
    assert 'transactionId' in data['transaction']
    assert 'ownerId' in data['transaction']

    assert 'accountId' in data['transaction']
    assert data['transaction']['accountId'] == str(user_account.id)
    assert 'period' in data['transaction']
    assert data['transaction']['period'] == 202408  # add function to calc period
    assert 'currencyId' in data['transaction']
    assert data['transaction']['currencyId'] == str(currency_id)
    assert 'amount' in data['transaction']
    assert data['transaction']['amount'] == amount
    assert 'transactionDate' in data['transaction']
    assert data['transaction']['transactionDate'] == transaction_date
    assert 'categoryId' in data['transaction']
    assert data['transaction']['categoryId'] == str(category_id)
    assert 'description' in data['transaction']
    assert data['transaction']['description'] == description

    # The transaction currency and amount must be the same in local transactions
    assert 'transactionCurrencyId' in data['transaction']
    assert data['transaction']['transactionCurrencyId'] == str(currency_id)
    assert 'transactionAmount' in data['transaction']
    assert data['transaction']['transactionAmount'] == amount


@pytest.mark.asyncio
async def test_create_transaction_closed_account(client, create_closed_account, create_category, create_currency):
    accounts = create_closed_account
    categories = create_category

    # Data only for local transaction, that means in the same currency as the account
    user_account = accounts[0]
    amount = 37.89
    transaction_date = '2024-08-25'
    category_id = categories[1].id
    description = 'My transaction that I made in a closed account'
    operation_type = 'OUTGOING'

    payload = {
        'accountId': str(user_account.id),
        'amount': amount,
        'transactionDate': transaction_date,
        'categoryId': str(category_id),
        'description': description,
        'operationType': operation_type,
    }
    response = await client.post('/account/transaction', json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_transactions(client, create_account_transaction):
    response = await client.get('/account/transaction')

    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


@pytest.mark.asyncio
async def test_create_balance(client, create_account_transaction):
    transactions = create_account_transaction

    payload = {
        'accountId': str(transactions[0].account_id),
    }
    response = await client.post('/account/balance', json=payload)

    assert response.status_code == status.HTTP_201_CREATED