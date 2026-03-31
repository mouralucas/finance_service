import pytest
from starlette import status

from schemas.investment_deprecated import InvestmentSchema, InvestmentStatementSchema
from services.utils.datetime import get_period


class TestStatement:

    @pytest.mark.asyncio
    async def test_create_first_investment_statement(
        self, client, create_active_investment, create_tax
    ):
        """
            The first statement should have the same period as the investment
        :param client:
        :param create_investment:
        :param create_tax:
        :return:
        """
        investments = create_active_investment

        investment_id = str(investments[0].id)
        period = get_period(investments[0].transaction_date)
        gross_amount = 35.10
        tax_total = 0.21
        tax_details = [
            {
                "currencyId": "BRL",
                "taxFeeId": str(create_tax[0].id),
                "amount": tax_total,
            }
        ]

        net_amount = gross_amount - sum(tax["amount"] for tax in tax_details)

        mutation = """
            mutation CreateInvestmentStatement (
                $statement: CreateInvestmentStatementInput
            ) {
                createInvestmentStatement(statement: $statement) {
                    created
                    statementId
                }
            }
        """

        payload = {
            "investmentId": investment_id,
            "period": period,
            "referenceDate": investments[0].transaction_date.strftime("%Y-%m-%d"),
            "withdrawn": 0,
            "contribution": investments[0].amount,
            "grossAmount": gross_amount,
            "netAmount": net_amount,
        }

        response = await client.post(
            "/graphql/finance",
            json={"query": mutation, "variables": {"statement": payload}},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "data" in data
        assert "createInvestmentStatement" in data["data"]
        data = data["data"]["createInvestmentStatement"]
        assert "created" in data
        assert data["created"] is True

        query = """
            query GetInvestmentStatements($params: GetInvestmentStatementsInput){
                getInvestmentStatements(params: $params) {
                    quantity
                    statements {
                        id
                        investmentId
                        period
                        contribution
                        previousAmount
                        grossAmount
                        totalTax
                        totalFee
                        referenceDate
                        atMaturity
                        valueChange
                        percentageChange
                        netAmount
                    }
                }
            }
        """
        params = {"params": {"investmentId": investment_id}}
        response = await client.post(
            "/graphql/finance", json={"query": query, "variables": params}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "data" in data
        assert "getInvestmentStatements" in data["data"]
        assert "quantity" in data["data"]["getInvestmentStatements"]
        assert "statements" in data["data"]["getInvestmentStatements"]

        data = data["data"]["getInvestmentStatements"]

        # Should only have one, since it is the first statement
        assert data["quantity"] == 1
        assert len(data["statements"]) == 1

        for statement in data["statements"]:
            assert "investmentId" in statement
            assert statement["investmentId"] == investment_id

            assert "contribution" in statement
            assert statement["contribution"] == investments[0].amount

            # TODO: add taxDetails and feeDetails validation again
            # assert "taxDetail" in statement
            # assert type(statement["taxDetail"]) is list
            # assert "feeDetail" in statement

            # assert "totalTax" in statement
            # assert statement["totalTax"] == tax_total
            # assert "totalFee" in statement

    # TODO: for this one add as not first statement, create mock to other statements
    @pytest.mark.asyncio
    async def test_create_investment_statement(self, client, create_active_investment):
        investments = create_active_investment
        mutation = """
            mutation CreateInvestmentStatement (
                $statement: CreateInvestmentStatementInput
            ) {
                createInvestmentStatement(statement: $statement) {
                    created
                    statementId
                }
            }
        """

        variables = {
            "statement": {
                "investmentId": str(investments[0].id),
                "period": get_period(investments[0].transaction_date),
                "referenceDate": investments[0].transaction_date.strftime("%Y-%m-%d"),
                "grossAmount": investments[0].amount * 1.05,
                "netAmount": (investments[0].amount * 1.05) - 3.60,
                "withdrawn": 0,
                "contribution": investments[0].amount,
                # TODO: add taxDetails and feeDetails
            }
        }

        response = await client.post(
            "/graphql/finance",
            json={"query": mutation, "variables": variables},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "errors" not in data

        assert "data" in data
        assert "createInvestmentStatement" in data["data"]
        created_info = data["data"]["createInvestmentStatement"]
        assert created_info.get("created") is True
        assert "statementId" in created_info

    @pytest.mark.asyncio
    async def test_get_investment_statements(self, client):
        assert True

    @pytest.mark.asyncio
    async def test_update_investment_statement(
        self, client, create_active_investment, create_investment_statement
    ):
        statement: InvestmentStatementSchema = create_investment_statement[0]

        new_gross_amount = statement.gross_amount + 1.25

        mutation = """
            mutation UpdateStatement($statementId: String!, $grossAmount: Float!) {
                updateInvestmentStatement(statement: { statementId: $statementId,
                                            grossAmount: $grossAmount }) {
                    updated
                    statementId
                }
            }
        """
        variables = {"statementId": str(statement.id), "grossAmount": new_gross_amount}

        response = await client.post(
            "/graphql/finance",
            json={"query": mutation, "variables": variables},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "errors" not in data
        assert data["data"]["updateInvestmentStatement"]["updated"] is True
        assert data["data"]["updateInvestmentStatement"]["statementId"] == str(
            statement.id
        )

        query = """
            query GetInvestmentStatement(
                $params: GetInvestmentStatementInput!
            ) {
                getInvestmentStatement(params: $params) {
                    statement {
                        id
                        grossAmount
                    }
                }
            }
        """
        p = {"params": {"id": str(statement.id)}}

        response = await client.post(
            "/graphql/finance",
            json={"query": query, "variables": p},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        updated_statement = data["data"]["getInvestmentStatement"]["statement"]
        assert updated_statement["id"] == str(statement.id)
        assert "grossAmount" in updated_statement
        assert updated_statement["grossAmount"] == new_gross_amount

    @pytest.mark.asyncio
    async def test_get_investment_statement_by_id(
        self, client, create_investment_statement
    ):
        statements = create_investment_statement
        statement = statements[0]

        query = """
            query GetInvestmentStatement (
                $params: GetInvestmentStatementInput!
            ) {
                getInvestmentStatement(params: $params) {
                    statement {
                        id
                        period
                        previousAmount
                        contribution
                        grossAmount
                        totalTax
                        totalFee
                        referenceDate
                        atMaturity
                        netAmount
                    }
                }
            }
        """
        variables = {"params": {"id": str(statement.id)}}

        response = await client.post(
            "/graphql/finance",
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "data" in data
        assert "getInvestmentStatement" in data["data"]
        assert "statement" in data["data"]["getInvestmentStatement"]
        assert "id" in data["data"]["getInvestmentStatement"]["statement"]

        fetched_statement = data["data"]["getInvestmentStatement"]["statement"]
        # The returned ID should be the same as the request
        assert fetched_statement["id"] == str(statement.id)

    @pytest.mark.asyncio
    async def test_get_statement_metadata(self, client, create_active_investment):
        investment: InvestmentSchema = create_active_investment[0]
        # transaction_date = investment.transaction_date
        amount = investment.amount

        query = """
            query GetStatementMetadata ($investmentId: String!) {
                getStatementMetadata (
                    params: { investmentId: $investmentId }
                ) {
                    period
                    referenceDate
                    contribution
                }
            }
        """
        variables = {"investmentId": str(investment.id)}

        response = await client.post(
            "/graphql/finance",
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "getStatementMetadata" in data["data"]
        assert "period" in data["data"]["getStatementMetadata"]
        assert "contribution" in data["data"]["getStatementMetadata"]
        assert data["data"]["getStatementMetadata"]["contribution"] == amount
        # TODO: add validation to the period and reference date

    @pytest.mark.asyncio
    async def test_get_investment_type(
        self, client, create_fixed_income_br_investment_type
    ):
        response = await client.get("/investment/type")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert type(data) is dict
        assert "investmentTypes" in data
        assert type(data["investmentTypes"]) is list

        for investment_type in data["investmentTypes"]:
            assert "investmentTypeName" in investment_type
