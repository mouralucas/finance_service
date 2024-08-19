from typing import Any

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.credit_card import CreditCardModel


class CreditCardManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_credit_card(self, card: CreditCardModel) -> SQLModel:
        new_card = await self.add_one(card)

        return new_card

    async def get_credit_cards(self, params: dict[str, Any]) -> list[SQLModel]:
        stmt = select(CreditCardModel).order_by(CreditCardModel.nickname)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(CreditCardModel, key) == value)

        credit_cards: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return credit_cards
    