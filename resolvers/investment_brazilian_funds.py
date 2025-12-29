from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo
from rolf_common.util.graphql_input_validation import validate_graphql_input

from schemas.request.investment import GetBrazilianFundInvestmentsRequest
from services.investment_brazilian_fund import InvestmentBrazilianFundService


@validate_graphql_input(GetBrazilianFundInvestmentsRequest)
async def get_investments_brazilian_funds(
    _, info: GraphQLResolveInfo, params: GetBrazilianFundInvestmentsRequest
):
    investments = await InvestmentBrazilianFundService(
        session=info.context["session"], user=info.context["user"]
    ).get_brazilian_fund_investments(params=params)

    return investments if investments else []


def bind_investment_brazilian_funds_resolvers(query: QueryType, mutation: MutationType):
    query.set_field(
        "getInvestmentsBrazilianFunds", resolver=get_investments_brazilian_funds
    )
