from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from schemas.request.finance import GetSummaryRequest


class FinanceService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)

        self.account_manager = AccountManager(self.session)
        self.user = user.model_dump()

    async def get_summary(self, params: GetSummaryRequest):
        balance = await self.account_manager.get_balance(current_period=True)

        print(balance)