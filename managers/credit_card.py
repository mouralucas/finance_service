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
    async def get_bill_history_aggregated(self, owner_id: uuid.UUID, start_period: int, end_period: int) -> list[dict[str, Any]]:
        """
        Created by: Lucas Penha de Moura - 29/10/2024

        :param owner_id: The id og the owner of the transactions
        :param start_period: the start period of the transactions
        :param end_period: the end period of the transactions
        :return: A dict with the total spent with all credit cards by period
        """
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

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None

    async def get_bill_history_by_card(self, owner_id: uuid.UUID, start_period: int, end_period: int) -> list[dict[str, Any]] | None:
        """
        Created by: Lucas Penha de Moura - 30/10/2024

        :param owner_id: The id og the owner of the transactions
        :param start_period: the start period of the transactions
        :param end_period: the end period of the transactions
        :return: A dict with the total spent by credit card/period
        """
        query = (
            select(
                CreditCardTransactionModel.period,
                CreditCardModel.nickname.label('credit_card'),
                func.round_(
                    func.sum(CreditCardTransactionModel.amount * -1)
                    , 2
                ).label('total_amount')
            )
            .select_from(CreditCardTransactionModel)
            .join(CreditCardModel, CreditCardModel.id == CreditCardTransactionModel.credit_card_id)
            .where(
                CreditCardTransactionModel.owner_id == owner_id,
                CreditCardTransactionModel.period >= start_period,
                CreditCardTransactionModel.period <= end_period
            )
            .group_by(
                CreditCardTransactionModel.period,
                CreditCardModel.nickname
            )
            .order_by(CreditCardTransactionModel.period)
        )

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None
