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
async def test_get_credit_card(client, create_valid_credit_card):
    credit_cards = create_valid_credit_card

    response = await client.get('/creditcard')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_create_bill_no_installment(client, create_valid_credit_card, create_category, create_currency):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # Since it's a transaction with no installments, the total amount should be
    # exact the same as the amount
    credit_card_id = str(credit_cards[0].id)
    due_date = '2024-09-20'
    transaction_date = '2024-08-25'
    total_amount = 112.45
    installments = [
        {
            'amount': total_amount,
            'dueDate': due_date,
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
    assert 'billEntry' in data
    assert type(data['billEntry']) is list
    assert len(data['billEntry']) == 1  # must be one when n installments

    entry_1 = data['billEntry'][0]

    assert 'billEntryId' in entry_1

    assert 'creditCardId' in entry_1
    assert entry_1['creditCardId'] == credit_card_id
    assert 'period' in entry_1
    # assert correct period
    assert 'dueDate' in entry_1
    # assert correct due_date
    assert 'transactionDate' in entry_1
    assert entry_1['transactionDate'] == transaction_date
    assert 'amount' in entry_1
    assert entry_1['amount'] == total_amount
    assert 'categoryId' in entry_1
    assert entry_1['categoryId'] == category_id
    assert 'currencyId' in entry_1
    assert entry_1['currencyId'] == currency_id
    assert 'transactionCurrencyId' in entry_1
    assert entry_1['transactionCurrencyId'] == currency_id
    assert 'transactionAmount' in entry_1
    assert entry_1['transactionAmount'] == total_amount

    # Installment fields
    assert 'isInstallment' in entry_1
    assert not entry_1['isInstallment']
    assert 'currentInstallment' in entry_1
    assert entry_1['currentInstallment'] == 1
    assert 'installments' in entry_1
    assert entry_1['installments'] == 1
    assert 'totalAmount' in entry_1
    assert entry_1['totalAmount'] == total_amount


@pytest.mark.asyncio
async def test_create_bill_with_installment(client, create_valid_credit_card, create_category, create_currency):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # In a transaction with installment the total amount must be greater than the amount value
    # "amount" its basically total amount / installments (it could vary a few cents due to different forms to calculate installments)
    total_installments = 3
    credit_card_id = str(credit_cards[0].id)
    due_date = '2024-09-20'
    transaction_date = '2024-08-05'
    total_amount = 1229.99
    installments = [
        {
            'amount': total_amount / 3,
            'dueDate': due_date,
            'currentInstallment': 1,
            'installments': total_installments
        },
        {
            'amount': total_amount / 3,
            'dueDate': due_date,
            'currentInstallment': 2,
            'installments': total_installments
        },
        {
            'amount': total_amount / 3,
            'dueDate': due_date,
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
    assert 'billEntry' in data
    assert type(data['billEntry']) is list
    assert len(data['billEntry']) == total_installments

    entry_1 = data['billEntry'][0]
    entry_2 = data['billEntry'][1]
    entry_3 = data['billEntry'][2]

    # Test each entry
    assert 'amount' in entry_1
    assert entry_1['amount'] == total_amount/total_installments

    # TODO add test for the due date and period!!
    assert 'isInstallment' in entry_1
    assert entry_1['isInstallment']
    assert 'currentInstallment' in entry_1
    assert entry_1['currentInstallment'] == 1
    assert 'installments' in entry_1
    assert entry_1['installments'] == total_installments
    assert 'totalAmount' in entry_1
    assert entry_1['totalAmount'] == total_amount

    assert 'amount' in entry_2
    assert entry_2['amount'] == total_amount / total_installments

    assert 'isInstallment' in entry_2
    assert entry_2['isInstallment']
    assert 'currentInstallment' in entry_2
    assert entry_2['currentInstallment'] == 2
    assert 'installments' in entry_2
    assert entry_2['installments'] == total_installments
    assert 'totalAmount' in entry_2
    assert entry_2['totalAmount'] == total_amount

    assert 'amount' in entry_3
    assert entry_3['amount'] == total_amount / total_installments

    assert 'isInstallment' in entry_3
    assert entry_3['isInstallment']
    assert 'currentInstallment' in entry_3
    assert entry_3['currentInstallment'] == 3
    assert 'installments' in entry_3
    assert entry_3['installments'] == total_installments
    assert 'totalAmount' in entry_3
    assert entry_3['totalAmount'] == total_amount
