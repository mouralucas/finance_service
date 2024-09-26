import uuid
from typing import Any, Sequence, cast

from fastapi import HTTPException
from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy import select, update, Executable, Row, func, case, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.account import AccountModel, AccountStatementModel


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

        if raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Account not found')

        account = cast(AccountModel, account)

        return account

    # Statement
    async def create_statement(self, statement: AccountStatementModel) -> SQLModel:
        new_statement = await self.add_one(statement)

        return new_statement

    async def get_statement(self, sql_statement: Executable) -> list[SQLModel]:
        statements_entries: list[SQLModel] = await self.get_all(sql_statement)

        return statements_entries

    async def get_balance(self, account_id: uuid.UUID) -> Sequence[Row[tuple[Any, ...] | Any]]:
        sql_statement: Executable = (
            select(
                AccountStatementModel.period,
                func.sum(AccountStatementModel.amount).label("total_amount"),
                func.sum(
                    case(
                        (AccountStatementModel.amount > 0, AccountStatementModel.amount),
                        else_=0
                    )
                ).label("incoming"),
                func.sum(
                    case(
                        (AccountStatementModel.amount < 0, AccountStatementModel.amount),
                        else_=0
                    )
                ).label("outgoing"),
                func.sum(
                    case(
                        (AccountStatementModel.category_id == 'dcef92cb-9664-4dc4-9adb-afe556016fe2', AccountStatementModel.amount),
                        else_=0
                    )
                ).label('earnings')

            )
            .where(AccountStatementModel.account_id == account_id, AccountStatementModel.active == True)
            .group_by(AccountStatementModel.period)
            .order_by(AccountStatementModel.period)
        )

        entries = await self.get_all(sql_statement)

        return entries