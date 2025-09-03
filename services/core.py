from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import BaseService
from sqlalchemy.ext.asyncio import AsyncSession

from managers.core import CoreManager
from schemas.core import CategorySchema, CountrySchema
from schemas.response.core import GetCategoryResponse, GetCountryResponse


class CoreService(BaseService):
    def __init__(self, session: AsyncSession, user: RequiredUser):
        super().__init__(session=session)
        self.user = user.model_dump()
        self.core_manager = CoreManager(session=self.session)

    async def get_categories(self) -> GetCategoryResponse:
        categories = await self.core_manager.get_categories()

        response = GetCategoryResponse(
            quantity=len(categories) if categories else 0,
            categories=(
                [CategorySchema.model_validate(category) for category in categories]
                if categories
                else []
            ),
        )

        return response

    async def get_countries(self) -> GetCountryResponse:
        countries = await self.core_manager.get_countries()

        response = GetCountryResponse(
            quantity=len(countries) if countries else 0,
            countries=(
                [CountrySchema.model_validate(country) for country in countries]
                if countries
                else []
            ),
        )

        return response

    async def create_category_expense_relation(self, relation):
        pass
