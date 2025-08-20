import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_investment_allocation(client):
    # TODO: create test body
    response = await client.get("/investment/allocation")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_investment_performance(client, create_active_investment, create_indexer):
    indexers = create_indexer

    payload = {
        'indexerId': indexers[0].id,
    }
    response = await client.get("/investment/performance", params=payload)

    assert response.status_code == status.HTTP_200_OK
