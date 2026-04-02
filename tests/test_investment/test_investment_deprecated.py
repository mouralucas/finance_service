import pytest
from starlette import status


@pytest.mark.asyncio
async def test_settle_investment(client, create_active_investment):
    investments = create_active_investment

    investment_id = investments[0].id
    settlement_date = "2025-08-09"
    gross_amount = 300.54
    net_amount = 250.32
    settlement_amount = 250.32
    tax_detail = [
        {
            "currencyId": "BRL",
            "taxFeeId": "a6c45a5a-f75f-475c-afa1-1cf02cd3fd04",
            "amount": settlement_amount * 0.15,
        }
    ]
    fee_detail = [
        {
            "currencyId": "BRL",
            "taxFeeId": "a187d754-73c9-46d3-ac57-7cc78ea01e6f",
            "amount": settlement_amount * 0.01,
        }
    ]

    payload = {
        "investmentId": str(investment_id),
        "settlementDate": settlement_date,
        "settlementAmount": settlement_amount,
        "grossAmount": gross_amount,
        "netAmount": net_amount,
        "taxDetail": tax_detail,
        "feeDetail": fee_detail,
    }
    response = await client.post("/investment/settle", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "investment" in data
    assert "isSettled" in data["investment"]
    assert data["investment"]["isSettled"] is True
    assert "settlementDate" in data["investment"]
    assert data["investment"]["settlementDate"] == settlement_date
    assert "settlementAmount" in data["investment"]
    assert float(data["investment"]["settlementAmount"]) == settlement_amount


@pytest.mark.asyncio
async def test_get_active_investments(
    client, create_active_investment, create_settled_investment
):
    active_investments = create_active_investment
    len_active_investments = len(active_investments)
    len_settled_investments = len(create_settled_investment)
    len_all_investments = len_active_investments + len_settled_investments

    query = """
        query GetInvestments($params: GetInvestmentsInput) {
            getInvestments(params: $params) {
                quantity
                investments {
                    id
                    isSettled
                    settlementDate
                    settlementAmount
                }
            }
        }
    """
    payload = {"params": {"isSettled": False}}
    response = await client.post(
        "/graphql/finance", json={"query": query, "variables": payload}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "data" in data
    assert "getInvestments" in data["data"]
    data = data["data"]["getInvestments"]
    assert "investments" in data

    assert len(data["investments"]) <= len_all_investments
    assert len(data["investments"]) == len_active_investments

    for invstment in data["investments"]:
        assert "isSettled" in invstment
        assert invstment["isSettled"] is False
        assert "settlementDate" in invstment
        assert invstment["settlementDate"] is None
        assert "settlementAmount" in invstment
        assert invstment["settlementAmount"] is None


@pytest.mark.asyncio
async def test_get_settled_investments(
    client, create_active_investment, create_settled_investment
):
    active_investments = create_active_investment
    len_active_investments = len(active_investments)
    len_settled_investments = len(create_settled_investment)
    len_all_investments = len_active_investments + len_settled_investments

    query = """
        query GetInvestments($params: GetInvestmentsInput) {
            getInvestments(params: $params) {
                quantity
                investments {
                    id
                    isSettled
                    settlementDate
                    settlementAmount
                }
            }
        }
    """
    payload = {"params": {"isSettled": True}}
    response = await client.post(
        "/graphql/finance", json={"query": query, "variables": payload}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "data" in data
    assert "getInvestments" in data["data"]
    data = data["data"]["getInvestments"]
    assert "investments" in data

    assert len(data["investments"]) <= len_all_investments
    assert len(data["investments"]) == len_settled_investments

    for invstment in data["investments"]:
        assert "isSettled" in invstment
        assert invstment["isSettled"] is True
        assert "settlementDate" in invstment
        assert invstment["settlementDate"] is not None
        assert "settlementAmount" in invstment
        assert invstment["settlementAmount"] is not None
