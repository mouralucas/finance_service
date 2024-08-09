from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.account import AccountManager
from models.account import AccountModel
from schemas.account import AccountSchema
from schemas.request.account import CreateAccountRequest
from schemas.response.account import CreateAccountResponse


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
