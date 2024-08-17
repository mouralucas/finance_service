import datetime

from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from models.account import AccountModel, AccountStatementModel
from schemas.account import AccountSchema, StatementSchema
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateStatementRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse
from schemas.response.account import CreateStatementResponse


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
        new_statement = AccountStatementModel(**statement_entry.model_dump())

        new_statement.owner_id = self.user['user_id']
        new_statement.period = self.get_period(new_statement.transaction_date)

        if not new_statement.transaction_currency_id:
            new_statement.transaction_currency_id = new_statement.currency_id
            new_statement.transaction_amount = new_statement.amount

        new_statement = await AccountManager(session=self.session).create_statement(statement=new_statement)

        response = CreateStatementResponse(
            account_statement_entry=StatementSchema.model_validate(new_statement),
        )

        return response

    @staticmethod
    def get_period(date: datetime.date | datetime.datetime) -> int:
        # if is_date_str:
        #     date = DateTime.str_to_datetime(date, input_format=input_format)
        year = date.year
        month = date.month
        return year * 100 + month
