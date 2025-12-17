from typing import Any, cast

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
    CreateBalanceResponse,
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

    async def get_accounts(self, params: GetAccountRequest):
        params_ = params.model_dump()
        params_["owner_id"] = self.user["user_id"]

        accounts = await self.account_manager.get_accounts(params=params_)

        response = {"quantity": len(accounts) if accounts else 0, "accounts": accounts}

        return response

    # Transactions
    async def create_transaction(
        self, transaction: CreateAccountTransactionRequest
    ) -> dict[str, Any]:
        account: AccountModel | None = await self.account_manager.get_account_by_id(
            transaction.account_id
        )
        if not account or not account.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not found or not active",
            )

        new_statement = AccountTransactionModel(**transaction.model_dump())

        new_statement.owner_id = self.user["user_id"]
        new_statement.currency = account.currency
        new_statement.period = get_period(new_statement.transaction_date)

        if not new_statement.transaction_currency_id:
            new_statement.transaction_currency = new_statement.currency
            new_statement.transaction_amount = new_statement.amount

        new_statement = await self.account_manager.create_transaction(
            statement=new_statement
        )

        response = {"success": True, "transaction_id": str(new_statement.id)}

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
    ) -> dict[str, Any]:
        transactions = await self.account_manager.get_transactions(
            owner_id=self.user["user_id"],
            start_period=params.start_period,
            end_period=params.end_period,
        )

        response = {
            "quantity": len(transactions) if transactions else 0,
            "transactions": transactions if transactions else [],
        }

        return response

    # Balance
    async def get_balance(self, params: GetBalanceRequest) -> dict[str, Any]:
        balance = await self.account_manager.get_balance_beta(
            account_id=params.account_id, period=params.period
        )

        response = {
            "quantity": len(balance) if balance else 0,
            "account_name": "account.nickname",
            "balance": balance,
        }
        return response
