import datetime

import pytest
from starlette import status

from services.utils.datetime import get_period


@pytest.mark.asyncio
async def test_get_investment_type(client, create_investment_type):
    response = await client.get('/investment/type')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert type(data) is dict
    assert 'investmentType' in data
    assert type(data['investmentType']) is list

    for investmentType in data['investmentType']:
        assert 'name' in investmentType


@pytest.mark.asyncio
async def test_create_first_investment_statement(client, create_investment, create_tax):
    """
        The first statement should have the same period as the investment
    :param client:
    :param create_investment:
    :param create_tax:
    :return:
    """
    investments = create_investment

    investment_id = str(investments[0].id)
    period = get_period(investments[0].transaction_date)
    gross_amount = 35.10
    tax_detail = [{
        'taxFeeId': str(create_tax[0].id),
        'amount': 0.21
    }]

    net_amount = gross_amount - sum(tax['amount'] for tax in tax_detail)

    payload = {
        'investmentId': investment_id,
        'period': period,
        'referenceDate': investments[0].transaction_date.strftime('%Y-%m-%d'),
        'grossAmount': gross_amount,
        'netAmount': net_amount,
        'taxDetail': tax_detail,
    }

    response = await client.post('/investment/statement', json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'investmentStatement' in data
    assert 'investmentId' in data['investmentStatement']
    assert data['investmentStatement']['investmentId'] == str(investment_id)
    assert 'period' in data['investmentStatement']
    assert data['investmentStatement']['period'] == period
    assert 'grossAmount' in data['investmentStatement']
    assert data['investmentStatement']['grossAmount'] == gross_amount
    assert 'totalTax' in data['investmentStatement']
    assert data['investmentStatement']['totalTax'] == sum(tax['amount'] for tax in tax_detail)
    assert 'totalFee' in data['investmentStatement']
    assert data['investmentStatement']['totalFee'] == 0
    assert 'netAmount' in data['investmentStatement']
    assert data['investmentStatement']['netAmount'] == net_amount
    # TODO: add test to tax and fee details


@pytest.mark.asyncio
async def test_get_statement(client, create_investment_statement):
    statements = create_investment_statement

    investment = statements[0].investment
    period = get_period(investment.transaction_date)

    payload = {
        'period': period
    }
    response = await client.get('/investment/statement', params=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()