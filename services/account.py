import datetime

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from models.account import AccountModel, AccountStatementModel
from schemas.account import AccountSchema, StatementSchema
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateStatementRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse
from schemas.response.account import CreateStatementResponse
from services.utils.datetime import get_period


class AccountService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()

    async def create_account(self, account: CreateAccountRequest) -> CreateAccountResponse:
        new_account = AccountModel(**account.model_dump())
        new_account.owner_id = self.user['user_id']

        new_account = await AccountManager(session=self.session).create_account(account=new_account)

        response = CreateAccountResponse(
            account=AccountSchema.model_validate(new_account),
        )

        return response

    async def get_accounts(self, params: GetAccountRequest) -> GetAccountResponse:
        params = params.model_dump()
        params['owner_id'] = self.user['user_id']

        accounts = await AccountManager(session=self.session).get_accounts(params=params)

        response = GetAccountResponse(
            quantity=len(accounts) if accounts else 0,
            accounts=accounts
        )

        return response

    async def create_statement(self, statement_entry: CreateStatementRequest) -> CreateStatementResponse:
        account = await AccountManager(self.session).get_account_by_id(statement_entry.account_id)
        if not account.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Account is not active')

        new_statement = AccountStatementModel(**statement_entry.model_dump())

        new_statement.owner_id = self.user['user_id']
        new_statement.currency = account.currency
        new_statement.period = get_period(new_statement.transaction_date)

        if not new_statement.transaction_currency_id:
            new_statement.transaction_currency = new_statement.currency
            new_statement.transaction_amount = new_statement.amount

        new_statement = await AccountManager(session=self.session).create_statement(statement=new_statement)

        response = CreateStatementResponse(
            account_statement_entry=StatementSchema.model_validate(new_statement),
        )

        return response
