
from ariadne import MutationType, QueryType
from schemas.request.investment import GetPerformanceRequest
from services.investment import InvestmentService


async def get_investment_performance_resolver(_, info, params):
    params_ = GetPerformanceRequest.model_validate(params)
    
    performance = await InvestmentService(session=info.context["session"], user=info.context["user"]).get_performance(
        params=params_
    )
    
    return performance.model_dump(by_alias=True)


def bind_investment_resovlers(query: QueryType, mutation: MutationType):
    query.set_field("getInvestmentPerformance", resolver=get_investment_performance_resolver)
