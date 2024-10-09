import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, Executable, RowMapping, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette import status

from models.investment import InvestmentModel, InvestmentTypeModel, InvestmentStatementModel, InvestmentObjectiveModel


class InvestmentManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create(self, investment: InvestmentModel) -> SQLModel:
        await self.add_one(investment)

        return investment

    async def update(self, investment: SQLModel, fields: dict[str, Any]) -> SQLModel:
        stmt = (
            update(InvestmentModel)
            .where(InvestmentModel.id == investment.id)
            .values(**fields)
        )

        updated_item = await self.update_one(sql_statement=stmt, sql_model=investment)

        return updated_item

    async def get_investment_by_id(self, investment_id: uuid.UUID, raise_exception: bool = False) -> InvestmentModel | None:
        investment = await self.get_by_id(InvestmentModel, investment_id)

        if not investment and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Investment not found')

        investment = cast(InvestmentModel, investment)

        return investment

    async def get_investments(self, params: dict[str, Any]) -> list[RowMapping]:
        sql_statement = select(InvestmentModel).order_by(InvestmentModel.transaction_date)

        for key, value in params.items():
            if value:
                sql_statement = sql_statement.where(getattr(InvestmentModel, key) == value)

        investments: list[RowMapping] = await self.get_all(sql_statement, unique_result=True)

        return investments

    # Investment statement
    async def create_statement(self, statement: InvestmentStatementModel) -> SQLModel:
        await self.add_one(statement)

        return statement

    async def get_statement(self, params: dict[str, Any]) -> list[InvestmentStatementModel] | None:
        stmt = select(InvestmentStatementModel).order_by(InvestmentStatementModel.period)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentStatementModel, key) == value)

        result: list[RowMapping] = await self.get_all(stmt, unique_result=True)
        statements = [cast(InvestmentStatementModel, statement) for statement in result]

        return statements

    async def get_latest_investment_statements(self, investment_ids: list[uuid.UUID]):
        subquery = (
            select(
                InvestmentStatementModel.investment_id,
                func.max(InvestmentStatementModel.period).label('max_period')
            )
            .where(InvestmentStatementModel.investment_id.in_(investment_ids))
            .group_by(InvestmentStatementModel.investment_id)
            .subquery()
        )

        sql_statement = (
            select(
                InvestmentStatementModel.investment_id,
                InvestmentStatementModel.period,
                InvestmentStatementModel.gross_amount,
            )
            .join(
                subquery,
                (InvestmentStatementModel.investment_id == subquery.c.investment_id) &
                (InvestmentStatementModel.period == subquery.c.max_period)
            )
        )

        result = await self.get_all(sql_statement)

        return result

    # Investment Types
    async def create_investment_type(self, investment_type: InvestmentTypeModel) -> SQLModel:
        await self.add_one(investment_type)

        return investment_type

    async def get_investment_type(self) -> list[RowMapping]:
        sql_statement: Executable = select(InvestmentTypeModel).order_by(InvestmentTypeModel.name)

        investment_types: list[RowMapping] = await self.get_all(sql_statement)

        return investment_types

    # Investment objectives
    async def create_objective(self, objective: InvestmentObjectiveModel) -> SQLModel:
        new_objective = await self.add_one(objective)

        return new_objective

    async def get_investment_objectives(self, params: dict[str, Any]) -> list[RowMapping] | None:
        stmt = select(InvestmentObjectiveModel)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentObjectiveModel, key) == value)

        investment_objectives: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return investment_objectives

    async def get_objective_by_id(self, objective_id: uuid.UUID) -> InvestmentObjectiveModel | None:
        objective = await self.get_by_id(InvestmentObjectiveModel, objective_id)

        return cast(InvestmentObjectiveModel, objective)
