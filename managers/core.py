from rolf_common.managers import BaseDataManager
from sqlalchemy import RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import CategoryExpenseTypeUserModel, CategoryModel, CountryModel


class CoreManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_categories(self) -> list[RowMapping] | None:
        query = select(
            CategoryModel.id.label("category_id"),
            CategoryModel.name.label("category_name"),
            CategoryModel.description,
            CategoryModel.comment,
            CategoryModel.parent_id,
            CategoryModel.order,
        )

        categories = await self.get_all(query)

        return categories

    async def get_countries(self) -> list[CountryModel] | None:
        query = select(CountryModel)

        countries = await self.get_all(query)

        return [country["CountryModel"] for country in countries] if countries else None

    async def create_category_expense_relation(
        self, relation: CategoryExpenseTypeUserModel
    ):
        pass
