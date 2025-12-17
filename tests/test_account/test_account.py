import pytest
from starlette import status

from schemas.account import AccountTransactionSchema


class TestAccount:
    @pytest.mark.asyncio
    async def test_create_account(
        self, client, create_bank, create_account_type_beta, create_currency_factory
    ):
        account_types = create_account_type_beta
        banks = create_bank
        currencies = create_currency_factory

        bank_id = banks[0].id
        nickname = "Minha conta 1"
        branch = "2033-2"
        number = "123654897"
        open_date = "2024-08-09"
        type_id = account_types[0].id
        currency_id = currencies[0].id

        payload = {
            "bankId": str(bank_id),
            "nickname": nickname,
            "branch": branch,
            "number": number,
            "openDate": open_date,
            "accountTypeId": str(type_id),
            "currencyId": str(currency_id),
        }
        response = await client.post("/account", json=payload)

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "account" in data

        assert "bankId" in data["account"]
        assert data["account"]["bankId"] == str(bank_id)
        assert "nickname" in data["account"]
        assert data["account"]["nickname"] == nickname
        assert "branch" in data["account"]
        assert data["account"]["branch"] == branch
        assert "number" in data["account"]
        assert data["account"]["number"] == number
        assert "openDate" in data["account"]
        assert data["account"]["openDate"] == open_date
        assert "typeId" in data["account"]
        assert data["account"]["typeId"] == str(type_id)
        assert "currencyId" in data["account"]
        assert data["account"]["currencyId"] == str(currency_id)

    @pytest.mark.asyncio
    async def test_get_account(self, client, create_open_account):
        query = """
            query GetAccounts {
                getAccounts {
                    quantity
                    accounts {
                        accountId
                        active
                        bankId
                        nickname
                        description
                        branch
                        number
                        openDate
                        closeDate
                        typeId
                        currencyId
                        currencySymbol
                    }
                }
            }
        """

        response = await client.post("/graphql/finance", json={"query": query})

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert "data" in data
        assert "getAccounts" in data["data"]
        assert "accounts" in data["data"]["getAccounts"]
        assert type(data["data"]["getAccounts"]["accounts"]) is list
        assert "quantity" in data["data"]["getAccounts"]
        assert data["data"]["getAccounts"]["quantity"] > 0

        for i in data["data"]["getAccounts"]["accounts"]:
            assert "accountId" in i
            assert "bankId" in i
            assert "nickname" in i

    @pytest.mark.asyncio
    async def test_account_factory(self, client, create_account_type_beta):
        print(create_account_type_beta)


class TestAccountsStatement:

    @pytest.mark.asyncio
    async def test_update_transaction(self, client, create_account_transaction):
        transaction: AccountTransactionSchema = create_account_transaction[0]

        new_amount = transaction.amount - 12.35

        payload = {"transactionId": transaction.id, "amount": new_amount}
        response = await client.patch("/account/transaction", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "transaction" in data
        assert "amount" in data["transaction"]
        assert round(data["transaction"]["amount"], 5) == round(new_amount, 5)


@pytest.mark.asyncio
async def test_close_account_with_credit_card(client, create_valid_credit_card):
    """
        This test should validate the cancellation date if the
            account and if the attr 'active' is false
        While an account may have a credit card associated with it,
            the card also need to be cancelled and tested, the fields
            to validate are the same as the account
    :param client:
    :param create_valid_credit_card
    :return:
    """
    account_id = str(create_valid_credit_card[0].account_id)
    close_date = "2024-12-21"

    payload = {
        "accountId": account_id,
        "closeDate": close_date,
    }
    response = await client.patch("/account/close", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Test the account itself
    assert "account" in data
    assert "accountId" in data["account"]
    assert data["account"]["accountId"] == account_id
    assert "closeDate" in data["account"]
    assert data["account"]["closeDate"] == close_date
    assert "active" in data["account"]
    assert not data["account"]["active"]

    # Test the credit card
    assert "creditCards" in data["account"]
    credit_cards = data["account"]["creditCards"]
    for i in credit_cards:
        assert "creditCardId" in i
        assert "accountId" in i
        assert i["accountId"] == account_id
        assert "cancellationDate" in i
        assert i["cancellationDate"] == close_date
        assert "active" in i
        assert not i["active"]


@pytest.mark.asyncio
async def test_create_transaction(
    client, create_open_account, create_category, create_currency
):
    accounts = create_open_account
    categories = create_category
    currencies = create_currency

    # Data only for local transaction, that means in the same currency as the account
    user_account = accounts[0]
    currency_id = currencies[0].id
    amount = 12.37
    transaction_date = "2024-08-15"
    category_id = categories[0].id
    description = "My transaction that I made"

    query = """
        mutation CreateAccountTransaction (
                $transaction: CreateAccountTransactionInput!
            ) {
            createAccountTransaction(
                transaction: $transaction
            ) {
                success
                transactionId
            }
        }
    """

    payload = {
        "accountId": str(user_account.id),
        "currencyId": currency_id,
        "amount": amount,
        "transactionDate": transaction_date,
        "categoryId": str(category_id),
        "description": description,
    }
    response = await client.post(
        "graphql/finance", json={"query": query, "variables": {"transaction": payload}}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "data" in data
    assert "createAccountTransaction" in data["data"]
    assert "success" in data["data"]["createAccountTransaction"]
    assert data["data"]["createAccountTransaction"]["success"] is True
    assert "transactionId" in data["data"]["createAccountTransaction"]
    assert data["data"]["createAccountTransaction"]["transactionId"] is not None


@pytest.mark.asyncio
async def test_create_transaction_closed_account(
    client, create_closed_account, create_category, create_currency
):
    accounts = create_closed_account
    categories = create_category
    currencies = create_currency

    # Data only for local transaction, that means in the same currency as the account
    user_account = accounts[0]
    currency_id = currencies[0].id
    amount = 37.89
    transaction_date = "2024-08-25"
    category_id = categories[1].id
    description = "My transaction that I made in a closed account"

    query = """
        mutation CreateAccountTransaction (
                $transaction: CreateAccountTransactionInput!
            ) {
            createAccountTransaction(
                transaction: $transaction
            ) {
                success
                transactionId
            }
        }
    """

    payload = {
        "accountId": str(user_account.id),
        "currencyId": currency_id,
        "amount": amount,
        "transactionDate": transaction_date,
        "categoryId": str(category_id),
        "description": description,
    }
    response = await client.post(
        "/graphql/finance", json={"query": query, "variables": {"transaction": payload}}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data
    assert data["errors"][0]["message"] == "403: Account not found or not active"


@pytest.mark.asyncio
async def test_get_transactions_no_filter(client, create_account_transaction):
    query = """
        query GetAccountTransactions {
            getAccountTransactions {
                quantity
                transactions {
                    transactionId
                    ownerId
                }
            }
        }
    """
    response = await client.post("/graphql/finance", json={"query": query})
    # TODO: this returns 200 but there is errors: why cannot send without filters if
    # not required?
    assert response.status_code == status.HTTP_200_OK