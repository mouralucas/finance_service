import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_credit_card(client, create_open_account, create_currency):
    accounts = create_open_account
    currencies = create_currency

    account_id = accounts[0].id
    currency_id = currencies[0].id
    issue_date = '2020-02-20'
    due_day = 20
    close_day = 13

    payload = {
        'nickname': 'My new credit card',
        'accountId': str(account_id),
        'currencyId': str(currency_id),
        'issueDate': issue_date,
        'dueDay': due_day,
        'closeDay': close_day
    }
    response = await client.post('/creditcard', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert 'creditCard' in data
    assert 'accountId' in data['creditCard']
    assert data['creditCard']['accountId'] == str(account_id)

    assert 'issueDate' in data['creditCard']
    assert 'cancellationDate' in data['creditCard']

    assert 'currencyId' in data['creditCard']
    assert data['creditCard']['currencyId'] == str(currency_id)
    assert 'dueDay' in data['creditCard']
    assert data['creditCard']['dueDay'] == due_day
    assert 'closeDay' in data['creditCard']
    assert data['creditCard']['closeDay'] == close_day


@pytest.mark.asyncio
async def test_get_valid_credit_card(client, create_valid_credit_card):
    credit_cards = create_valid_credit_card
    response = await client.get('/creditcard')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'creditCards' in data
    credit_card_1 = data['creditCards'][0]

    assert 'creditCardId' in credit_card_1
    assert credit_card_1['creditCardId'] == str(credit_cards[0].id)
    assert 'nickname' in credit_card_1
    assert credit_card_1['nickname'] == credit_cards[0].nickname
    assert 'accountId' in credit_card_1
    assert credit_card_1['accountId'] == str(credit_cards[0].account_id)
    assert 'currencyId' in credit_card_1
    assert credit_card_1['currencyId'] == str(credit_cards[0].currency_id)
    assert 'issueDate' in credit_card_1
    assert credit_card_1['issueDate'] == credit_cards[0].issue_date.strftime('%Y-%m-%d')
    assert 'cancellationDate' in credit_card_1
    assert credit_card_1['cancellationDate'] is None
    assert 'dueDay' in credit_card_1
    assert credit_card_1['dueDay'] == credit_cards[0].due_day
    assert 'closeDay' in credit_card_1
    assert credit_card_1['closeDay'] == credit_cards[0].close_day


@pytest.mark.asyncio
async def test_cancel_credit_card(client, create_valid_credit_card):
    credit_cards = create_valid_credit_card

    credit_card_id = str(credit_cards[0].id)
    cancellation_date = '2024-08-20'

    payload = {
        'creditCardId': credit_card_id,
        'cancellationDate': cancellation_date
    }
    response = await client.patch('/creditcard/cancel', json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'creditCard' in data
    assert 'cancellationDate' in data['creditCard']
    assert data['creditCard']['cancellationDate'] == cancellation_date
    assert 'active' in data['creditCard']
    assert data['creditCard']['active'] is False


@pytest.mark.asyncio
async def test_get_all_transactions(client):
    pass


@pytest.mark.asyncio
async def test_get_transactions_by_period(client):
    pass
