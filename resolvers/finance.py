from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo
from rolf_common.util.graphql_input_validation import validate_graphql_input

from schemas.request.finance import GetIndexerSeriesRequest
from services.finance import FinanceService


@validate_graphql_input(GetIndexerSeriesRequest)
async def get_indexer_series_resolver(
    _, info: GraphQLResolveInfo, params: GetIndexerSeriesRequest
):
    indexer_series = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_indexer_series(params=params)

    return indexer_series


async def get_periodicity_resolver(_, info: GraphQLResolveInfo):
    periodicity = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_periodicity()

    return periodicity


async def get_currencies_resolver(_, info: GraphQLResolveInfo):
    currencies = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_currencies()

    return currencies


def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getIndexerSeries", resolver=get_indexer_series_resolver)
    query.set_field("getCurrencies", resolver=get_currencies_resolver)
    query.set_field("getPeriodicity", resolver=get_periodicity_resolver)
