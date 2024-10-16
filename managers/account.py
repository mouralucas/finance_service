import uuid
from typing import Any, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, Executable, func, case, RowMapping, literal_column, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.account import AccountModel, AccountTransactionModel, AccountBalanceModel


class AccountManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_account(self, account: AccountModel) -> SQLModel:
        new_account = await self.add_one(account)

        return new_account

    async def get_accounts(self, params: dict[str, Any]) -> list[RowMapping]:
        stmt = select(AccountModel)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(AccountModel, key) == value)

        accounts: list[RowMapping] = await self.get_all(stmt, unique_result=True)

        return accounts

    async def update_account(self, account: SQLModel, fields: dict[str, Any]) -> SQLModel:
        stmt = (
            update(AccountModel)
            .where(AccountModel.id == account.id)
            .values(**fields)
        )

        updated_account = await self.update_one(sql_statement=stmt, sql_model=account)

        return updated_account

    async def get_account_by_id(self, account_id: uuid.UUID, raise_exception: bool = False) -> AccountModel | None:
        account = await self.get_by_id(sql_model=AccountModel, object_id=account_id)

        if not account and raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Account not found')

        account = cast(AccountModel, account)

        return account

    # Statement
    async def create_statement(self, statement: AccountTransactionModel) -> SQLModel:
        new_statement = await self.add_one(statement)

        return new_statement

    async def get_statement(self, sql_statement: Executable) -> list[RowMapping]:
        statements_entries: list[RowMapping] = await self.get_all(sql_statement)

        return statements_entries


    async def get_balance(self, account_id: uuid.UUID, start_period: int, end_period: int) -> list[RowMapping]:
        sql_statement = select(AccountBalanceModel).order_by(AccountBalanceModel.period)

        if start_period:
            sql_statement = sql_statement.where(AccountBalanceModel.period >= start_period)

        if end_period:
            sql_statement = sql_statement.where(AccountBalanceModel.period <= end_period)

        balance = await self.get_all(sql_statement)

        return balance


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
        # period_series = (
        #     select(func.unnest(literal_column(f'ARRAY{period_range}')).label('period'))
        #     .cte('integer_series')
        # )
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

        print(sql_statement)

        transactions = await self.get_all(sql_statement)

        return transactions
