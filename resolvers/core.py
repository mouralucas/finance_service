from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from services.core import CoreService


async def get_categories_resolver(_, info: GraphQLResolveInfo):
    categories = await CoreService(
        session=info.context["session"], user=info.context["user"]
    ).get_categories()

    return categories


def bind_core_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCategories", resolver=get_categories_resolver)
