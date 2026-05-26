import uuid
from typing import Any

from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.credit_card import CreditCardManager
from managers.finance import FinanceManager
from managers.investment import InvestmentManager
from models.investment_deprecated import FundsBrModel
from schemas.core import (
    BankSchema,
    ExpensesByCategory,
    IndexerSchema,
    IndexerTypeSchema,
    LiquiditySchema,
    TaxFeeSchema,
)
from schemas.finance import FundsBrSchema
from schemas.request.finance import (
    CreateBrazilianFundRequest,
    GetIndexerSeriesRequest,
    GetSummaryRequest,
    GetTaxFeeRequest,
)
from schemas.response.finance import (
    CreateBrazilianFundResponse,
    GetBankResponse,
    GetBrazilianFundsResponse,
    GetExpensesByCategoryResponse,
    GetIndexerResponse,
    GetIndexerTypeResponse,
    GetLiquidityResponse,
    GetTaxFeeResponse,
)
from services.utils.datetime import get_previous_period


class FinanceService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)

        self.account_manager = AccountManager(self.session)
        self.finance_manager = FinanceManager(self.session)
        self.investment_manager = InvestmentManager(self.session)
        self.user = user.model_dump()

    async def get_summary(self, params: GetSummaryRequest):
        balance = await self.account_manager.get_balance(current_period=True)

        print(balance)

    async def get_currencies(self) -> dict[str, Any]:
        currencies = await self.finance_manager.get_currencies()

        response = {
            "quantity": len(currencies) if currencies else 0,
            "currencies": currencies,
        }

        return response

    async def get_tax_fee(self, params: GetTaxFeeRequest) -> GetTaxFeeResponse:
        tax_fees = await self.finance_manager.get_tax_fee(
            country_id=params.country_id, tax_fee_type=params.type
        )

        response = GetTaxFeeResponse(
            tax_fee=(
                [TaxFeeSchema.model_validate(tax_fee) for tax_fee in tax_fees]
                if tax_fees
                else []
            ),
        )

        return response

    async def get_banks(self) -> GetBankResponse:
        banks = await self.finance_manager.get_banks()

        response = GetBankResponse(
            quantity=len(banks) if banks else 0,
            banks=[BankSchema.model_validate(bank) for bank in banks] if banks else [],
        )

        return response

    async def get_indexer_types(self) -> GetIndexerTypeResponse:
        indexer_types = await self.finance_manager.get_indexer_types()

        response = GetIndexerTypeResponse(
            quantity=len(indexer_types) if indexer_types else 0,
            indexer_types=(
                [
                    IndexerTypeSchema.model_validate(indexer_type)
                    for indexer_type in indexer_types
                ]
                if indexer_types
                else []
            ),
        )

        return response

    async def get_indexers(self) -> GetIndexerResponse:
        indexers = await self.finance_manager.get_indexers()

        response = GetIndexerResponse(
            quantity=len(indexers) if indexers else 0,
            indexers=(
                [IndexerSchema.model_validate(indexer) for indexer in indexers]
                if indexers
                else []
            ),
        )

        return response

    async def get_liquidity(self) -> GetLiquidityResponse:
        liquidity = await self.finance_manager.get_liquidity()

        response = GetLiquidityResponse(
            quantity=len(liquidity) if liquidity else 0,
            liquidity=(
                [LiquiditySchema.model_validate(i) for i in liquidity]
                if liquidity
                else []
            ),
        )

        return response

    async def get_periodicity(self) -> dict[str, Any]:
        periodicity = await self.finance_manager.get_periodicity()

        response = {
            "quantity": len(periodicity) if periodicity else 0,
            "periodicities": periodicity,
        }

        return response

    # Dashboards services
    async def get_expenses_by_category(self) -> GetExpensesByCategoryResponse:
        # TODO: How to solve the problem with different currencies?
        # exclude_categories = []

        account_ = await AccountManager(
            session=self.session
        ).get_account_expenses_by_category(owner_id=self.user["user_id"], period=202411)
        credit_card_ = await CreditCardManager(
            session=self.session
        ).get_credit_card_expense_by_category(
            owner_id=self.user["user_id"], period=202411
        )

        transactions_by_category = {}
        for item in [dict(row) for row in account_ + credit_card_]:
            category_id = item["category_id"]
            total = item["total"]
            if category_id in transactions_by_category:
                transactions_by_category[category_id]["total"] += total
            else:
                transactions_by_category[category_id] = item

        response = GetExpensesByCategoryResponse(
            expenses_by_category=[
                ExpensesByCategory.model_validate(transaction)
                for transaction in list(transactions_by_category.values())
            ],
        )

        return response

    async def get_finance_summary(self):

        investment = self._get_investiment_summary()
        transactions = await self._get_monthly_incoming_and_outgoing()

        return {
            "investment": investment,
        }

    async def _get_investiment_summary(self) -> dict[str, Any]:
        total_gross = await self.investment_manager.get_total_active_gross(
            owner_id=self.user["user_id"],
        )
        total_last_month = await self.investment_manager.get_performance_portfolio(
            owner_id=self.user["user_id"],
            investment_id=None,
            indexer_id=uuid.UUID("2a2b100f-17d9-4c61-b3b4-f06662113953"),
            period_range=0,
        )
        total_last_month = total_last_month[-1] if total_last_month else []
        total_invested = await self.investment_manager.get_total_invested(
            owner_id=self.user["user_id"], is_settled=False
        )
        investments = await self.investment_manager.get_investments(
            owner_id=self.user["user_id"], is_settled=False
        )

        investment = {
            "total_invested": total_invested if total_invested else 0,
            "total_gross": total_gross if total_gross else 0,
            "total_growth": total_gross - total_invested if total_invested else 0,
            "active_investments_count": len(investments) if investments else 0,
            "total_growth_percentage": (
                ((total_gross - total_invested) / total_invested) * 100
                if total_invested
                else 0
            ),
            "last_month_growth_percentage": 0,
        }

        return investment

    async def _get_monthly_incoming_and_outgoing(self):
        transactions = await self.account_manager.get_transactions(
            owner_id=self.user["user_id"],
            start_period=get_previous_period(),
            end_period=get_previous_period(),
        )
        if not transactions:
            return {"total_incoming": 0, "total_outgoing": 0}
        
        total_incoming = sum(
            transaction["amount"] for transaction in transactions if transaction["amount"] > 0
        )
        total_outgoing = sum(
            transaction["amount"] for transaction in transactions if transaction["amount"] < 0
        )
        
        return {"total_incoming": total_incoming, "total_outgoing": total_outgoing}

    # Funds service -> Will be deprecated
    async def create_br_fund(
        self, fund: CreateBrazilianFundRequest
    ) -> CreateBrazilianFundResponse:
        fund_model = FundsBrModel(**fund.model_dump())
        fund_model.owner_id = self.user["user_id"]
        fund_model.fees = (
            [fee.model_dump(mode="json") for fee in fund.fees] if fund.fees else None
        )

        new_fund = await self.finance_manager.create_fund(fund_model)

        response = CreateBrazilianFundResponse(
            fund=FundsBrSchema.model_validate(new_fund),
        )

        return response

    async def get_brazilian_funds(self) -> GetBrazilianFundsResponse:
        funds = await self.finance_manager.get_brazilian_funds()

        response = GetBrazilianFundsResponse(
            quantity=len(funds) if funds else 0,
            funds=(
                [FundsBrSchema.model_validate(fund) for fund in funds] if funds else []
            ),
        )

        return response

    # Indexer series data
    async def get_indexer_series(
        self, params: GetIndexerSeriesRequest
    ) -> dict[str, Any]:
        indexer = await self.finance_manager.get_indexer_by_id(
            indexer_id=params.indexer_id
        )
        periodicity = await self.finance_manager.get_periodicity_by_id(
            periodicity_id=params.periodicity_id
        )
        series = await self.finance_manager.get_indexer_series(
            indexer_id=params.indexer_id,
            periodicity_id=params.periodicity_id,
            start_period=params.start_period,
            end_period=params.end_period,
        )

        response = {
            "quantity": len(series) if series else 0,
            "indexer": indexer.name,
            "periodicity": periodicity.name,
            "series": series,
        }

        return response

    # Currency exchange services
    async def get_currency_avarage_price(self):
        pass
