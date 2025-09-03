from typing import cast

from fastapi import HTTPException
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from managers.account import AccountManager
from managers.credit_card import CreditCardManager
from models.account import AccountBalanceModel, AccountModel, AccountTransactionModel
from models.credit_card import CreditCardModel
from schemas.account import (
    AccountBalanceSchema,
    AccountSchema,
    AccountTransactionSchema,
)
from schemas.request.account import (
    CloseAccountRequest,
    CreateAccountRequest,
    CreateAccountTransactionRequest,
    CreateBalanceRequest,
    GetAccountRequest,
    GetAccountTransactionRequest,
    GetBalanceRequest,
    UpdateAccountTransactionRequest,
)
from schemas.response.account import (
    CloseAccountResponse,
    CreateAccountResponse,
    CreateAccountTransactionResponse,
    CreateBalanceResponse,
    GetAccountResponse,
    GetAccountTransactionResponse,
    GetBalanceResponse,
    UpdateTransactionResponse,
)
from services.utils.datetime import get_current_period, get_period, get_period_range


class AccountService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session)
        self.user = user.model_dump()
        self.account_manager = AccountManager(session=self.session)

    # Account
    async def create_account(
        self, account: CreateAccountRequest
    ) -> CreateAccountResponse:
        new_account = AccountModel(**account.model_dump())
        new_account.owner_id = self.user["user_id"]

        new_account = await self.account_manager.create_account(account=new_account)

        response = CreateAccountResponse(
            account=AccountSchema.model_validate(new_account),
        )

        return response

    async def close_account(self, account: CloseAccountRequest) -> CloseAccountResponse:
        current_account = await self.account_manager.get_account_by_id(account.id)
        if not current_account or not current_account.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or already closed",
            )

        fields = account.model_dump()
        fields["active"] = False

        closed_account = await self.account_manager.update_account(
            current_account, fields
        )

        for credit_card in current_account.credit_cards:
            credit_card_fields = {
                "id": credit_card.id,
                "cancellation_date": account.close_date,
                "active": False,
            }
            await CreditCardManager(session=self.session).update_credit_card(
                cast(CreditCardModel, credit_card), credit_card_fields
            )

        response = CloseAccountResponse(
            account=AccountSchema.model_validate(closed_account),
        )

        return response

    async def get_accounts(self, params: GetAccountRequest) -> GetAccountResponse:
        params_ = params.model_dump()
        params_["owner_id"] = self.user["user_id"]

        accounts: list[AccountModel] | None = await self.account_manager.get_accounts(
            params=params_
        )

        response = GetAccountResponse(
            quantity=len(accounts) if accounts else 0,
            accounts=(
                [AccountSchema.model_validate(data) for data in accounts]
                if accounts
                else []
            ),
        )

        return response

    # Transactions
    async def create_transaction(
        self, statement_entry: CreateAccountTransactionRequest
    ) -> CreateAccountTransactionResponse:
        account = await self.account_manager.get_account_by_id(
            statement_entry.account_id
        )
        if not account.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active"
            )

        new_statement = AccountTransactionModel(**statement_entry.model_dump())

        new_statement.owner_id = self.user["user_id"]
        new_statement.currency = account.currency
        new_statement.period = get_period(new_statement.transaction_date)

        if not new_statement.transaction_currency_id:
            new_statement.transaction_currency = new_statement.currency
            new_statement.transaction_amount = new_statement.amount

        new_statement = await self.account_manager.create_transaction(
            statement=new_statement
        )

        response = CreateAccountTransactionResponse(
            transaction=AccountTransactionSchema.model_validate(new_statement),
        )

        return response

    async def update_transaction(
        self, transaction: UpdateAccountTransactionRequest
    ) -> UpdateTransactionResponse:
        changed_fields = transaction.model_dump(exclude_unset=True)
        if "transaction_date" in changed_fields:
            period = get_period(changed_fields["transaction_date"])
            changed_fields["period"] = period

        updated_transaction = await self.account_manager.update_transaction(
            transaction_id=transaction.id, fields=changed_fields
        )

        response = UpdateTransactionResponse(
            transaction=AccountTransactionSchema.model_validate(updated_transaction)
        )

        return response

    async def get_transactions(
        self, params: GetAccountTransactionRequest
    ) -> GetAccountTransactionResponse:
        transactions = await self.account_manager.get_transactions(
            owner_id=self.user["user_id"],
            start_period=params.start_period,
            end_period=params.end_period,
        )

        response = GetAccountTransactionResponse(
            quantity=len(transactions) if transactions else 0,
            transactions=(
                [
                    AccountTransactionSchema(**transaction)
                    for transaction in transactions
                ]
                if transactions
                else []
            ),
        )

        return response

    # Balance
    async def create_balance(self, params: CreateBalanceRequest):
        account: AccountModel = await self.account_manager.get_account_by_id(
            params.account_id
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not exists"
            )

        # Get balance from the last period with registered transactions until the
        #   account is closed or current period
        min_period: int = await self.account_manager.get_only_one(
            select(func.min(AccountTransactionModel.period)).where(
                AccountTransactionModel.account_id == params.account_id
            )
        )
        max_period: int = (
            get_period(account.close_date)
            if account.close_date
            else get_current_period()
        )

        # TODO: create better validation
        if not min_period:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provavelmente não existem transações nessa conta",
            )

        # Get all periods between min and max periods, so even without transactions,
        #   all periods in this range have its own balance
        period_range: list[int] = get_period_range(min_period, max_period)

        # Fetch all transactions grouped by period
        transactions_by_period = (
            await self.account_manager.get_consolidated_transactions_by_period(
                account_id=params.account_id, period_range=period_range
            )
        )

        # The first balance available always starts with 'previous_balance' at zero,
        #   even if in actual account have more transactions
        # The user should add the previous amount as a transaction, so the
        #   calculation is correct at the end
        previous_balance = 0.0

        balance_entries = []
        for period_data in transactions_by_period:
            period = period_data.period
            earnings = period_data.earnings
            incoming = period_data.incoming - earnings
            outgoing = period_data.outgoing
            transactions = incoming - abs(outgoing)
            balance = previous_balance + float(transactions) + float(earnings)

            account_balance = AccountBalanceModel(
                account_id=params.account_id,
                period=period,
                previous_balance=previous_balance,
                incoming=incoming,
                outgoing=abs(outgoing),
                transactions=transactions,
                earnings=earnings,
                balance=balance,
            )

            balance_entries.append(account_balance)
            # Update the previous balance with the current balance
            previous_balance = balance

        # Remove previous balance data for the account
        await self.account_manager.delete_balance(account_id=params.account_id)

        # Add the calculated balance for the account
        self.session.add_all(balance_entries)

        response = CreateBalanceResponse(
            account_nickname=account.nickname,
            periods_saved=len(balance_entries),
        )

        return response

    async def get_balance(self, params: GetBalanceRequest) -> GetBalanceResponse:
        balance = await self.account_manager.get_balance_beta(
            account_id=params.account_id, period=params.period
        )

        response = GetBalanceResponse(
            account_name="account.nickname",
            quantity=len(balance) if balance else 0,
            balance=(
                [AccountBalanceSchema.model_validate(data) for data in balance]
                if balance
                else []
            ),
        )
        return response
