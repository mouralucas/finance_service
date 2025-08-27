import asyncio

from rolf_common.managers import BaseDataManager

from backend.database import sessionmanager
from data_mock.account import get_account_transaction_mock, get_account_type_mock, get_closed_account_mock, get_open_account_mock
from data_mock.core import (
    get_bank_mock,
    get_category_mock,
    get_category_parent_mock,
    get_country_mock,
    get_currency_mock,
    get_expense_type_mock,
    get_fee_mock,
    get_index_type_mock,
    get_indexer_mock,
    get_liquidity_mock,
    get_tax_mock,
)
from data_mock.credit_card import get_cancelled_credit_card_mock, get_credit_card_mock
from data_mock.investment.base import get_brazilian_fund_mock
from data_mock.investment.investment import (
    get_active_investment_mock,
    get_fixed_income_br_investment_type_mock,
    get_investment_category_mock,
    get_investment_statement_mock,
)
from models.account import AccountModel, AccountTransactionModel, AccountTypeModel
from models.core import (
    BankModel,
    CategoryModel,
    CountryModel,
    CurrencyModel,
    ExpenseTypeModel,
    IndexerModel,
    IndexerTypeModel,
    LiquidityModel,
    TaxFeeModel,
)
from models.credit_card import CreditCardModel
from models.investment import FundsBrModel, InvestmentCategoryModel, InvestmentModel, InvestmentStatementModel, InvestmentTypeModel


async def populate():
    async with sessionmanager.session() as session:
        # Core data
        await BaseDataManager(session).add_or_ignore_all(BankModel, get_bank_mock())
        await BaseDataManager(session).add_or_ignore_all(CurrencyModel, get_currency_mock())
        await BaseDataManager(session).add_or_ignore_all(IndexerTypeModel, get_index_type_mock())
        await BaseDataManager(session).add_or_ignore_all(IndexerModel, get_indexer_mock())
        await BaseDataManager(session).add_or_ignore_all(CategoryModel, get_category_parent_mock())
        await BaseDataManager(session).add_or_ignore_all(CategoryModel, get_category_mock())
        await BaseDataManager(session).add_or_ignore_all(LiquidityModel, get_liquidity_mock())
        await BaseDataManager(session).add_or_ignore_all(CountryModel, get_country_mock())
        await BaseDataManager(session).add_or_ignore_all(ExpenseTypeModel, get_expense_type_mock())
        await BaseDataManager(session).add_or_ignore_all(TaxFeeModel, get_tax_mock())
        await BaseDataManager(session).add_or_ignore_all(TaxFeeModel, get_fee_mock())

        # Account data
        await BaseDataManager(session).add_or_ignore_all(AccountTypeModel, get_account_type_mock())
        await BaseDataManager(session).add_or_ignore_all(AccountModel, get_open_account_mock())
        await BaseDataManager(session).add_or_ignore_all(AccountModel, get_closed_account_mock())
        await BaseDataManager(session).add_or_ignore_all(AccountTransactionModel, get_account_transaction_mock())

        # Credit Card data
        await BaseDataManager(session).add_or_ignore_all(CreditCardModel, get_credit_card_mock())
        await BaseDataManager(session).add_or_ignore_all(CreditCardModel, get_cancelled_credit_card_mock())

        # Investment data
        await BaseDataManager(session).add_or_ignore_all(InvestmentCategoryModel, get_investment_category_mock())
        await BaseDataManager(session).add_or_ignore_all(InvestmentTypeModel, get_fixed_income_br_investment_type_mock())
        await BaseDataManager(session).add_or_ignore_all(InvestmentModel, get_active_investment_mock())
        await BaseDataManager(session).add_or_ignore_all(InvestmentStatementModel, get_investment_statement_mock())
        await BaseDataManager(session).add_or_ignore_all(FundsBrModel, get_brazilian_fund_mock())


if __name__ == '__main__':
    loop = asyncio.run(populate())
