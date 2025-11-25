import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import Executable, RowMapping, case, func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette import status

from models.core import BankModel, CurrencyModel, IndexerSeriesModel
from models.investment import InvestmentModel, InvestmentStatementModel
from models.investment_deprecated import (
    InvestmentCategoryModel,
    InvestmentObjectiveModel,
    InvestmentTypeModel,
)
from services.utils.datetime import get_previous_period


class InvestmentManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_investment(self, investment: Any) -> SQLModel:
        await self.add_one(investment)

        return investment

    async def update_investment(
        self, investment_id: uuid.UUID, fields: dict[str, Any]
    ) -> InvestmentModel:
        query = (
            update(InvestmentModel)
            .where(InvestmentModel.id == investment_id)
            .values(**fields)
        )

        await self.session.execute(query)
        await self.session.flush()

        updated_investment = await self.get_investment_by_id(
            investment_id=investment_id
        )

        return cast(InvestmentModel, updated_investment)

    async def get_investment_by_id(
        self, investment_id: uuid.UUID, raise_exception: bool = False
    ) -> InvestmentModel:
        investment = await self.get_by_id(InvestmentModel, investment_id)

        if not investment and raise_exception:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Investment not found"
            )

        investment = cast(InvestmentModel, investment)

        return investment

    async def get_investments(
        self, owner_id: uuid.UUID, is_settled: bool | None
    ) -> list[dict[Any, Any]] | None:
        investment_alias = aliased(InvestmentModel)
        currency_alias = aliased(CurrencyModel)
        type_alias = aliased(InvestmentTypeModel)
        bank_alias = aliased(BankModel)
        statement_alias = aliased(InvestmentStatementModel)

        subquery = (
            select(
                statement_alias.investment_id.label("investment_id"),
                func.max(statement_alias.period).label("latest_period"),
            )
            .group_by(statement_alias.investment_id)
            .subquery()
        )

        query = (
            select(
                investment_alias.id,
                investment_alias.custodian_id,
                investment_alias.account_id,
                bank_alias.name.label("custodian_name"),
                investment_alias.name,
                investment_alias.transaction_date,
                investment_alias.maturity_date,
                investment_alias.price,
                investment_alias.quantity,
                investment_alias.amount,
                investment_alias.contracted_rate,
                investment_alias.currency_id,
                currency_alias.symbol.label("currency_symbol"),
                investment_alias.type_id,
                type_alias.name.label("investment_type_name"),
                investment_alias.liquidity_id,
                investment_alias.indexer_id,
                investment_alias.indexer_type_id,
                investment_alias.country_id,
                investment_alias.is_settled,
                investment_alias.settlement_date,
                investment_alias.settlement_amount,
                case(
                    (
                        statement_alias.gross_amount.is_(None),
                        investment_alias.amount,
                    ),
                    else_=statement_alias.gross_amount,
                ).label("gross_amount"),
                case(
                    (
                        statement_alias.gross_amount.is_not(None),
                        (
                            (statement_alias.gross_amount - investment_alias.amount)
                            / investment_alias.amount
                        )
                        * 100,
                    ),
                    else_=0,
                ).label("percentage_change"),
                statement_alias.period,
                investment_alias.objective_id,
            )
            .join(currency_alias, investment_alias.currency_id == currency_alias.id)
            .join(type_alias, investment_alias.type_id == type_alias.id)
            .join(bank_alias, investment_alias.custodian_id == bank_alias.id)
            .outerjoin(subquery, investment_alias.id == subquery.c.investment_id)
            .outerjoin(
                statement_alias,
                (statement_alias.investment_id == investment_alias.id)
                & (statement_alias.period == subquery.c.latest_period),
            )
            .where(
                investment_alias.owner_id == owner_id,
            )
            .order_by(investment_alias.transaction_date)
        )

        if is_settled is not None and is_settled:
            query = query.where(investment_alias.is_settled)

        if is_settled is not None and not is_settled:
            query = query.where(~investment_alias.is_settled)

        investments: list[RowMapping] | None = await self.get_all(query)

        return (
            [dict(investment.items()) for investment in investments]
            if investments
            else None
        )

    # Investment statement
    async def create_statement(self, statement: InvestmentStatementModel) -> SQLModel:
        await self.add_one(statement)

        return statement

    async def update_statement(
        self, statement_id: uuid.UUID, fields: dict[str, Any]
    ) -> InvestmentStatementModel:
        query = (
            update(InvestmentStatementModel)
            .where(InvestmentStatementModel.id == statement_id)
            .values(**fields)
        )

        await self.session.execute(query)
        await self.session.flush()

        updated_statement = await self.get_by_id(
            sql_model=InvestmentStatementModel, object_id=statement_id
        )

        return cast(InvestmentStatementModel, updated_statement)

    async def get_statements(self, investment_id: uuid.UUID):
        m = InvestmentStatementModel

        previous_gross = func.lag(m.gross_amount).over(
            partition_by=m.investment_id, order_by=m.period
        )

        adjusted_previous = func.coalesce(previous_gross, 0) + func.coalesce(
            m.contribution, 0
        )

        variation_value = m.gross_amount - adjusted_previous

        variation_percent = case(
            (adjusted_previous != 0, (variation_value / adjusted_previous * 100)),
            else_=None,
        )

        stmt = (
            select(
                m.id,
                m.investment_id,
                m.period,
                func.coalesce(previous_gross, 0).label("previous_amount"),
                m.gross_amount,
                m.contribution,
                m.total_tax,
                m.tax_detail,
                m.total_fee,
                m.fee_detail,
                m.reference_date,
                m.at_maturity,
                variation_value.label("value_change"),
                variation_percent.label("percentage_change"),
                m.net_amount,
            )
            .where(m.investment_id == investment_id)
            .order_by(m.period.desc())
        )

        result: list[RowMapping] | None = await self.get_all(stmt)
        statements = [dict(statement) for statement in result] if result else None
        return statements

    async def get_statement_by_id(
        self, statement_id: uuid.UUID
    ) -> InvestmentStatementModel | None:
        statement = await self.get_by_id(InvestmentStatementModel, statement_id)

        return cast(InvestmentStatementModel, statement)

    async def get_latest_investment_statements(self, investment_ids: list[uuid.UUID]):
        subquery = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .where(InvestmentStatementModel.investment_id.in_(investment_ids))
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        query = select(
            InvestmentStatementModel.investment_id,
            InvestmentStatementModel.period,
            InvestmentStatementModel.gross_amount,
        ).join(
            subquery,
            (InvestmentStatementModel.investment_id == subquery.c.investment_id)
            & (InvestmentStatementModel.period == subquery.c.latest_period),
        )

        result = await self.get_all(query)

        return result

    # Investment Types
    async def create_investment_type(
        self, investment_type: InvestmentTypeModel
    ) -> SQLModel:
        await self.add_one(investment_type)

        return investment_type

    async def get_investment_type(self) -> list[RowMapping]:
        query: Executable = select(InvestmentTypeModel).order_by(
            InvestmentTypeModel.name
        )

        investment_types: list[RowMapping] = await self.get_all(query)

        return investment_types

    # Investment objectives
    async def create_objective(
        self, objective: InvestmentObjectiveModel
    ) -> SQLModel | None:
        new_objective = await self.add_one(objective)

        return new_objective

    async def get_objectives(
        self, owner_id: str, objective_id: uuid.UUID | None = None
    ) -> list[dict[Any, Any]] | None:
        stmt_alias = aliased(InvestmentStatementModel)

        latest_stmt_subq = (
            select(
                stmt_alias.investment_id,
                stmt_alias.gross_amount,
            )
            .distinct(stmt_alias.investment_id)
            .order_by(stmt_alias.investment_id, stmt_alias.reference_date.desc())
            .subquery()
        )

        query = (
            select(
                InvestmentObjectiveModel.id,
                InvestmentObjectiveModel.owner_id,
                InvestmentObjectiveModel.title,
                InvestmentObjectiveModel.currency_id,
                InvestmentObjectiveModel.amount,
                InvestmentObjectiveModel.estimated_deadline,
                func.coalesce(func.sum(latest_stmt_subq.c.gross_amount), 0).label(
                    "current_amount"
                ),
            )
            .outerjoin(
                InvestmentModel,
                (InvestmentModel.objective_id == InvestmentObjectiveModel.id)
                & (InvestmentModel.is_settled.is_(False)),
            )
            .outerjoin(
                latest_stmt_subq,
                latest_stmt_subq.c.investment_id == InvestmentModel.id,
            )
            .where(InvestmentObjectiveModel.owner_id == owner_id)
            .group_by(InvestmentObjectiveModel.id)
            .order_by(InvestmentObjectiveModel.estimated_deadline)
        )

        if objective_id:
            query = query.where(InvestmentObjectiveModel.id == objective_id)

        investment_objectives: list[RowMapping] | None = await self.get_all(
            query, unique_result=True
        )

        return (
            [dict(obj.items()) for obj in investment_objectives]
            if investment_objectives
            else None
        )

    async def get_objective_by_id(
        self, objective_id: uuid.UUID
    ) -> InvestmentObjectiveModel | None:
        objective = await self.get_by_id(InvestmentObjectiveModel, objective_id)

        return cast(InvestmentObjectiveModel, objective)

    async def get_objective_investments(
        self, objective_id: uuid.UUID | None = None, with_objective: bool | None = None
    ) -> list[InvestmentModel]:
        """
        Created by: Lucas Penha de Moura

            Get investments based on objectives.
        :param objective_id: The objective identification
        :param with_objective: If true return all investments with an objective,
            if false return all investments without an objective set.
        :return:
        """
        query = select(InvestmentModel)

        if objective_id:
            query = query.where(InvestmentModel.objective_id == objective_id)

        if with_objective:
            query = query.where(InvestmentModel.objective.is_null(with_objective))

        investments = await self.get_all(query)

        return (
            [investment["InvestmentModel"] for investment in investments]
            if investments
            else []
        )

    # Dashboard
    async def get_total_invested(
        self, owner_id: uuid.UUID, investment_id: uuid.UUID = None
    ) -> float:
        query = select(func.sum(InvestmentModel.amount)).where(
            InvestmentModel.owner_id == owner_id, ~InvestmentModel.is_settled
        )

        if investment_id:
            query = query.where(InvestmentModel.id == investment_id)

        total_invested = await self.session.execute(query)
        total_invested = total_invested.scalar() or 0.0

        return total_invested

    async def get_allocation_by_investment_type(
        self, owner_id: uuid.UUID
    ) -> list[RowMapping] | None:
        # Get the latest statement per investment
        subquery_latest_period = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        # Create an alias to the self relation in InvestmentType
        parent_investment_type = aliased(InvestmentTypeModel)

        query = (
            select(
                case(
                    (
                        parent_investment_type.name.is_not(None),
                        parent_investment_type.name,
                    ),
                    else_=InvestmentTypeModel.name,
                ).label("name"),
                func.sum(InvestmentStatementModel.gross_amount).label("total"),
            )
            .select_from(InvestmentStatementModel)
            .join(
                InvestmentModel,
                InvestmentModel.id == InvestmentStatementModel.investment_id,
            )
            .join(
                InvestmentTypeModel, InvestmentTypeModel.id == InvestmentModel.type_id
            )
            .outerjoin(
                parent_investment_type,
                InvestmentTypeModel.parent_id == parent_investment_type.id,
            )
            .join(
                subquery_latest_period,
                (
                    InvestmentStatementModel.investment_id
                    == subquery_latest_period.c.investment_id
                )
                & (
                    InvestmentStatementModel.period
                    == subquery_latest_period.c.latest_period
                ),
            )
            .where(~InvestmentModel.is_settled, InvestmentModel.owner_id == owner_id)
            .group_by(
                case(
                    (
                        parent_investment_type.name.is_not(None),
                        parent_investment_type.name,
                    ),
                    else_=InvestmentTypeModel.name,
                )
            )
        )

        result = await self.get_all(query)

        return result

    async def get_allocation_by_category(self, owner_id: uuid.UUID) -> list[RowMapping]:
        subquery_latest_period = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        query = (
            select(
                InvestmentCategoryModel.name.label("name"),
                func.sum(InvestmentStatementModel.gross_amount).label("total"),
            )
            .select_from(InvestmentStatementModel)
            .join(
                InvestmentModel,
                InvestmentModel.id == InvestmentStatementModel.investment_id,
            )
            .join(
                InvestmentTypeModel, InvestmentTypeModel.id == InvestmentModel.type_id
            )
            .join(
                InvestmentCategoryModel,
                InvestmentCategoryModel.id
                == InvestmentTypeModel.investment_category_id,
            )
            .join(
                subquery_latest_period,
                (
                    InvestmentStatementModel.investment_id
                    == subquery_latest_period.c.investment_id
                )
                & (
                    InvestmentStatementModel.period
                    == subquery_latest_period.c.latest_period
                ),
            )
            .where(
                ~InvestmentModel.is_settled,
                InvestmentModel.owner_id == owner_id,
            )
            .group_by(InvestmentCategoryModel.name)
        )

        result = await self.get_all(query)

        return result

    async def get_allocation_by_custodian(
        self, owner_id: uuid.UUID
    ) -> list[RowMapping]:
        subquery_latest_period = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        query = (
            select(
                BankModel.name.label("name"),
                func.sum(InvestmentStatementModel.gross_amount).label("total"),
            )
            .select_from(InvestmentStatementModel)
            .join(
                InvestmentModel,
                InvestmentModel.id == InvestmentStatementModel.investment_id,
            )
            .join(BankModel, InvestmentModel.custodian_id == BankModel.id)
            .join(
                subquery_latest_period,
                (
                    InvestmentStatementModel.investment_id
                    == subquery_latest_period.c.investment_id
                )
                & (
                    InvestmentStatementModel.period
                    == subquery_latest_period.c.latest_period
                ),
            )
            .where(
                ~InvestmentModel.is_settled,
                InvestmentModel.owner_id == owner_id,
            )
            .group_by(BankModel.name)
        )

        result = await self.get_all(query)

        return result

    async def get_allocation_by_objectives(
        self, owner_id: uuid.UUID
    ) -> list[RowMapping] | None:
        subquery_latest_period = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        query = (
            select(
                case(
                    (InvestmentObjectiveModel.title.is_(None), literal("Não alocado")),
                    else_=InvestmentObjectiveModel.title,
                ).label("name"),
                func.sum(InvestmentStatementModel.gross_amount).label("total"),
            )
            .select_from(InvestmentStatementModel)
            .join(
                InvestmentModel,
                InvestmentModel.id == InvestmentStatementModel.investment_id,
            )
            .outerjoin(
                InvestmentObjectiveModel,
                InvestmentModel.objective_id == InvestmentObjectiveModel.id,
            )
            .join(
                subquery_latest_period,
                (
                    InvestmentStatementModel.investment_id
                    == subquery_latest_period.c.investment_id
                )
                & (
                    InvestmentStatementModel.period
                    == subquery_latest_period.c.latest_period
                ),
            )
            .where(
                ~InvestmentModel.is_settled,
                InvestmentModel.owner_id == owner_id,
            )
            .group_by(InvestmentObjectiveModel.title)
        )

        result = await self.get_all(query)

        return result

    async def get_performance_portfolio(
        self,
        owner_id: uuid.UUID,
        investment_id: uuid.UUID | None,
        indexer_id: uuid.UUID,
        period_range: int,
    ) -> list[dict] | None:
        """
        Created by: Lucas Penha de Moura - 17/10/2024
            Fetches the sum of gross, net and previous amount for the period range
        :param investment_id: the identification of the investment
        :param indexer_id: the identification of the indexer
        :param owner_id: the identification of the owner of the investment
        :param period_range: The number of past periods to fetch, if 0 return all
            available periods

        :return: RowMapping with period and total gross, net and previous amount
        """
        query = (
            select(
                InvestmentStatementModel.period,
                func.sum(InvestmentStatementModel.previous_amount).label(
                    "total_previous"
                ),
                func.sum(InvestmentStatementModel.gross_amount).label("total_gross"),
                func.sum(InvestmentStatementModel.net_amount).label("total_net"),
                IndexerSeriesModel.value.label("indexer_variation"),
                case(
                    (
                        func.sum(InvestmentStatementModel.previous_amount) != 0,
                        (
                            (
                                func.sum(InvestmentStatementModel.gross_amount)
                                - func.sum(InvestmentStatementModel.previous_amount)
                            )
                            / func.sum(InvestmentStatementModel.previous_amount)
                        )
                        * 100,
                    ),
                    else_=0,
                ).label("variation"),
            )
            .select_from(InvestmentStatementModel)
            .join(
                InvestmentModel,
                InvestmentModel.id == InvestmentStatementModel.investment_id,
            )
            .outerjoin(
                IndexerSeriesModel,
                (IndexerSeriesModel.period == InvestmentStatementModel.period)
                & (IndexerSeriesModel.indexer_id == indexer_id)
                & (
                    IndexerSeriesModel.periodicity_id
                    == uuid.UUID("dc5b3bf8-2b84-423a-9a90-e7e194e355fa")
                ),
            )
            .where(InvestmentModel.owner_id == owner_id)
            .group_by(InvestmentStatementModel.period, IndexerSeriesModel.value)
            .order_by(InvestmentStatementModel.period)
        )

        if period_range > 0:
            start_period = get_previous_period(offset=period_range)
            query = query.where(InvestmentStatementModel.period >= start_period)

        if investment_id:
            query = query.where(InvestmentStatementModel.investment_id == investment_id)

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None
