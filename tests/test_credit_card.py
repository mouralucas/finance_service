import pytest
from starlette import status
import datetime
from services.credit_card import CreditCardService
from services.utils.datetime import get_period


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


####### Credit Card Transactions Tests #######
@pytest.mark.asyncio
async def test_create_transaction_no_installment(client, create_valid_credit_card, create_category, create_currency):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # Since it's a transaction with no installments, the total amount should be
    # exact the same as the amount
    credit_card_id = str(credit_cards[0].id)
    due_day = credit_cards[0].due_day
    close_day = credit_cards[0].close_day
    transaction_date = '2024-08-25'
    total_amount = 112.45
    installments = [
        {
            'amount': total_amount,
            'currentInstallment': 1,
            'installments': 1
        }
    ]
    category_id = str(categories[0].id)
    currency_id = str(currencies[0].id)

    is_international_transaction = False
    description = 'My new credit card transaction'
    operation_type = 'INCOMING'

    payload = {
        'creditCardId': credit_card_id,
        'transactionDate': transaction_date,
        'totalAmount': total_amount,
        'installments': installments,
        'categoryId': category_id,
        'currencyId': currency_id,
        'isInternationalTransaction': is_international_transaction,
        'description': description,
        'operationType': operation_type
    }

    response = await client.post('/creditcard/bill', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'transaction' in data
    assert type(data['transaction']) is list
    assert len(data['transaction']) == 1  # must be one when n installments

    entries = data['transaction']
    for entry in entries:
        due_date = CreditCardService.set_due_date(datetime.datetime.strptime(transaction_date, "%Y-%m-%d").date(), close_day, due_day, installment=entry['currentInstallment'])
        period = get_period(due_date)

        assert 'transactionId' in entry

        assert 'creditCardId' in entry
        assert entry['creditCardId'] == credit_card_id
        assert 'period' in entry
        assert entry['period'] == period
        assert 'dueDate' in entry
        assert entry['dueDate'] == due_date.strftime('%Y-%m-%d')
        assert 'transactionDate' in entry
        assert entry['transactionDate'] == transaction_date
        assert 'amount' in entry
        assert entry['amount'] == total_amount
        assert 'categoryId' in entry
        assert entry['categoryId'] == category_id
        assert 'currencyId' in entry
        assert entry['currencyId'] == currency_id
        assert 'transactionCurrencyId' in entry
        assert entry['transactionCurrencyId'] == currency_id
        assert 'transactionAmount' in entry
        assert entry['transactionAmount'] == total_amount

        # Installment fields
        assert 'isInstallment' in entry
        assert not entry['isInstallment']
        assert 'currentInstallment' in entry
        assert entry['currentInstallment'] == 1
        assert 'installments' in entry
        assert entry['installments'] == 1
        assert 'totalAmount' in entry
        assert entry['totalAmount'] == total_amount


@pytest.mark.asyncio
async def test_create_transaction_with_installment(client, create_valid_credit_card, create_category, create_currency):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # In a transaction with installment the total amount must be greater than the amount value
    # "amount" its basically total amount / installments (it could vary a few cents due to different forms to calculate installments)
    total_installments = 3
    credit_card_id = str(credit_cards[0].id)
    due_day = credit_cards[0].due_day
    close_day = credit_cards[0].close_day
    transaction_date = '2024-08-05'

    total_amount = 1229.99
    installments = [
        {
            'amount': total_amount / 3,
            'currentInstallment': 1,
            'installments': total_installments
        },
        {
            'amount': total_amount / 3,
            'currentInstallment': 2,
            'installments': total_installments
        },
        {
            'amount': total_amount / 3,
            'currentInstallment': 3,
            'installments': total_installments
        }
    ]
    category_id = str(categories[1].id)
    currency_id = str(currencies[0].id)

    is_international_transaction = False
    description = 'My installment transaction'
    operation_type = 'INCOMING'

    payload = {
        'creditCardId': credit_card_id,
        'transactionDate': transaction_date,
        'totalAmount': total_amount,
        'installments': installments,
        'categoryId': category_id,
        'currencyId': currency_id,
        'isInternationalTransaction': is_international_transaction,
        'description': description,
        'operationType': operation_type
    }
    response = await client.post('/creditcard/bill', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'transaction' in data
    assert type(data['transaction']) is list
    assert len(data['transaction']) == total_installments

    entries = data['transaction']

    for idx, entry in enumerate(entries):
        due_date = CreditCardService.set_due_date(datetime.datetime.strptime(transaction_date, "%Y-%m-%d").date(), close_day, due_day, installment=entry['currentInstallment'])
        period = get_period(due_date)

        assert 'amount' in entry
        assert entry['amount'] == total_amount / total_installments

        assert 'period' in entry
        assert entry['period'] == period
        assert 'dueDate' in entry
        assert entry['dueDate'] == due_date.strftime('%Y-%m-%d')
        assert 'isInstallment' in entry
        assert entry['isInstallment']
        assert 'currentInstallment' in entry
        assert entry['currentInstallment'] == idx + 1
        assert 'installments' in entry
        assert entry['installments'] == total_installments
        assert 'totalAmount' in entry
        assert entry['totalAmount'] == total_amount


@pytest.mark.asyncio
async def test_create_transaction_cancelled_card(client, create_cancelled_card, create_category, create_currency):
    transaction_date = '2024-07-03'
    total_amount = 112.45
    installments = [
        {
            'amount': total_amount,
            'currentInstallment': 1,
            'installments': 1
        }
    ]
    credit_card_id = str(create_cancelled_card[0].id)
    category_id = str(create_category[0].id)
    currency_id = str(create_currency[0].id)

    payload = {
        'creditCardId': credit_card_id,
        'transactionDate': transaction_date,
        'totalAmount': total_amount,
        'installments': installments,
        'categoryId': category_id,
        'currencyId': currency_id,
        'isInternationalTransaction': False,
        'operationType': 'OUTGOING'
    }

    response = await client.post('/creditcard/bill', json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_all_transactions(client):
    pass

@pytest.mark.asyncio
async def test_get_transactions_by_period(client):
    pass