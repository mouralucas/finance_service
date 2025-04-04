import pytest
from dateutil.relativedelta import relativedelta
from starlette import status

from tests.utils import random_date


@pytest.mark.asyncio
async def test_create_brazilian_fund_investment(client, create_brazilian_funds, create_country, create_currency,
                                                create_open_account, create_funds_br_investment_type):
    br_funds = create_brazilian_funds
    accounts = create_open_account
    investment_types = create_funds_br_investment_type

    name = 'Lucas Fundo de Investimento FIM'
    account_id = accounts[0].id
    account_name = accounts[0].nickname
    price = 3.25789
    amount = 1250.00
    quantity = price * amount
    investment_type_id = investment_types[0].id
    investment_type_name = investment_types[0].name
    currency_id = 'BRL'
    country_id = 'BR'
    fund_id = br_funds[0].id
    fund_name = br_funds[0].name
    transaction_date = random_date()
    investment_quotation_date = transaction_date + relativedelta(days=1)
    investment_settlement_date = investment_quotation_date + relativedelta(days=1)

    payload = {
        'name': name,
        'accountId': str(account_id),
        'price': price,
        'quantity': quantity,
        'amount': amount,
        'investmentTypeId': str(investment_type_id),
        'currencyId': currency_id,
        'countryId': country_id,
        'fundId': str(fund_id),
        'transactionDate': transaction_date.strftime("%Y-%m-%d"),
        'investmentQuotationDate': investment_quotation_date.strftime("%Y-%m-%d"),
        'investmentSettlementDate': investment_settlement_date.strftime("%Y-%m-%d"),
    }
    response = await client.post('/investment/funds/br', json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'fund' in data

    assert 'investmentId' in data['fund']
    assert 'accountId' in data['fund']
    assert data['fund']['accountId'] == str(account_id)
    assert 'price' in data['fund']
    assert data['fund']['price'] == price
    assert 'quantity' in data['fund']
    assert data['fund']['quantity'] == quantity
    assert 'amount' in data['fund']
    assert data['fund']['amount'] == amount
    assert 'investmentTypeId' in data['fund']
    assert data['fund']['investmentTypeId'] == str(investment_type_id)
    assert 'currencyId' in data['fund']
    assert data['fund']['currencyId'] == currency_id
    assert 'countryId' in data['fund']
    assert data['fund']['countryId'] == country_id
    assert 'fundId' in data['fund']
    assert data['fund']['fundId'] == str(fund_id)
    assert 'fundName' in data['fund']
    assert data['fund']['fundName'] == fund_name
    assert 'transactionDate' in data['fund']
    assert data['fund']['transactionDate'] == transaction_date.strftime("%Y-%m-%d")
    assert 'investmentQuotationDate' in data['fund']
    assert data['fund']['investmentQuotationDate'] == investment_quotation_date.strftime("%Y-%m-%d")
    assert 'investmentSettlementDate' in data['fund']
    assert data['fund']['investmentSettlementDate'] == investment_settlement_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_create_brazilian_fund_investment_statement(client, create_tax, create_currency, create_country, create_bank, create_open_account, create_funds_br_investment_type,
                                                          create_brazilian_fund_investment):
    """
            This test verifies if the contribution in period is being calculated correctly.
            The service checks if there are any contributions in the period, if there are, it adds the contribution to the statement.
        """
    fund_investments = create_brazilian_fund_investment
    taxes = create_tax

    fund_id = fund_investments[0].fund_id
    total_invested = sum(investment.amount for investment in fund_investments if investment.fund_id == fund_id)
    period = 202503
    reference_date = '2025-03-31'
    gross_amount = total_invested * 1.01
    tax_details = [{
        'taxFeeId': str(taxes[0].id),
        'amount': total_invested * 1.01,
        'currencyId': 'BRL',
    }]
    total_tax = sum(tax['amount'] for tax in tax_details)
    net_amount = gross_amount - tax_details[0]['amount']
    price = fund_investments[0].price * 1.1

    payload = {
        'period': period,
        'referenceDate': reference_date,
        'grossAmount': gross_amount,
        'netAmount': net_amount,
        'taxDetail': tax_details,
        'price': price,
        'fundId': str(fund_id),
    }
    response = await client.post('/investment/funds/br/statement', json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert 'statement' in data
    assert 'investmentStatementId' in data['statement']
    assert 'referenceDate' in data['statement']
    assert data['statement']['referenceDate'] == reference_date
    assert 'period' in data['statement']
    assert data['statement']['period'] == period
    assert 'grossAmount' in data['statement']
    assert data['statement']['grossAmount'] == gross_amount
    assert 'totalTax' in data['statement']
    assert data['statement']['totalTax'] == round(total_tax, 5)
    assert 'netAmount' in data['statement']
    assert data['statement']['netAmount'] == net_amount
    assert 'fundId' in data['statement']
    assert data['statement']['fundId'] == str(fund_id)
    assert 'contribution' in data['statement']
    # For first statement the contribution is the total invested
    assert data['statement']['contribution'] == total_invested
    assert 'price' in data['statement']
    assert data['statement']['price'] == round(price, 5)
    assert 'penalty' in data['statement']
    # If not provided, the penalty is 0
    assert data['statement']['penalty'] == 0


@pytest.mark.asyncio
async def test_create_brazilian_fund_investment_statement_with_contribution_in_period(client, create_tax, create_currency,
                                                                                      create_brazilian_fund_investment):
    pass
