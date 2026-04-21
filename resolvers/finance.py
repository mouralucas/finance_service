import uuid

from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo
from rolf_common.util.graphql_input_validation import validate_graphql_input

from schemas.request.finance import GetIndexerSeriesRequest
from schemas.request.integration import SyncIndexerSeriesRequest
from services.finance import FinanceService
from services.integration import BcbIntegrationService


@validate_graphql_input(GetIndexerSeriesRequest)
async def get_indexer_series_resolver(
    _, info: GraphQLResolveInfo, params: GetIndexerSeriesRequest
):
    indexer_series = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_indexer_series(params=params)

    return indexer_series


@validate_graphql_input(SyncIndexerSeriesRequest)
async def sync_indexer_series_resolver(
    _, info: GraphQLResolveInfo, params: SyncIndexerSeriesRequest
):
    indexer_series = await BcbIntegrationService(
        session=info.context["session"]
    ).sync_monthly_data(indexer_id=uuid.UUID("2a2b100f-17d9-4c61-b3b4-f06662113953"))

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

async def get_finance_summary_resolver(_, info: GraphQLResolveInfo):
    finance_summary = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_finance_summary()
    
    return finance_summary

def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    # Queries
    query.set_field("getIndexerSeries", resolver=get_indexer_series_resolver)
    query.set_field("getCurrencies", resolver=get_currencies_resolver)
    query.set_field("getPeriodicity", resolver=get_periodicity_resolver)
    query.set_field("getFinanceSummary", resolver=get_finance_summary_resolver)

    # Mutations
    mutation.set_field("syncIndexerSeries", resolver=sync_indexer_series_resolver)
