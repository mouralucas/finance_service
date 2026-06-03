import datetime

import pytest
from starlette import status

from services.credit_card import CreditCardService
from services.utils.datetime import get_installments_due_dates, get_period


class TestCreditCardTransactions:
    @pytest.mark.asyncio
    async def test_get_installments_due_dates(self, client, create_valid_credit_card):
        credit_cards = create_valid_credit_card

        query = """
            query GetCreditCardInstallmentDueDates (
                $params: GetInstallmentsDueDatesInput!
            ) {
                getCreditCardInstallmentDueDates(
                    params: $params
                ) {
                    dueDates {
                        currentInstallment
                        dueDate
                    }
                }
            }
        """
        payload = {
            "transactionDate": "2024-11-11",
            "creditCardId": str(credit_cards[0].id),
            "totInstallments": 3,
        }
        response = await client.post(
            "/graphql/finance", json={"query": query, "variables": {"params": payload}}
        )
        assert response.status_code == status.HTTP_200_OK


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

    mutation = """
        mutation CreateCreditCardTransaction (
            $transaction: CreateCreditCardTransactionInput!
        ) {
            createCreditCardTransaction(
                transaction: $transaction
            ) {
                success
                ids
            }
        }
    """

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

    response = await client.post(
        "/graphql/finance",
        json={"query": mutation, "variables": {"transaction": payload}},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "data" in data
    assert "createCreditCardTransaction" in data["data"]
    assert "success" in data["data"]["createCreditCardTransaction"]
    assert len(data["data"]["createCreditCardTransaction"]["ids"]) == 1


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
    
    mutation = """
        mutation CreateCreditCardTransaction (
            $transaction: CreateCreditCardTransactionInput!
        ) {
            createCreditCardTransaction(
                transaction: $transaction
            ) {
                success
                ids
            }
        }
    """

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

    response = await client.post(
        "/graphql/finance",
        json={"query": mutation, "variables": {"transaction": payload}},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "data" in data
    assert "createCreditCardTransaction" in data["data"]
    assert "success" in data["data"]["createCreditCardTransaction"]
    assert "ids" in data["data"]["createCreditCardTransaction"]
    assert len(data["data"]["createCreditCardTransaction"]["ids"]) > 1


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
