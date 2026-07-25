import pytest
from starlette import status


class TestInvestments:

    @pytest.mark.asyncio
    async def test_create_investment(
        self,
        client,
        create_open_account,
        create_fixed_income_br_investment_type,
        create_indexer_type,
        create_indexer,
        create_liquidity,
        create_country,
    ):
        accounts = create_open_account
        account = accounts[0]
        investment_types = create_fixed_income_br_investment_type
        indexer_types = create_indexer_type
        indexers = create_indexer
        liquidity = create_liquidity
        currency_id = accounts[0].currency_id

        name = "Investment in an asset"
        type_id = investment_types[0].id
        transaction_date = "2024-08-10"
        maturity_date = "2025-08-09"
        quantity = 1.025
        price = 1021.32
        amount = quantity * price
        contracted_rate = "10%"
        indexer_type_id = indexer_types[0].id
        indexer_id = indexers[0].id
        liquidity_id = liquidity[0].id
        currency_id = currency_id
        country_id = "BR"

        payload = {
            "accountId": str(account.id),
            "name": name,
            "typeId": str(type_id),
            "transactionDate": transaction_date,
            "maturityDate": maturity_date,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "contractedRate": contracted_rate,
            "currencyId": str(currency_id),
            "indexerTypeId": str(indexer_type_id),
            "indexerId": str(indexer_id),
            "liquidityId": str(liquidity_id),
            "countryId": country_id,
        }
        response = await client.post("/investment", json=payload)

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert "investment" in data

        assert "investmentId" in data["investment"]

        assert "accountId" in data["investment"]
        assert data["investment"]["accountId"] == str(account.id)

        assert "name" in data["investment"]
        assert data["investment"]["name"] == name

        # Todo: refactor to return typeId
        assert "investmentTypeId" in data["investment"]
        assert data["investment"]["investmentTypeId"] == str(type_id)

        assert "transactionDate" in data["investment"]
        assert data["investment"]["transactionDate"] == transaction_date

        assert "maturityDate" in data["investment"]
        assert data["investment"]["maturityDate"] == maturity_date

        assert "quantity" in data["investment"]
        assert float(data["investment"]["quantity"]) == quantity

        assert "price" in data["investment"]
        assert float(data["investment"]["price"]) == price

        assert "amount" in data["investment"]
        assert float(data["investment"]["amount"]) == amount

        assert "indexerTypeId" in data["investment"]
        assert data["investment"]["indexerTypeId"] == str(indexer_type_id)

        assert "indexerId" in data["investment"]
        assert data["investment"]["indexerId"] == str(indexer_id)

        assert "liquidityId" in data["investment"]
        assert data["investment"]["liquidityId"] == str(liquidity_id)

        assert "currencyId" in data["investment"]
        assert data["investment"]["currencyId"] == str(currency_id)

        assert "isSettled" in data["investment"]
        assert data["investment"]["isSettled"] is False

    @pytest.mark.asyncio
    async def test_create_settled_investment(
        self,
        client,
        create_open_account,
        create_fixed_income_br_investment_type,
        create_indexer_type,
        create_indexer,
        create_liquidity,
        create_currency,
        create_country,
    ):
        accounts = create_open_account

        custodian_id = accounts[0].bank_id
        name = "Investment already liquidated"
        type_id = create_fixed_income_br_investment_type[0].id
        transaction_date = "2022-07-04"
        maturity_date = "2024-08-01"
        quantity = 1
        price = 112.47
        amount = quantity * price
        contracted_rate = "115% do CDI"
        indexer_type_id = create_indexer_type[0].id
        indexer_id = create_indexer[0].id
        liquidity_id = create_liquidity[0].id
        currency_id = create_currency[0].id
        country_id = "BR"
        settlement_date = "2024-08-01"
        settlement_amount = price + (price * 0.2)  # (about 20%)

        payload = {
            "custodianId": str(custodian_id),
            "accountId": str(accounts[0].id),
            "name": name,
            "typeId": str(type_id),
            "transactionDate": transaction_date,
            "maturityDate": maturity_date,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "contractedRate": contracted_rate,
            "currencyId": str(currency_id),
            "indexerTypeId": str(indexer_type_id),
            "indexerId": str(indexer_id),
            "liquidityId": str(liquidity_id),
            "countryId": country_id,
            "settlementDate": settlement_date,
            "settlementAmount": settlement_amount,
        }
        response = await client.post("/investment", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "investment" in data

        assert "settlementDate" in data["investment"]
        assert data["investment"]["settlementDate"] == settlement_date
        assert "settlementAmount" in data["investment"]
        assert float(data["investment"]["settlementAmount"]) == settlement_amount
        assert "isSettled" in data["investment"]
        assert data["investment"]["isSettled"] is True

    @pytest.mark.asyncio
    async def test_get_investment_type(
        self, client, create_fixed_income_br_investment_type
    ):

        query = """
            query GetInvestmentTypes {
                getInvestmentTypes {
                    quantity
                    investmentTypes {
                        id
                        name
                        description
                        parentId
                        investmentCategoryId
                    }
                }
            }
        """
        response = await client.post("/graphql/finance", json={"query": query})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "getInvestmentTypes" in data["data"]
        assert "investmentTypes" in data["data"]["getInvestmentTypes"]
        data = data["data"]["getInvestmentTypes"]
        assert type(data) is dict
        assert "investmentTypes" in data
        assert type(data["investmentTypes"]) is list

        for investment_type in data["investmentTypes"]:
            assert "name" in investment_type
