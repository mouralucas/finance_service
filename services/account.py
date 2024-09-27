from typing import cast

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import select, func, delete, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from managers.credit_card import CreditCardManager
from models.account import AccountModel, AccountStatementModel, AccountBalanceModel
from models.credit_card import CreditCardModel
from schemas.account import AccountSchema, StatementSchema
from schemas.request.account import CreateAccountRequest, GetAccountRequest, CreateStatementRequest, CloseAccountRequest, CreateBalanceRequest
from schemas.response.account import CreateAccountResponse, GetAccountResponse, CloseAccountResponse, CreateBalanceResponse
from schemas.response.account import CreateStatementResponse
from services.utils.datetime import get_period, get_current_period, get_period_sequence


class AccountService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()
        self.account_manager = AccountManager(session=self.session)

    # Account
    async def create_account(self, account: CreateAccountRequest) -> CreateAccountResponse:
        new_account = AccountModel(**account.model_dump())
        new_account.owner_id = self.user['user_id']

        new_account = await self.account_manager.create_account(account=new_account)

        response = CreateAccountResponse(
            account=AccountSchema.model_validate(new_account),
        )

        return response

    async def close_account(self, account: CloseAccountRequest) -> CloseAccountResponse:
        current_account = await self.account_manager.get_account_by_id(account.id)
        if not current_account or not current_account.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Account not found or already closed')

        fields = account.model_dump()
        fields['active'] = False

        closed_account = await self.account_manager.update_account(current_account, fields)

        for credit_card in current_account.credit_cards:
            credit_card_fields = {
                'id': credit_card.id,
                'cancellation_date': account.close_date,
                'active': False
            }
            await CreditCardManager(session=self.session).update_credit_card(cast(CreditCardModel, credit_card), credit_card_fields)

        # Refresh account object with the cancelled credit cards
        await self.session.refresh(closed_account)

        response = CloseAccountResponse(
            account=AccountSchema.model_validate(closed_account),
        )

        return response

    async def get_accounts(self, params: GetAccountRequest) -> GetAccountResponse:
        params = params.model_dump()
        params['owner_id'] = self.user['user_id']

        accounts: list[RowMapping] = await self.account_manager.get_accounts(params=params)

        response = GetAccountResponse(
            quantity=len(accounts) if accounts else 0,
            accounts=[AccountSchema.model_validate(data["AccountModel"]) for data in accounts]
        )

        return response

    # Statement
    async def create_statement(self, statement_entry: CreateStatementRequest) -> CreateStatementResponse:
        account = await self.account_manager.get_account_by_id(statement_entry.account_id)
        if not account.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Account is not active')

        new_statement = AccountStatementModel(**statement_entry.model_dump())

        new_statement.owner_id = self.user['user_id']
        new_statement.currency = account.currency
        new_statement.period = get_period(new_statement.transaction_date)

        if not new_statement.transaction_currency_id:
            new_statement.transaction_currency = new_statement.currency
            new_statement.transaction_amount = new_statement.amount

        new_statement = await self.account_manager.create_statement(statement=new_statement)

        response = CreateStatementResponse(
            account_statement_entry=StatementSchema.model_validate(new_statement),
        )

        return response

    # Balance
    async def create_balance(self, params: CreateBalanceRequest):
        account: AccountModel = await self.account_manager.get_account_by_id(params.account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Account not exists')

        # Get balance from the last period with registered transactions until the account is closed or current period
        min_period: int = await self.account_manager.get_only_one(select(func.min(AccountStatementModel.period)).where(AccountStatementModel.account_id == params.account_id))
        max_period: int = get_period(account.close_date) if account.close_date else get_current_period()

        # Get all periods between min and max periods so even without transactions all periods in this range have its own balance
        period_range: list[int] = get_period_sequence(min_period, max_period)

        # Fetch all transactions grouped by period
        transactions_by_period = await self.account_manager.get_consolidated_transactions_by_period(account_id=params.account_id, period_range=period_range)

        # The firs balance available always start with 'previous_balance' at zero, even if in actual account have more transactions
        # The user should add the previous amount as a transaction, so the calculation is correct at the end
        previous_balance = 0.0

        # Remove previous balance data for the account
        await self.session.execute(delete(AccountBalanceModel).where(AccountBalanceModel.account_id == params.account_id))
        await self.session.flush()

        balance_entries = []
        for period_data in transactions_by_period:

            period = period_data.period
            earnings = period_data.earnings
            incoming = period_data.incoming - earnings
            outgoing = period_data.outgoing
            transactions = incoming - abs(outgoing)
            balance = previous_balance + transactions + earnings

            account_balance = AccountBalanceModel(
                account_id=params.account_id,
                period=period,
                previous_balance=previous_balance,
                incoming=incoming,
                outgoing=abs(outgoing),
                transactions=transactions,
                earnings=earnings,
                balance=balance
            )

            balance_entries.append(account_balance)
            # Update the previous balance with the current balance
            previous_balance = balance

        self.session.add_all(balance_entries)

        response = CreateBalanceResponse(
            accountNickname=account.nickname,
            periods_saved=len(balance_entries),
        )

        return response