import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from typing import Any

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.account import AccountModel, AccountStatementModel


class AccountManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_account(self, account: AccountModel) -> SQLModel:
        new_account = await self.add_one(account)

        return new_account

    async def get_accounts(self, params: dict[str, Any]) -> list[SQLModel]:
        stmt = select(AccountModel)

        for key, value in params.items():
            if value:
                stmt = stmt.where(getattr(AccountModel, key) == value)

        accounts: list[SQLModel] = await self.get_all(stmt, unique_result=True)

        return accounts

    async def update_account(self, account: SQLModel, fields: dict[str, Any]) -> SQLModel:
        stmt = (
            update(AccountModel)
            .where(AccountModel.id == account.id)
            .values(**fields)
        )

        updated_account = await self.update_one(sql_statement=stmt, sql_model=account)

        return updated_account

    async def get_account_by_id(self, account_id: uuid.UUID, raise_exception: bool = False) -> SQLModel:
        account = await self.get_by_id(sql_model=AccountModel, object_id=account_id)

        if raise_exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Account not found')

        return account

    async def create_statement(self, statement: AccountStatementModel) -> SQLModel:
        new_statement = await self.add_one(statement)

        return new_statement
