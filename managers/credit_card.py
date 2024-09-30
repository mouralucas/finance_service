import uuid
from typing import Any, cast

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from models.credit_card import CreditCardModel, CreditCardTransactionModel


class CreditCardManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_credit_card(self, card: CreditCardModel) -> SQLModel:
        new_card = await self.add_one(card)

        return new_card

    async def update_credit_card(self, credit_card: SQLModel, fields: dict[str, Any]):
        stmt = (
            update(CreditCardModel)
            .where(CreditCardModel.id == credit_card.id)
            .values(**fields)
        )

        updated_credit_card = await self.update_one(sql_statement=stmt, sql_model=credit_card)

        return updated_credit_card

    async def get_credit_card_by_id(self, card_id: uuid.UUID) -> CreditCardModel:
        stmt = select(CreditCardModel).where(CreditCardModel.id == card_id)

        credit_card = await self.get_only_one(stmt)

        credit_card = cast(CreditCardModel, credit_card)

        return credit_card

    async def get_credit_cards(self, params: dict[str, Any]) -> list[RowMapping]:
        stmt = select(CreditCardModel).order_by(CreditCardModel.nickname)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(CreditCardModel, key) == value)

        credit_cards: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return credit_cards

    ## Bills entries
    async def create_bill_entry(self, bill_entries: list[CreditCardTransactionModel]) -> list[SQLModel]:
        new_bill_entries = await self.add_all(bill_entries)
        [await self.session.refresh(i) for i in new_bill_entries]

        return new_bill_entries
