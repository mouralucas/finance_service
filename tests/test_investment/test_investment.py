import pytest
from starlette import status

from services.utils.datetime import get_period


class TestInvestmentStatement:

    @pytest.mark.asyncio
    async def test_investment_statement_creation(
        self, client, create_active_investment
    ):
        investments = create_active_investment

        payload = {
            "investmentId": str(investments[0].id),
            "period": get_period(investments[0].transaction_date),
            # TODO: change to last day of month.
            #  In future, the value will be automatically calculated based on the period
            "referenceDate": investments[0].transaction_date.strftime("%Y-%m-%d"),
            "grossAmount": investments[0].amount * 1.05,
            "netAmount": (investments[0].amount * 1.05) - 3.60,
            "taxDetails": [
                {
                    "taxFeeId": "9969f9fd-e397-489f-950e-6fc68d8f0d6b",
                    "amount": 3.52,
                    "currencyId": "BRL",
                }
            ],
            "feeDetails": [
                {
                    "taxFeeId": "18a4ba92-1fef-4037-b0cf-14a7c3132453",
                    "amount": 0.08,
                    "currencyId": "BRL",
                }
            ],
        }
        response = await client.post("/investment/statement", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert "investmentStatement" in data
        assert "investmentId" in data["investmentStatement"]
        assert data["investmentStatement"]["investmentId"] == str(investments[0].id)
