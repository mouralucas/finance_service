import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from typing import Any

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.investment import InvestmentModel, InvestmentTypeModel
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

    async def get_by_id(self, investment_id: uuid.UUID, raise_exception: bool = False) -> SQLModel:
        stmt = select(InvestmentModel).where(InvestmentModel.id == investment_id)

        investment: SQLModel = await self.get_only_one(stmt)

        if not investment and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Investment not found')

        return investment

    async def get(self, params: dict[str, Any]) -> list[SQLModel]:
        stmt = select(InvestmentModel).order_by(InvestmentModel.transaction_date)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentModel, key) == value)

        investments: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return investments

    async def create_investment_type(self, investment_type: InvestmentTypeModel) -> SQLModel:
        await self.add_one(investment_type)

        return investment_type

    async def get_investment_type(self, params: dict[str, Any]):
        # TODO: create a generic method (all gets are the same, onle change is the model)
        stmt = select(InvestmentTypeModel) # TODO: create an order by rule

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(InvestmentTypeModel, key) == value)

        investment_types: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return investment_types
