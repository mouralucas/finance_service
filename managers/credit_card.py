import uuid
from typing import Any, cast

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, RowMapping, func
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

    async def get_credit_cards(self, params: dict[str, Any]) -> list[CreditCardModel] | None:
        stmt = select(CreditCardModel).order_by(CreditCardModel.nickname)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(CreditCardModel, key) == value)

        credit_cards: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return [credit_card['CreditCardModel'] for credit_card in credit_cards] if credit_cards else None

    # Transactions
    async def create_bill_entry(self, bill_entries: list[CreditCardTransactionModel]) -> list[SQLModel]:
        new_bill_entries = await self.add_all(bill_entries)
        [await self.session.refresh(i) for i in new_bill_entries]

        return new_bill_entries

    # Bill
    async def get_bill(self, owner_id: uuid.UUID,
                       start_period: int, end_period: int, credit_card_id: uuid.UUID = None) -> list[dict[str, Any]]:

        query = (
            select(
                CreditCardTransactionModel.period,
                func.sum(
                    CreditCardTransactionModel.amount * -1
                ).label('total_amount')
            )
            .select_from(CreditCardTransactionModel)
            .where(
                CreditCardTransactionModel.owner_id == owner_id,
                CreditCardTransactionModel.period >= start_period,
                CreditCardTransactionModel.period <= end_period
            )
            .group_by(CreditCardTransactionModel.period)
            .order_by(CreditCardTransactionModel.period)
        )

        # .select_from(CreditCardTransactionModel))
        # .where(CreditCardTransactionModel.owner_id == owner_id)
        # .group_by(CreditCardTransactionModel.period)

        if credit_card_id:
            query = query.where(CreditCardTransactionModel.credit_card_id == credit_card_id)

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None



