from ariadne import MutationType, QueryType

from schemas.request.finance import GetIndexerSeriesRequest
from services.finance import FinanceService


async def get_indexer_series_resolver(_, info, params):
    params = GetIndexerSeriesRequest.model_validate(params)

    indexer_series = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_indexer_series(params=params)

    return indexer_series.model_dump(by_alias=True)


async def get_currencies_resolver(_, info):
    currencies = await FinanceService(
        session=info.context["session"], user=info.context["user"]
    ).get_currencies()

    return currencies.model_dump(by_alias=True)


def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getIndexerSeries", resolver=get_indexer_series_resolver)
    query.set_field("getCurrencies", resolver=get_currencies_resolver)
