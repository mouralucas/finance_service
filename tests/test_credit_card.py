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
async def test_get_credit_card(client, create_credit_card):
    credit_cards = create_credit_card

    response = await client.get('/creditcard')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_create_bill(client, create_credit_card, create_category, create_currency):
    credit_cards = create_credit_card
    currencies = create_currency
    categories = create_category


    credit_card_id = str(credit_cards[0].id)
    due_date = '2024-09-20'
    transaction_date = '2024-08-25'
    amount = 112.45
    category_id = str(categories[0].id)
    currency_id = str(currencies[0].id)


