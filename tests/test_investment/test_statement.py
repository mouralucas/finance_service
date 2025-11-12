import pytest
from starlette import status

from schemas.investment_deprecated import InvestmentStatementSchema
from services.utils.datetime import get_period


class TestStatement:

    @pytest.mark.asyncio
    async def test_update_statement(
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


@pytest.mark.asyncio
async def test_get_investment_type(client, create_fixed_income_br_investment_type):
    response = await client.get("/investment/type")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert type(data) is dict
    assert "investmentTypes" in data
    assert type(data["investmentTypes"]) is list

    for investment_type in data["investmentTypes"]:
        assert "investmentTypeName" in investment_type


@pytest.mark.asyncio
async def test_create_first_investment_statement(
    client, create_active_investment, create_tax
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
        {"currencyId": "BRL", "taxFeeId": str(create_tax[0].id), "amount": tax_total}
    ]

    net_amount = gross_amount - sum(tax["amount"] for tax in tax_details)

    payload = {
        "investmentId": investment_id,
        "period": period,
        "referenceDate": investments[0].transaction_date.strftime("%Y-%m-%d"),
        "grossAmount": gross_amount,
        "netAmount": net_amount,
        "taxDetails": tax_details,
    }

    response = await client.post("/investment/statement", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "created" in data
    assert data["created"] is True

    payload = {"investmentId": investment_id}
    response = await client.get("/investment/statement", params=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "statement" in data
    assert len(data["statement"]) == 1
    for statement in data["statement"]:
        assert "investmentId" in statement
        assert statement["investmentId"] == investment_id

        assert "contribution" in statement
        assert statement["contribution"] == investments[0].amount

        assert "taxDetail" in statement
        assert type(statement["taxDetail"]) is list
        assert "feeDetail" in statement

        assert "totalTax" in statement
        assert statement["totalTax"] == tax_total
        assert "totalFee" in statement


@pytest.mark.asyncio
async def test_get_statement(client, create_investment_statement):
    statements = create_investment_statement

    investment = statements[0].investment
    period = get_period(investment.transaction_date)

    payload = {"investmentId": investment.id, "period": period}
    response = await client.get("/investment/statement", params=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "statement" in data
