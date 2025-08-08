import uuid
from typing import cast

from rolf_common.models import SQLModel
from sqlalchemy import RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession

from managers.investment import InvestmentManager
from models.investment_brazilian_fund import InvestmentBrazilianFundsModel, InvestmentBrazilianFundsStatementModel


class InvestmentBrazilianFundManager(InvestmentManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_brazilian_fund(self, investment: InvestmentBrazilianFundsModel) -> SQLModel:
        new_investment_fund = await self.add_one(investment)

        return new_investment_fund

    async def get_brazilian_fund_investment(self, investment_id: uuid.UUID | None, is_settled: bool) -> list[InvestmentBrazilianFundsModel]:
        query = select(InvestmentBrazilianFundsModel).where(
            InvestmentBrazilianFundsModel.is_settled == is_settled
        )

        if investment_id:
            query = query.where(InvestmentBrazilianFundsModel.id == investment_id)

        if is_settled:
            query = query.where(InvestmentBrazilianFundsModel.is_settled)

        result = await self.get_all(query)

        return [investment['InvestmentBrazilianFundsModel'] for investment in result]

    async def get_brazilian_fund_investment_consolidated(self, fund_id: uuid.UUID):
        pass

    async def get_investments_by_fund_id(self, fund_id: uuid.UUID) -> list[InvestmentBrazilianFundsModel]:
        query = (
            select(
                InvestmentBrazilianFundsModel
            )
            .where(
                InvestmentBrazilianFundsModel.fund_id == fund_id
            )
            .order_by(InvestmentBrazilianFundsModel.transaction_date)
        )
        investments = await self.get_all(query)

        return [investment['InvestmentBrazilianFundsModel'] for investment in investments] if investments else None

    async def create_investment_statement(self, statement: InvestmentBrazilianFundsStatementModel) -> InvestmentBrazilianFundsStatementModel:
        new_statement = await self.add_one(statement)

        return cast(InvestmentBrazilianFundsStatementModel, new_statement)

    async def get_statement(self, fund_id: uuid.UUID, period: int = None,
                            start_period: int = None, end_period: int = None):
        query = (
            select(InvestmentBrazilianFundsStatementModel)
            .where(InvestmentBrazilianFundsStatementModel.fund_id == fund_id)
            .order_by(InvestmentBrazilianFundsStatementModel.period.desc())
        )

        result: list[RowMapping] = await self.get_all(query, unique_result=True)

        return [statement['InvestmentBrazilianFundsStatementModel'] for statement in result] if result else None
