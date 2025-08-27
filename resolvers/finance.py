from ariadne import MutationType, QueryType

from schemas.request.finance import GetIndexerSeriesRequest
from services.finance import FinanceService


async def resolve_get_indexer_series(_, info, params):
    params = GetIndexerSeriesRequest.model_validate(params)

    indexer_series = await FinanceService(session=info.context['session'],
                                           user=info.context['user'])\
                                            .get_indexer_series(params=params)

    return indexer_series.model_dump()

def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    query.set_field('getIndexerSeries', resolver=resolve_get_indexer_series)
