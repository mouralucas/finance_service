import uuid
from typing import Any, cast

from rolf_common.managers import BaseDataManager
from rolf_common.models.base import SQLModel
from sqlalchemy import RowMapping, case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from models.core import CategoryModel, CurrencyModel
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

        updated_credit_card = await self.update_one(
            sql_statement=stmt, sql_model=credit_card
        )

        return updated_credit_card

    async def get_credit_card_by_id(self, card_id: uuid.UUID) -> CreditCardModel:
        stmt = select(CreditCardModel).where(CreditCardModel.id == card_id)

        credit_card = await self.get_only_one(stmt)

        credit_card = cast(CreditCardModel, credit_card)

        return credit_card

    async def get_credit_cards(
        self, owner_id, credit_card_id=None, is_active=None
    ) -> list[RowMapping] | None:
        query = (
            select(
                CreditCardModel.id.label("credit_card_id"),
                CreditCardModel.owner_id,
                CreditCardModel.nickname,
                CreditCardModel.account_id,
                CreditCardModel.issue_date,
                CreditCardModel.cancellation_date,
                CreditCardModel.currency_id,
                CreditCardModel.due_day,
                CreditCardModel.close_day,
                CreditCardModel.active,
            )
            .where(CreditCardModel.owner_id == owner_id)
            .order_by(CreditCardModel.nickname)
        )

        if credit_card_id is not None:
            query = query.where(CreditCardModel.id == credit_card_id)

        if is_active is not None:
            query = query.where(CreditCardModel.active == is_active)

        credit_cards: list[RowMapping] | None = await self.get_all(query)

        return credit_cards

    # Transactions
    async def create_credit_card_transaction(
        self, transactions: list[CreditCardTransactionModel]
    ) -> list[CreditCardTransactionModel] | None:
        new_bill_entries = await self.add_all(transactions)
        [await self.session.refresh(i) for i in new_bill_entries]

        return [
            cast(CreditCardTransactionModel, transaction)
            for transaction in new_bill_entries
        ]

    async def get_credit_card_transactions(
        self,
        owner_id: uuid.UUID,
        start_period: int | None = None,
        end_period: int | None = None,
        parent_id: int | None = None,
    ) -> list[dict[Any, Any]] | None:
        transaction_alias = aliased(CreditCardTransactionModel)
        category_alias = aliased(CategoryModel)
        card_alias = aliased(CreditCardModel)
        currency_alias = aliased(CurrencyModel)
        transaction_currency_alias = aliased(CurrencyModel)

        query = (
            select(
                transaction_alias.id,
                transaction_alias.period,
                transaction_alias.transaction_date,
                func.round_(transaction_alias.amount, 2).label("amount"),
                transaction_alias.description,
                transaction_alias.due_date,
                transaction_alias.credit_card_id,
                card_alias.nickname.label("credit_card_nickname"),
                transaction_alias.category_id,
                category_alias.name.label("category_name"),
                transaction_alias.currency_id,
                currency_alias.symbol.label("currency_symbol"),
                func.round_(transaction_alias.transaction_amount, 2).label(
                    "transaction_amount"
                ),
                transaction_alias.transaction_currency_id,
                transaction_currency_alias.symbol.label("transaction_currency_symbol"),
                transaction_alias.is_installment,
                transaction_alias.current_installment,
                transaction_alias.installments,
                transaction_alias.created_at,
                transaction_alias.edited_at,
            )
            .select_from(transaction_alias)
            .where(transaction_alias.owner_id == owner_id)
            .join(card_alias, transaction_alias.credit_card_id == card_alias.id)
            .join(category_alias, transaction_alias.category_id == category_alias.id)
            .join(currency_alias, transaction_alias.currency_id == currency_alias.id)
            .join(
                transaction_currency_alias,
                transaction_alias.transaction_currency_id
                == transaction_currency_alias.id,
            )
            .order_by(
                transaction_alias.transaction_date.desc(),
                transaction_alias.created_at.desc(),
            )
        )

        if start_period is not None:
            query = query.where(transaction_alias.period >= start_period)

        if end_period is not None:
            query = query.where(transaction_alias.period <= end_period)

        if parent_id is not None:
            query = query.where(transaction_alias.parent_id == parent_id)

        transactions = await self.get_all(query)

        return (
            [dict(transaction.items()) for transaction in transactions]
            if transactions
            else None
        )

    # Bill
    async def get_bill_history_aggregated(
        self, owner_id: uuid.UUID, start_period: int, end_period: int
    ) -> list[dict[Any, Any]] | None:
        """
        Created by: Lucas Penha de Moura - 29/10/2024

        :param owner_id: The id og the owner of the transactions
        :param start_period: the start period of the transactions
        :param end_period: the end period of the transactions
        :return: A dict with the total spent with all credit cards by period
        """
        query = (
            select(
                CreditCardModel.nickname,
                CreditCardTransactionModel.period,
                func.sum(CreditCardTransactionModel.amount * -1).label("total_amount"),
            )
            .select_from(CreditCardTransactionModel)
            .outerjoin(
                CreditCardModel,
                CreditCardModel.id == CreditCardTransactionModel.credit_card_id,
            )
            .where(
                CreditCardTransactionModel.owner_id == owner_id,
                CreditCardTransactionModel.period >= start_period,
                CreditCardTransactionModel.period <= end_period,
            )
            .group_by(CreditCardModel.nickname, CreditCardTransactionModel.period)
            .order_by(CreditCardTransactionModel.period)
        )

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else None

    async def get_bill_history_by_card(
        self, owner_id: uuid.UUID, start_period: int, end_period: int
    ) -> list[dict[Any, Any]] | None:
        """
        Created by: Lucas Penha de Moura - 30/10/2024

            This query fetches the total amount spent by card/period for the owner
                in the period range

        :param owner_id: The id og the owner of the transactions
        :param start_period: the start period of the transactions
        :param end_period: the end period of the transactions
        :return: A dict with the total spent by credit card/period
        """
        query = (
            select(
                CreditCardTransactionModel.period,
                CreditCardModel.nickname.label("credit_card"),
                CurrencyModel.symbol.label("currency_symbol"),
                func.round_(
                    func.sum(
                        case(
                            (
                                CreditCardTransactionModel.is_installment,
                                CreditCardTransactionModel.transaction_amount * -1,
                            ),
                            else_=0,
                        )
                    ),
                    2,
                ).label("total_installments"),
                func.round_(func.sum(CreditCardTransactionModel.amount * -1), 2).label(
                    "total_amount"
                ),
            )
            .select_from(CreditCardTransactionModel)
            .join(
                CreditCardModel,
                CreditCardModel.id == CreditCardTransactionModel.credit_card_id,
            )
            .join(CurrencyModel, CreditCardModel.currency_id == CurrencyModel.id)
            .where(
                CreditCardTransactionModel.owner_id == owner_id,
                CreditCardTransactionModel.period >= start_period,
                CreditCardTransactionModel.period <= end_period,
            )
            .group_by(
                CreditCardTransactionModel.period,
                CreditCardModel.nickname,
                CurrencyModel.symbol,
            )
            .order_by(CreditCardTransactionModel.period.desc())
        )

        result = await self.get_all(query)

        return [dict(i.items()) for i in result] if result else []

    # Dashboard
    async def get_credit_card_expense_by_category(
        self, owner_id: uuid.UUID, period: int
    ) -> list[RowMapping]:
        credit_card_transaction_alias = aliased(CreditCardTransactionModel)
        category_alias = aliased(CategoryModel)
        category_parent_alias = aliased(CategoryModel)

        query = (
            select(
                func.sum(credit_card_transaction_alias.amount * -1).label("total"),
                category_parent_alias.id.label("category_id"),
                category_parent_alias.name.label("category_name"),
            )
            .select_from(credit_card_transaction_alias)
            .join(
                category_alias,
                credit_card_transaction_alias.category_id == category_alias.id,
            )
            .join(
                category_parent_alias,
                category_alias.parent_id == category_parent_alias.id,
            )
            .where(
                credit_card_transaction_alias.owner_id == owner_id,
                credit_card_transaction_alias.period == period,
                credit_card_transaction_alias.amount < 0,
            )
            .group_by(
                category_parent_alias.id,
                category_parent_alias.name,
            )
        )

        result = await self.get_all(query)

        return result if result else []
