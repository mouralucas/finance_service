from sqlalchemy import select
from typing import Any

from rolf_common.managers import BaseDataManager
from rolf_common.models import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create_statement(self, statement: AccountStatementModel) -> SQLModel:
        new_statement = await self.add_one(statement)

        return new_statement
