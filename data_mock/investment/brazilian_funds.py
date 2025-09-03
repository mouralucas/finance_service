import random
import uuid
from datetime import datetime
from typing import Any

from dateutil.relativedelta import relativedelta

from data_mock.account import get_open_account_mock
from data_mock.common import default_model_dict
from data_mock.core import get_country_mock, get_currency_mock, get_tax_mock
from data_mock.investment.base import (
    get_brazilian_fund_mock,
    get_funds_br_investment_type_mock,
)
from services.utils.datetime import (
    get_period,
    get_period_dates,
    get_period_range,
    get_previous_period,
)


def get_brazilian_fund_investment_mock():
    brazilian_funds = get_brazilian_fund_mock()
    investment_types = get_funds_br_investment_type_mock()
    accounts = get_open_account_mock()
    currencies = get_currency_mock()
    countries = get_country_mock()

    investment_date = datetime.now() - relativedelta(months=10)
    quotation_date = investment_date + relativedelta(days=2)
    settlement_date = quotation_date + relativedelta(days=1)
    price = random.uniform(150.0, 300.0)
    quantity = random.uniform(2.0, 30.0)
    amount = price * quantity

    brazilian_fund_investment: list[dict[str, Any]] = [
        {
            "id": uuid.UUID("a8d5e2c1-5f7b-4e0b-9a6f-3b7b6e8c5f4d"),
            "owner_id": uuid.UUID("adf52a1e-7a19-11ed-a1eb-0242ac120002"),
            "name": "Fundo de Investimento Teste",
            "custodian_id": accounts[2]["bank_id"],
            "account_id": accounts[2]["id"],  # XP
            "price": price,
            "quantity": quantity,
            "amount": amount,
            "type_id": investment_types[0]["id"],
            "currency_id": currencies[0]["id"],
            "country_id": countries[0]["id"],
            "fund_id": brazilian_funds[0]["id"],
            "transaction_date": investment_date,
            "investment_quotation_date": quotation_date,
            "investment_settlement_date": settlement_date,
        }
    ]

    return brazilian_fund_investment


def get_brazilian_fund_investment_statement_mock():
    brazilian_funds_investment = get_brazilian_fund_investment_mock()
    tax = get_tax_mock()

    investment_period = get_period(brazilian_funds_investment[0]["transaction_date"])
    fund_id = brazilian_funds_investment[0]["fund_id"]

    fund_statement: list[dict[str, Any]] = []
    previous_amount = 0
    contribution = brazilian_funds_investment[0]["amount"]
    for idx, period in enumerate(
        get_period_range(investment_period, get_previous_period())
    ):
        gross_amount = (contribution + previous_amount) * random.uniform(0.95, 1.05)
        tax_detail = [
            {
                "id": str(tax[0]["id"]),
                "amount": gross_amount + (gross_amount * 0.15),
                "currency_id": "BRL",
            }
        ]
        net_amount = gross_amount - sum(tax["amount"] for tax in tax_detail)
        _, reference_date = get_period_dates(period)

        fund_statement.append(
            {
                **default_model_dict,
                "id": uuid.uuid4(),
                "period": period,
                "previous_amount": previous_amount,
                "gross_amount": gross_amount,
                "tax_detail": tax_detail,
                "net_amount": net_amount,
                "reference_date": reference_date,
                "fund_id": fund_id,
                "contribution": contribution,
                "price": 0,
            }
        )

        previous_amount = gross_amount
        # May add a new investment, then check the period with the investment period
        contribution = 0

    return fund_statement


if __name__ == "__main__":
    r = get_brazilian_fund_investment_statement_mock()
    for i in r:
        print(i["gross_amount"])
