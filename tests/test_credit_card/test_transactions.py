import datetime

import pytest
from starlette import status

from services.credit_card import CreditCardService
from services.utils.datetime import get_installments_due_dates, get_period


@pytest.mark.asyncio
async def test_create_transaction_no_installment(
    client, create_valid_credit_card, create_category, create_currency
):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # Since it's a transaction with no installments, the total amount should be
    # exact the same as the amount
    credit_card_id = str(credit_cards[0].id)
    due_day = credit_cards[0].due_day
    close_day = credit_cards[0].close_day
    transaction_date = "2024-08-25"
    total_amount = 112.45

    tot_installments = 1
    installments_dates = get_installments_due_dates(
        transaction_date=datetime.datetime.strptime(transaction_date, "%Y-%m-%d"),
        close_day=close_day,
        due_day=due_day,
        tot_installments=tot_installments,
    )

    installments = []
    for idx, installment in enumerate(installments_dates):
        installments.append(
            {
                "currentInstallment": installment["current_installment"],
                "amount": total_amount / tot_installments,
                "dueDate": str(installment["due_date"]),
            }
        )

    category_id = str(categories[0].id)
    currency_id = str(currencies[0].id)

    is_international_transaction = False
    description = "My new credit card transaction"

    payload = {
        "creditCardId": credit_card_id,
        "transactionDate": transaction_date,
        "totalAmount": total_amount,
        "totInstallments": tot_installments,
        "installments": installments,
        "categoryId": category_id,
        "currencyId": currency_id,
        "isInternationalTransaction": is_international_transaction,
        "description": description,
    }

    response = await client.post("/creditcard/transaction", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "transaction" in data
    assert type(data["transaction"]) is list
    assert len(data["transaction"]) == 1  # must be one when n installments

    entries = data["transaction"]
    for entry in entries:
        due_date = CreditCardService.set_due_date(
            datetime.datetime.strptime(transaction_date, "%Y-%m-%d").date(),
            close_day,
            due_day,
            installment=entry["currentInstallment"],
        )
        period = get_period(due_date)

        assert "transactionId" in entry

        assert "creditCardId" in entry
        assert entry["creditCardId"] == credit_card_id
        assert "period" in entry
        assert entry["period"] == period
        assert "dueDate" in entry
        assert entry["dueDate"] == due_date.strftime("%Y-%m-%d")
        assert "transactionDate" in entry
        assert entry["transactionDate"] == transaction_date
        assert "amount" in entry
        assert entry["amount"] == total_amount
        assert "categoryId" in entry
        assert entry["categoryId"] == category_id
        assert "currencyId" in entry
        assert entry["currencyId"] == currency_id
        assert "transactionCurrencyId" in entry
        assert entry["transactionCurrencyId"] == currency_id
        assert "transactionAmount" in entry
        assert entry["transactionAmount"] == total_amount

        # Installment fields
        assert "isInstallment" in entry
        assert not entry["isInstallment"]
        assert "currentInstallment" in entry
        assert entry["currentInstallment"] == 1
        assert "installments" in entry
        assert entry["installments"] == 1
        assert "totalAmount" in entry
        assert entry["totalAmount"] == total_amount


@pytest.mark.asyncio
async def test_create_transaction_with_installment(
    client, create_valid_credit_card, create_category, create_currency
):
    credit_cards = create_valid_credit_card
    currencies = create_currency
    categories = create_category

    # In a transaction with installment the total amount
    #   must be greater than the amount value
    # "amount" its basically total amount / installments
    #   (it could vary a few cents due to different forms to calculate installments)
    total_installments = 3
    credit_card_id = str(credit_cards[0].id)
    due_day = credit_cards[0].due_day
    close_day = credit_cards[0].close_day
    transaction_date = "2024-08-05"
    total_amount = 1229.99
    tot_installments = 3

    installments_dates = get_installments_due_dates(
        transaction_date=datetime.datetime.strptime(transaction_date, "%Y-%m-%d"),
        close_day=close_day,
        due_day=due_day,
        tot_installments=tot_installments,
    )

    installments = []
    for idx, installment in enumerate(installments_dates):
        installments.append(
            {
                "currentInstallment": installment["current_installment"],
                "amount": total_amount / tot_installments,
                "dueDate": str(installment["due_date"]),
            }
        )

    category_id = str(categories[1].id)
    currency_id = str(currencies[0].id)

    is_international_transaction = False
    description = "My installment transaction"

    payload = {
        "creditCardId": credit_card_id,
        "transactionDate": transaction_date,
        "totalAmount": total_amount,
        "totInstallments": tot_installments,
        "installments": installments,
        "categoryId": category_id,
        "currencyId": currency_id,
        "isInternationalTransaction": is_international_transaction,
        "description": description,
    }
    response = await client.post("/creditcard/transaction", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "transaction" in data
    assert type(data["transaction"]) is list
    assert len(data["transaction"]) == total_installments

    entries = data["transaction"]

    for idx, entry in enumerate(entries):
        due_date = CreditCardService.set_due_date(
            datetime.datetime.strptime(transaction_date, "%Y-%m-%d").date(),
            close_day,
            due_day,
            installment=entry["currentInstallment"],
        )
        period = get_period(due_date)

        assert "amount" in entry
        assert entry["amount"] == round(total_amount / total_installments, 5)

        assert "period" in entry
        assert entry["period"] == period
        assert "dueDate" in entry
        assert entry["dueDate"] == due_date.strftime("%Y-%m-%d")
        assert "isInstallment" in entry
        assert entry["isInstallment"]
        assert "currentInstallment" in entry
        assert entry["currentInstallment"] == idx + 1
        assert "installments" in entry
        assert entry["installments"] == total_installments
        assert "totalAmount" in entry
        assert entry["totalAmount"] == total_amount


@pytest.mark.asyncio
async def test_create_transaction_cancelled_card(
    client, create_cancelled_card, create_category, create_currency
):
    transaction_date = "2024-07-03"
    total_amount = 112.45
    installments = [
        {"amount": total_amount, "currentInstallment": 1, "dueDate": "2024-07-20"}
    ]
    credit_card_id = str(create_cancelled_card[0].id)
    category_id = str(create_category[0].id)
    currency_id = str(create_currency[0].id)

    payload = {
        "creditCardId": credit_card_id,
        "transactionDate": transaction_date,
        "totalAmount": total_amount,
        "totInstallments": 1,
        "installments": installments,
        "categoryId": category_id,
        "currencyId": currency_id,
        "isInternationalTransaction": False,
    }

    response = await client.post("/creditcard/transaction", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_installments_due_dates(client, create_valid_credit_card):
    credit_cards = create_valid_credit_card

    payload = {
        "transactionDate": "2024-11-11",
        "creditCardId": credit_cards[0].id,
        "totInstallments": 3,
    }
    response = await client.get(
        "creditcard/transaction/installment/due-date", params=payload
    )
    assert response.status_code == status.HTTP_200_OK
