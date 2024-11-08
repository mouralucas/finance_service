from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.core import CoreManager
from schemas.core import CategorySchema, CurrencySchema
from schemas.response.core import GetCategoryResponse


class CoreService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.core_manager = CoreManager(session=self.session)

    async def get_categories(self):
        categories = await self.core_manager.get_categories()

        response = GetCategoryResponse(
            categories=[CategorySchema.model_validate(category) for category in categories],
        )

        return response
