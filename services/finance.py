from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from managers.finance import FinanceManager
from schemas.core import CurrencySchema
from schemas.request.finance import GetSummaryRequest
from schemas.response.finance import GetCurrencyResponse


class FinanceService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)

        self.account_manager = AccountManager(self.session)
        self.finance_manager = FinanceManager(self.session)
        self.user = user.model_dump()

    async def get_summary(self, params: GetSummaryRequest):
        balance = await self.account_manager.get_balance(current_period=True)

        print(balance)

    async def get_currencies(self):
        currencies = await self.finance_manager.get_currencies()

        response = GetCurrencyResponse(
            currencies=[CurrencySchema.model_validate(currency) for currency in currencies],
        )

        return response