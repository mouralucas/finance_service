import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_investment_allocation(client):
    # TODO: create test body
    response = await client.get("/investment/allocation")

    assert response.status_code == status.HTTP_200_OK