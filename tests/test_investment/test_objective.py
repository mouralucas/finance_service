import datetime

import pytest
from dateutil.relativedelta import relativedelta
from starlette import status


@pytest.mark.asyncio
async def test_create_objective(client, create_currency):
    currencies = create_currency

    payload = {
        "title": "Meu objetivo",
        "description": "Comprar um apartamento na praia",
        "amount": 50000,
        "currencyId": currencies[0].id,
        "estimatedDeadline": (
            datetime.datetime.now(datetime.UTC) + relativedelta(years=1, months=6)
        ).strftime("%Y-%m-%d"),
    }
    response = await client.post("/investment/objective", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert "objective_created" in data


@pytest.mark.asyncio
async def test_get_open_objectives(client, create_open_investment_objectives):
    # TODO: add tests
    response = await client.get("/investment/objective")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "objectives" in data


@pytest.mark.asyncio
async def test_check_investments_for_objectives(client, create_active_investment):
    """
    Created by: Lucas Penha de Moura - 21/09/2024
        This test checks the function that looks for an investment without an objective
    """
    response = await client.get("/investment/objective/not-set")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "investments" in data
    assert type(data["investments"]) is list


@pytest.mark.asyncio
async def test_get_objective_summary(client):
    pass
