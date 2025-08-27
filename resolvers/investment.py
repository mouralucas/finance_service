

from ariadne import MutationType, QueryType
from schemas.request.investment import GetInvestmentRequest
from services.investment import InvestmentService


async def get_investments_resolver(_, info, params):
    params_ = GetInvestmentRequest.model_validate(params)

    investments = await InvestmentService(session=info.context['session'], user=info.context['user']).get_investments(params=params_)

    return investments.model_dump(by_alias=True)


def bind_investment_resovlers(query: QueryType, mutation: MutationType):
    query.set_field('getInvestments', resolver=get_investments_resolver)