from ariadne import MutationType, QueryType

from services.core import CoreService


async def get_categories_resolver(_, info):
    categories = await CoreService(
        session=info.context["session"], user=info.context["user"]
    ).get_categories()

    return categories.model_dump(by_alias=True)


def bind_core_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCategories", resolver=get_categories_resolver)
