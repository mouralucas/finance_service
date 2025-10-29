from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.investment import GetBrazilianFundInvestmentsRequest
from services.investment_brazilian_fund import InvestmentBrazilianFundService


async def get_investments_brazilian_funds(_, info: GraphQLResolveInfo, params):
    params_ = GetBrazilianFundInvestmentsRequest.model_validate(params)

    investments = await InvestmentBrazilianFundService(
        session=info.context["session"], user=info.context["user"]
    ).get_brazilian_fund_investments(params=params_)

    return investments.model_dump(by_alias=True)


def bind_investment_brazilian_funds_resolvers(query: QueryType, mutation: MutationType):
    query.set_field(
        "getInvestmentsBrazilianFunds", resolver=get_investments_brazilian_funds
    )
