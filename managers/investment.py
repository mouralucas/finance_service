import uuid

from fastapi import HTTPException
from sqlalchemy import select, update, Executable, RowMapping
from typing import Any, List, cast

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.investment import InvestmentModel, InvestmentTypeModel, InvestmentStatementModel, InvestmentObjectiveModel
from schemas.request.investment import LiquidateInvestmentRequest
from schemas.response.investment import LiquidateInvestmentResponse


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

        if raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Investment not found')

        investment = cast(InvestmentModel, investment)

        return investment

    async def get(self, params: dict[str, Any]) -> list[SQLModel]:
        stmt = select(InvestmentModel).order_by(InvestmentModel.transaction_date)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentModel, key) == value)

        investments: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return investments

    # Investment statement
    async def create_statement(self, statement: InvestmentStatementModel) -> SQLModel:
        await self.add_one(statement)

        return statement

    async def get_statement(self, params: dict[str, Any]) -> list[RowMapping] | None:
        stmt = select(InvestmentStatementModel).order_by(InvestmentStatementModel.period)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentStatementModel, key) == value)

        statements: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return statements

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

    async def get_investment_by_objective(self, params: dict[str, Any]) -> list[RowMapping]:
        sql_statement = select(InvestmentModel).where(InvestmentModel.objective_id == None).order_by(InvestmentModel.transaction_date)

        return await self.get_all(sql_statement)


