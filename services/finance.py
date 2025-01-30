from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.credit_card import CreditCardManager
from managers.finance import FinanceManager
from schemas.core import CurrencySchema, BankSchema, IndexerTypeSchema, IndexerSchema, LiquiditySchema, ExpensesByCategory, TaxFeeSchema
from schemas.request.finance import GetSummaryRequest, GetTaxFeeRequest
from schemas.response.finance import GetCurrencyResponse, GetBankResponse, GetIndexerTypeResponse, GetIndexerResponse, GetLiquidityResponse, GetExpensesByCategoryResponse, GetTaxFeeResponse


class FinanceService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)

        self.account_manager = AccountManager(self.session)
        self.finance_manager = FinanceManager(self.session)
        self.user = user.model_dump()

    async def get_summary(self, params: GetSummaryRequest):
        balance = await self.account_manager.get_balance(current_period=True)

        print(balance)

    async def get_currencies(self) -> GetCurrencyResponse:
        currencies = await self.finance_manager.get_currencies()

        response = GetCurrencyResponse(
            quantity=len(currencies) if currencies else 0,
            currencies=[CurrencySchema.model_validate(currency) for currency in currencies] if currencies else [],
        )

        return response

    async def get_tax_fee(self, params: GetTaxFeeRequest) -> GetTaxFeeResponse:
        tax_fees = await  self.finance_manager.get_tax_fee(country_id=params.country_id, tax_fee_type=params.type)

        response = GetTaxFeeResponse(
            tax_fee=[TaxFeeSchema.model_validate(tax_fee) for tax_fee in tax_fees] if tax_fees else [],
        )

        return response

    async def get_banks(self) -> GetBankResponse:
        banks = await self.finance_manager.get_banks()

        response = GetBankResponse(
            quantity=len(banks) if banks else 0,
            banks=[BankSchema.model_validate(bank) for bank in banks] if banks else []
        )

        return response

    async def get_indexer_types(self) -> GetIndexerTypeResponse:
        indexer_types = await self.finance_manager.get_indexer_types()

        response = GetIndexerTypeResponse(
            quantity=len(indexer_types) if indexer_types else 0,
            indexer_types=[IndexerTypeSchema.model_validate(indexer_type) for indexer_type in indexer_types] if indexer_types else [],
        )

        return response

    async def get_indexers(self) -> GetIndexerResponse:
        indexers = await self.finance_manager.get_indexers()

        response = GetIndexerResponse(
            quantity=len(indexers) if indexers else 0,
            indexers=[IndexerSchema.model_validate(indexer) for indexer in indexers] if indexers else [],
        )

        return response

    async def get_liquidity(self) -> GetLiquidityResponse:
        liquidity = await  self.finance_manager.get_liquidity()

        response = GetLiquidityResponse(
            quantity=len(liquidity) if liquidity else 0,
            liquidity=[LiquiditySchema.model_validate(i) for i in liquidity] if liquidity else []
        )

        return response

    # Dashboards services
    async def get_expenses_by_category(self) -> GetExpensesByCategoryResponse:
        # TODO: How to solve the problem with different currencies?
        exclude_categories = []

        account_ = await AccountManager(session=self.session).get_account_expenses_by_category(owner_id=self.user['user_id'], period=202411)
        credit_card_ = await CreditCardManager(session=self.session).get_credit_card_expense_by_category(owner_id=self.user['user_id'], period=202411)

        transactions_by_category = {}
        for item in [dict(row) for row in account_ + credit_card_]:
            category_id = item["category_id"]
            total = item["total"]
            if category_id in transactions_by_category:
                transactions_by_category[category_id]["total"] += total
            else:
                transactions_by_category[category_id] = item


        response = GetExpensesByCategoryResponse(
            expenses_by_category=[ExpensesByCategory.model_validate(transaction) for transaction in list(transactions_by_category.values())],
        )

        return response