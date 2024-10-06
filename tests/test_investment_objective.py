import datetime

import pytest
from dateutil.relativedelta import relativedelta
from starlette import status


@pytest.mark.asyncio
async def test_create_objective(client):
    payload = {
        'title': 'Meu objetivo',
        'description': 'Comprar um apartamento na praia',
        'amount': 50000,
        'estimatedDeadline': (datetime.datetime.utcnow() + relativedelta(years=1, months=6)).strftime('%Y-%m-%d'),
    }
    response = await client.post('/investment/objective', json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert 'objective' in data
    assert 'objectiveId' in data['objective']

    assert 'title' in data['objective']
    assert data['objective']['title'] == payload['title']
    assert 'description' in data['objective']
    assert data['objective']['description'] == payload['description']
    assert 'amount' in data['objective']
    assert data['objective']['amount'] == payload['amount']
    assert 'estimatedDeadline' in data['objective']
    assert data['objective']['estimatedDeadline'] == payload['estimatedDeadline']


@pytest.mark.asyncio
async def test_get_open_objectives(client, create_open_investment_objectives):
    response = await client.get('/investment/objective')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert 'objectives' in data


@pytest.mark.asyncio
async def test_check_investments_for_objectives(client, create_investment):
    """
    Created by: Lucas Penha de Moura - 21/09/2024
        This test checks the function that looks for an investment without an objective
    """
    response = await client.get('/investment/objective/not-set')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert 'investments' in data
    assert type(data['investments']) is list

@pytest.mark.asyncio
async def test_get_objective_summary(client):
    pass