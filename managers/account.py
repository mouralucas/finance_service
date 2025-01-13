import datetime
import uuid
from typing import Any, cast
from unicodedata import category

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, func, case, RowMapping, literal_column, union_all, union, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette import status

from models.account import AccountModel, AccountTransactionModel, AccountBalanceModel
from models.core import CurrencyModel, CategoryModel
from models.credit_card import CreditCardTransactionModel
from services.utils.datetime import get_current_period


class AccountManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_account(self, account: AccountModel) -> AccountModel:
        new_account = await self.add_one(account)

        return cast(AccountModel, new_account)

    async def get_accounts(self, params: dict[str, Any]) -> list[AccountModel] | None:
        stmt = select(AccountModel)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(AccountModel, key) == value)

        accounts: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return [account['AccountModel'] for account in accounts] if accounts else None

    async def update_account(self, account: SQLModel, fields: dict[str, Any]) -> AccountModel:
        query = (
            update(AccountModel)
            .where(AccountModel.id == account.id)
            .values(**fields)
        )

        updated_account = await self.update_one(sql_statement=query, sql_model=account)

        return cast(AccountModel, updated_account)

    async def get_account_by_id(self, account_id: uuid.UUID, raise_exception: bool = False) -> AccountModel | None:
        account = await self.get_by_id(sql_model=AccountModel, object_id=account_id)

        if not account and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Account not found')

        return cast(AccountModel, account) if account else None

    # Transactions
    async def create_transaction(self, statement: AccountTransactionModel) -> AccountTransactionModel:
        new_statement = await self.add_one(statement)

        return cast(AccountTransactionModel, new_statement)

    async def update_transaction(self, transaction_id, fields: list[dict[str, Any]]) -> AccountTransactionModel:
        query = (
            update(AccountTransactionModel)
            .where(AccountTransactionModel.id == transaction_id)
            .values(**fields)
        )

        await self.session.execute(query)
        await self.session.flush()

        updated_transaction = await self.get_by_id(sql_model=AccountTransactionModel, object_id=transaction_id)

        return cast(AccountTransactionModel, updated_transaction)

    async def get_transactions(self, owner_id: uuid.UUID, start_period: int, end_period: int) -> list[dict[str, Any]]:
        transaction_alias = aliased(AccountTransactionModel)
        account_alias = aliased(AccountModel)
        currency_alias = aliased(CurrencyModel)
        transaction_currency_alias = aliased(CurrencyModel)
        category_alias = aliased(CategoryModel)

        query = (
            select(
                transaction_alias.owner_id,
                transaction_alias.id,
                transaction_alias.account_id,
                account_alias.nickname.label('account_nickname'),
                transaction_alias.currency_id,
                currency_alias.symbol.label('currency_symbol'),
                transaction_alias.amount,
                transaction_alias.period,
                transaction_alias.transaction_date,
                transaction_alias.category_id,
                category_alias.name.label('category_name'),
                transaction_alias.description,
                transaction_alias.transaction_currency_id,
                transaction_currency_alias.symbol.label('transaction_currency_symbol'),
                transaction_alias.transaction_amount,
                transaction_alias.exchange_rate,
                transaction_alias.tax_perc,
                transaction_alias.tax,
                transaction_alias.spread_perc,
                transaction_alias.spread,
                transaction_alias.effective_rate,
            )
            .select_from(transaction_alias)
            .where(
                transaction_alias.owner_id == owner_id,
                transaction_alias.period >= start_period,
                transaction_alias.period <= end_period
            )
            .join(account_alias, transaction_alias.account_id == account_alias.id)
            .join(currency_alias, transaction_alias.currency_id == currency_alias.id)
            .join(transaction_currency_alias, transaction_alias.transaction_currency_id == transaction_currency_alias.id)
            .join(category_alias, transaction_alias.category_id == category_alias.id)
            .order_by(transaction_alias.transaction_date.desc(), transaction_alias.created_at.desc())
        )

        if start_period:
            query = query.where(transaction_alias.period >= start_period)

        if end_period:
            query = query.where(transaction_alias.period <= end_period)

        transactions: list[RowMapping] = await self.get_all(query)

        return [dict(transaction.items()) for transaction in transactions] if transactions else None

    # Balance
    async def get_balance(self, account_id: uuid.UUID = None,
                          start_period: int = None, end_period: int = None,
                          current_period: bool = False) -> list[RowMapping]:
        """
        Created by: Lucas Penha de Moura - 29/09/2024

        :param account_id: The id of the account
        :param start_period: The start period for the balance
        :param end_period:  The end period for the balance
        :param current_period: Return the balance for the current period

        :return: 
        """
        query = (
            select(
                AccountBalanceModel.period,
                func.sum(AccountBalanceModel.balance).label('total_balance'),
                func.sum(AccountBalanceModel.incoming).label('total_incoming'),
                func.sum(AccountBalanceModel.outgoing).label('total_outgoing'),
            )
            .group_by(AccountBalanceModel.period)
            .order_by(AccountBalanceModel.period)
        )

        if start_period and not current_period:
            query = query.where(AccountBalanceModel.period >= start_period)

        if end_period and not current_period:
            query = query.where(AccountBalanceModel.period <= end_period)

        if account_id is not None:
            query = query.where(AccountBalanceModel.account_id == account_id)

        if current_period:
            query = query.where(AccountBalanceModel.period == get_current_period())

        balance = await self.get_all(query)

        return balance

    async def delete_balance(self, account_id: uuid.UUID) -> None:
        await self.session.execute(delete(AccountBalanceModel).where(AccountBalanceModel.account_id == account_id))
        await self.session.flush()

        return

    async def get_consolidated_transactions_by_period(self, account_id: uuid.UUID, period_range: list[int]) -> list[RowMapping] | None:
        """
        Created by: Lucas Penha de Moura - 27/09/2024
            This function feches the transactions by an account in a given period range.
            The return of this function is a list of rows that contains all incoming and outgoing transactions, plus the earnings of the account, if set.

        :param account_id: The id of the account
        :param period_range: The range of periods
        :return: A list of RowMapping containing the incoming and outgoing transactions
        """
        # TODO: create a relation that the user can choose its own 'earning' category, then add a parameter to that case
        # TODO: add group by currency_id and create a new field in balance model to save amounts in other currencies
        integer_series_cte = (
            select(literal_column(str(value)).label('period'))
            for value in period_range
        )
        period_series = union_all(*integer_series_cte).cte('integer_series')

        sql_statement = (
            select(
                period_series.c.period,
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.amount > 0, AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label("incoming"),
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.amount < 0, AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label("outgoing"),
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.category_id == uuid.UUID('dcef92cb-9664-4dc4-9adb-afe556016fe2'), AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label('earnings')
            )
            # Move the filtering conditions to the LEFT JOIN ON clause
            .outerjoin(
                AccountTransactionModel,
                (period_series.c.period == AccountTransactionModel.period) &
                (AccountTransactionModel.account_id == account_id) &
                (AccountTransactionModel.active == True)
            )
            .group_by(period_series.c.period)
            .order_by(period_series.c.period)
        )

        transactions = await self.get_all(sql_statement)

        return transactions

    async def get_consolidate_transactions_by_date_range(self, start_date: datetime.date | None = None,
                                                         end_date: datetime.date | None = None,
                                                         account_id: uuid.UUID | None = None) -> list[RowMapping] | None:
        query = (
            select(
                AccountTransactionModel.currency_id,
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.amount > 0, AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label("incoming"),
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.amount < 0, AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label("outgoing"),
                func.coalesce(
                    func.sum(
                        case(
                            (AccountTransactionModel.category_id == uuid.UUID('dcef92cb-9664-4dc4-9adb-afe556016fe2'), AccountTransactionModel.amount),
                            else_=0
                        )
                    ), 0
                ).label('earnings'),
                func.sum(AccountTransactionModel.amount).label('balance')
            )
            .select_from(AccountTransactionModel)
            .group_by(AccountTransactionModel.currency_id)
        )

        if start_date is not None:
            query = query.where(AccountTransactionModel.transaction_date >= start_date)

        if end_date is not None:
            query = query.where(AccountTransactionModel.transaction_date <= end_date)

        if account_id is not None:
            query = query.where(AccountTransactionModel.account_id == account_id)

        response = await self.get_all(query)

        return response

    async def get_account_expenses_by_category(self, owner_id: uuid.UUID, period: int) -> list[RowMapping] | None:
        account_transaction_alias = aliased(AccountTransactionModel)
        category_alias = aliased(CategoryModel)
        category_parent_alias = aliased(CategoryModel)

        query = (
            select(
                func.sum(account_transaction_alias.amount * -1).label('total'),
                category_parent_alias.id.label('category_id'),
                category_parent_alias.name.label('category_name'),
            )
            .select_from(account_transaction_alias)
            .join(category_alias, account_transaction_alias.category_id == category_alias.id)
            .join(category_parent_alias, category_alias.parent_id == category_parent_alias.id)
            .where(
                account_transaction_alias.owner_id == owner_id,
                account_transaction_alias.period == period,
                account_transaction_alias.amount < 0
            )
            .group_by(
                category_parent_alias.id,
                category_parent_alias.name,
            )
        )

        result = await self.get_all(query)

        return result if result else []