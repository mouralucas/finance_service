import pytest
from starlette import status


class TestBank:
    @pytest.mark.asyncio
    async def test_get_banks(self, client, create_bank_beta):
        total_banks = len(create_bank_beta)

        response = await client.get("/finance/bank")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "quantity" in data
        assert data["quantity"] == total_banks
        assert "banks" in data
        assert type(data["banks"]) is list
        assert len(data["banks"]) == data["quantity"]
