from datetime import date, datetime, timezone

import pytest
from dateutil.relativedelta import relativedelta
from rolf_common.util.datetime import get_timestamp_aware
from starlette import status

from services.utils.datetime import get_randon_date


@pytest.mark.asyncio
async def test_create_funds_br_investment(client, create_funds_br_investment_type, create_open_account, create_currency, create_country):
    # This endpoint was not created yet
    accounts = create_open_account
    currencies = create_currency
    countries = create_country

    investment_name = 'Investimento no fundo multimercado'
    account = accounts[0]
    price = 172.32
    quantity = 527
    amount = price * quantity
    investment_type = create_funds_br_investment_type[0]
    currency = currencies[0]
    country = countries[0]
    objective = None
    investment_quotation_date = get_randon_date(start_date=get_timestamp_aware() - relativedelta(months=3), end_date=get_timestamp_aware())
    investment_settlement_date = investment_quotation_date + relativedelta(days=2)
    redemption_quotation_range = 'D+2 (dias úteis)'
    redemption_quotation_date = get_randon_date(start_date=get_timestamp_aware(), end_date=get_timestamp_aware() + relativedelta(months=5))
    redemption_settlement_range = 'D+4 (dias úteis)'
    redemption_settlement_date = redemption_quotation_date + relativedelta(days=4)
    minimum_balance = 100
    minimum_transaction = 150
    initial_investment = 500

    payload = {
        'name': investment_name,
        'accountId': str(account.id),
        'price': price,
        'quantity': quantity,
        'amount': amount,
        'investmentTypeId': str(investment_type.id),
        'currencyId': str(currency.id),
        'countryId': str(country.id),
        'objectiveId': objective,
        'investmentQuotationDate': str(investment_quotation_date.strftime('%Y-%m-%d')),
        'investmentSettlementDate': str(investment_settlement_date.strftime('%Y-%m-%d')),
        'redemptionQuotationRange': redemption_quotation_range,
        'redemptionQuotationDate': str(redemption_quotation_date.strftime('%Y-%m-%d')),
        'redemptionSettlementRange': redemption_settlement_range,
        'redemptionSettlementDate': str(redemption_settlement_date.strftime('%Y-%m-%d')),
        'minimumBalance': minimum_balance,
        'minimumTransaction': minimum_transaction,
        'initialInvestment': initial_investment,
    }
    # response = await client.post('/investment/funds/br', json=payload)
    assert True
