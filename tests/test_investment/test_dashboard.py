import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_investment_allocation(client):
    # TODO: create test body
    response = await client.get("/investment/allocation")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_investment_performance(
    client, create_active_investment, create_indexer, create_periodicity
):
    assert True
