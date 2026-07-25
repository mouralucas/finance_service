import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models.base import SQLModel
from sqlalchemy import Executable, RowMapping, and_, case, func, literal, select, update
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

        updated_investment = await self.get_investment_by_id(id=investment_id)

        return cast(InvestmentModel, updated_investment)

    async def get_investment_by_id(
        self, id: uuid.UUID, raise_exception: bool = False
    ) -> InvestmentModel | None:
        investment = await self.get_by_id(InvestmentModel, id)

        if not investment and raise_exception:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Investment not found"
            )

        return cast(InvestmentModel, investment) if investment else None

    async def get_investments(
        self,
        owner_id: uuid.UUID,
        is_settled: bool | None,
        investment_type_id: uuid.UUID | None = None,
    ) -> list[dict[Any, Any]] | None:
        investment_alias = aliased(InvestmentModel)
        currency_alias = aliased(CurrencyModel)
        type_alias = aliased(InvestmentTypeModel)
        bank_alias = aliased(BankModel)
        statement_alias = aliased(InvestmentStatementModel)

        statement_sum_cte = (
            select(
                InvestmentStatementModel.investment_id.label("investment_id"),
                func.sum(InvestmentStatementModel.contribution).label(
                    "total_contribution"
                ),
                func.sum(InvestmentStatementModel.withdrawn).label("total_withdrawn"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .cte("statement_sum")
        )

        latest_statement_cte = (
            select(
                InvestmentStatementModel.investment_id.label("investment_id"),
                func.max(InvestmentStatementModel.period).label("latest_period"),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .cte("latest_statement")
        )

        initial_adjusted = func.coalesce(
            statement_sum_cte.c.total_contribution, 0
        ) - func.coalesce(statement_sum_cte.c.total_withdrawn, 0)

        initial_adjusted_safe = func.nullif(initial_adjusted, 0)

        percentage_change = case(
            (
                and_(
                    statement_alias.gross_amount.is_not(None),
                    initial_adjusted_safe.is_not(None),
                ),
                (
                    (statement_alias.gross_amount - initial_adjusted_safe)
                    / initial_adjusted_safe
                )
                * 100,
            ),
            else_=0,
        ).label("percentage_change")

        query = (
            select(
                investment_alias.id,
                investment_alias.custodian_id,
                investment_alias.account_id,
                bank_alias.name.label("custodian_name"),
                investment_alias.name,
                investment_alias.transaction_date,
                investment_alias.maturity_date,
                investment_alias.contracted_rate,
                investment_alias.quantity,
                investment_alias.price,
                investment_alias.amount,
                func.coalesce(statement_sum_cte.c.total_contribution, 0).label(
                    "total_contribution"
                ),
                func.coalesce(statement_sum_cte.c.total_withdrawn, 0).label(
                    "total_withdrawn"
                ),
                currency_alias.id.label("currency_id"),
                currency_alias.symbol.label("currency_symbol"),
                type_alias.id.label("type_id"),
                type_alias.name.label("investment_type_name"),
                investment_alias.liquidity_id,
                investment_alias.indexer_id,
                investment_alias.indexer_type_id,
                investment_alias.country_id,
                investment_alias.is_settled,
                investment_alias.settlement_date,
                investment_alias.settlement_amount,
                investment_alias.observation,
                case(
                    (
                        statement_alias.gross_amount.is_(None),
                        investment_alias.amount,
                    ),
                    else_=statement_alias.gross_amount,
                ).label("gross_amount"),
                percentage_change,
                statement_alias.period,
            )
            .join(currency_alias, investment_alias.currency_id == currency_alias.id)
            .join(type_alias, investment_alias.type_id == type_alias.id)
            .join(bank_alias, investment_alias.custodian_id == bank_alias.id)
            .outerjoin(
                statement_sum_cte,
                statement_sum_cte.c.investment_id == investment_alias.id,
            )
            .outerjoin(
                latest_statement_cte,
                latest_statement_cte.c.investment_id == investment_alias.id,
            )
            .outerjoin(
                statement_alias,
                and_(
                    statement_alias.investment_id == investment_alias.id,
                    statement_alias.period == latest_statement_cte.c.latest_period,
                ),
            )
            .where(investment_alias.owner_id == owner_id)
            .order_by(investment_alias.transaction_date)
        )

        if is_settled is not None:
            query = query.where(investment_alias.is_settled.is_(is_settled))

        if investment_type_id:
            query = query.where(investment_alias.type_id == investment_type_id)

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

        # Total amount of the previous period
        previous_gross = func.lag(m.gross_amount).over(
            partition_by=m.investment_id, order_by=m.period
        )

        # Adjusted value of the previous period (contribution - withdrawn)
        adjusted_previous = (
            func.coalesce(previous_gross, 0)
            + func.coalesce(m.contribution, 0)
            - func.coalesce(m.withdrawn, 0)
        )

        # Absolute variation
        variation_value = m.gross_amount - adjusted_previous

        # Percentage variation
        variation_percent = case(
            (adjusted_previous != 0, (variation_value / adjusted_previous * 100)),
            else_=0,
        )

        stmt = (
            select(
                m.id,
                m.investment_id,
                m.period,
                func.coalesce(previous_gross, 0).label("previous_amount"),
                m.gross_amount,
                m.contribution,
                m.withdrawn,
                m.total_tax,
                m.tax_detail,
                m.total_fee,
                m.fee_detail,
                m.reference_date,
                m.at_maturity,
                m.currency_id,
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

    async def get_investment_type(self) -> list[dict[Any, Any]] | None:
        query: Executable = select(
            InvestmentTypeModel.id,
            InvestmentTypeModel.name,
            InvestmentTypeModel.description,
            InvestmentTypeModel.parent_id,
            InvestmentTypeModel.country_id,
            InvestmentTypeModel.investment_category_id,
        ).order_by(InvestmentTypeModel.name)

        investment_types: list[RowMapping] | None = await self.get_all(query)

        return (
            [dict(type.items()) for type in investment_types]
            if investment_types
            else None
        )

    # Investment objectives
    async def create_objective(
        self, objective: InvestmentObjectiveModel
    ) -> SQLModel | None:
        new_objective = await self.add_one(objective)

        return new_objective

    async def get_objectives(
        self, owner_id: str, objective_id: uuid.UUID | None = None
    ) -> list[dict[Any, Any]] | None:
        latest_date_subq = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.reference_date).label(
                    "max_reference_date"
                ),
            )
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        latest_stmt_subq = (
            select(
                InvestmentStatementModel.investment_id,
                InvestmentStatementModel.gross_amount,
            )
            .join(
                latest_date_subq,
                (
                    InvestmentStatementModel.investment_id
                    == latest_date_subq.c.investment_id
                )
                & (
                    InvestmentStatementModel.reference_date
                    == latest_date_subq.c.max_reference_date
                ),
            )
            .subquery()
        )

        query = (
            select(
                InvestmentObjectiveModel.id,
                InvestmentObjectiveModel.owner_id,
                InvestmentObjectiveModel.title,
                InvestmentObjectiveModel.description,
                InvestmentObjectiveModel.currency_id,
                InvestmentObjectiveModel.amount,
                InvestmentObjectiveModel.estimated_deadline.label("estimate_deadline"),
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
        self,
        owner_id: uuid.UUID,
        is_settled: bool | None = None,
        investment_id: uuid.UUID | None = None,
    ) -> float:
        query = select(func.sum(InvestmentModel.amount)).where(
            InvestmentModel.owner_id == owner_id,
        )

        if is_settled is not None and is_settled:
            query = query.where(InvestmentModel.is_settled.is_(True))
        elif is_settled is not None and not is_settled:
            query = query.where(InvestmentModel.is_settled.is_(False))

        if investment_id:
            query = query.where(InvestmentModel.id == investment_id)

        total_invested = await self.session.execute(query)
        total_invested = total_invested.scalar() or 0.0

        return float(total_invested)

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
        is_settled: bool = False,
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
        m = InvestmentStatementModel

        # ---------------------------
        # 1) Window functions
        # ---------------------------

        previous_gross = func.lag(m.gross_amount).over(
            partition_by=m.investment_id,
            order_by=m.period,
        )

        previous_adjusted = (
            func.coalesce(previous_gross, 0)
            + func.coalesce(m.contribution, 0)
            - func.coalesce(m.withdrawn, 0)
        )

        # ---------------------------
        # 2) Subquery with window functions
        # ---------------------------

        subq = select(
            m.id.label("id"),
            m.investment_id.label("investment_id"),
            m.period.label("period"),
            m.gross_amount.label("gross_amount"),
            m.net_amount.label("net_amount"),
            previous_adjusted.label("previous_adjusted"),
        ).subquery()

        sq = subq  # alias curto

        # ---------------------------
        # 3) Final  query with joins and filters
        # ---------------------------

        query = (
            select(
                sq.c.period,
                func.sum(sq.c.previous_adjusted).label("total_previous_adjusted"),
                func.sum(sq.c.gross_amount).label("total_gross"),
                func.sum(sq.c.net_amount).label("total_net"),
                IndexerSeriesModel.value.label("indexer_variation"),
                case(
                    (
                        func.sum(sq.c.previous_adjusted) != 0,
                        (
                            (
                                func.sum(sq.c.gross_amount)
                                - func.sum(sq.c.previous_adjusted)
                            )
                            / func.sum(sq.c.previous_adjusted)
                        )
                        * 100,
                    ),
                    else_=0,
                ).label("variation"),
            )
            .select_from(sq)
            .join(
                InvestmentModel,
                InvestmentModel.id == sq.c.investment_id,
            )
            .outerjoin(
                IndexerSeriesModel,
                (IndexerSeriesModel.period == sq.c.period)
                & (IndexerSeriesModel.indexer_id == indexer_id)
                & (
                    IndexerSeriesModel.periodicity_id
                    == uuid.UUID("dc5b3bf8-2b84-423a-9a90-e7e194e355fa")
                ),
            )
            .where(InvestmentModel.owner_id == owner_id)
            .group_by(sq.c.period, IndexerSeriesModel.value)
            .order_by(sq.c.period)
        )

        # For settled investments, show everything
        if period_range > 0 and not is_settled:
            start_period = get_previous_period(offset=period_range)
            query = query.where(sq.c.period >= start_period)

        if investment_id:
            query = query.where(sq.c.investment_id == investment_id)

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None

    async def get_total_active_gross(
        self,
        owner_id: uuid.UUID,
    ) -> float:
        m = InvestmentStatementModel

        latest_stmt = (
            select(
                m.investment_id,
                m.gross_amount,
            )
            .distinct(m.investment_id)
            .order_by(m.investment_id, m.period.desc())
            .subquery()
        )

        ls = latest_stmt

        query = (
            select(func.sum(ls.c.gross_amount))
            .select_from(ls)
            .join(
                InvestmentModel,
                InvestmentModel.id == ls.c.investment_id,
            )
            .where(
                InvestmentModel.owner_id == owner_id,
                InvestmentModel.is_settled.is_(False),
            )
        )

        result = await self.session.execute(query)
        total = result.scalar()

        return float(total) if total else 0.0

    async def get_total_last_month_active_gross(
        self,
        owner_id: uuid.UUID,
    ) -> dict:
        m = InvestmentStatementModel

        last_period = get_previous_period(offset=1)

        # ---------------------------
        # 1) Total gross do mês passado
        # ---------------------------
        total_query = (
            select(
                func.sum(m.gross_amount).label("total_gross"),
                func.count(func.distinct(m.investment_id)).label("stmt_count"),
            )
            .join(
                InvestmentModel,
                InvestmentModel.id == m.investment_id,
            )
            .where(
                InvestmentModel.owner_id == owner_id,
                InvestmentModel.is_settled.is_(False),
                m.period == last_period,
            )
        )

        # ---------------------------
        # 2) Total de investimentos ativos
        # ---------------------------
        active_query = select(func.count(InvestmentModel.id)).where(
            InvestmentModel.owner_id == owner_id,
            InvestmentModel.is_settled.is_(False),
        )

        total_result = await self.session.execute(total_query)
        active_result = await self.session.execute(active_query)

        total_row = total_result.one()
        active_count = active_result.scalar() or 0

        total_gross = total_row.total_gross or 0
        stmt_count = total_row.stmt_count or 0

        return {
            "total_gross_last_month": float(total_gross),
            "all_have_statement_last_month": stmt_count == active_count,
            "missing_count": active_count - stmt_count,
        }

    async def get_financial_dashboard_total_evolution(
        self,
        owner_id: uuid.UUID,
        investment_id: uuid.UUID | None,
        indexer_id: uuid.UUID,
        period_range: int,
        is_settled: bool = False,
    ):
        m = InvestmentStatementModel

        # ---------------------------
        # 1) Window base (lag)
        # ---------------------------

        previous_gross = func.lag(m.gross_amount).over(
            partition_by=m.investment_id,
            order_by=m.period,
        )

        previous_adjusted = (
            func.coalesce(previous_gross, 0)
            + func.coalesce(m.contribution, 0)
            - func.coalesce(m.withdrawn, 0)
        )

        base_subq = select(
            m.id.label("id"),
            m.investment_id.label("investment_id"),
            m.period.label("period"),
            m.gross_amount.label("gross_amount"),
            previous_adjusted.label("previous_adjusted"),
        ).subquery()

        sq = base_subq

        # ---------------------------
        # 2) Apply filters BEFORE ranking
        # ---------------------------

        filtered_sq = (
            select(sq)
            .join(InvestmentModel, InvestmentModel.id == sq.c.investment_id)
            .where(InvestmentModel.owner_id == owner_id)
        )

        if investment_id:
            filtered_sq = filtered_sq.where(sq.c.investment_id == investment_id)

        if period_range > 0 and not is_settled:
            start_period = get_previous_period(offset=period_range)
            filtered_sq = filtered_sq.where(sq.c.period >= start_period)

        filtered_sq = filtered_sq.subquery()

        # ---------------------------
        # 3) Row number (first / last)
        # ---------------------------

        first_rn = func.row_number().over(
            partition_by=filtered_sq.c.investment_id,
            order_by=filtered_sq.c.period.asc(),
        )

        last_rn = func.row_number().over(
            partition_by=filtered_sq.c.investment_id,
            order_by=filtered_sq.c.period.desc(),
        )

        ranked_sq = select(
            filtered_sq.c.investment_id,
            filtered_sq.c.period,
            filtered_sq.c.previous_adjusted,
            filtered_sq.c.gross_amount,
            first_rn.label("rn_first"),
            last_rn.label("rn_last"),
        ).subquery()

        # ---------------------------
        # 4) Aggregation (dashboard)
        # ---------------------------

        initial_amount = func.sum(
            case(
                (ranked_sq.c.rn_first == 1, ranked_sq.c.previous_adjusted),
                else_=0,
            )
        )

        final_amount = func.sum(
            case(
                (ranked_sq.c.rn_last == 1, ranked_sq.c.gross_amount),
                else_=0,
            )
        )

        variation = case(
            (
                initial_amount != 0,
                ((final_amount - initial_amount) / initial_amount) * 100,
            ),
            else_=0,
        )

        # ---------------------------
        # 5) Final query
        # ---------------------------

        query = select(
            initial_amount.label("initial_amount"),
            final_amount.label("final_amount"),
            variation.label("total_variation"),
        )

        result = await self.session.execute(query)
        row = result.one()

        return {
            "initial_amount": row.initial_amount or 0,
            "final_amount": row.final_amount or 0,
            "total_variation": row.total_variation or 0,
        }
