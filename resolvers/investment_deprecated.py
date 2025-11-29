from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.investment import GetInvestmentRequest, GetStatementsRequest
from services.investment import InvestmentService
from services.investment_deprecated import InvestmentServiceDeprecated


async def get_investments_resolver(_, info: GraphQLResolveInfo, params):
    params_ = GetInvestmentRequest.model_validate(params)

    investments = await InvestmentServiceDeprecated(
        session=info.context["session"], user=info.context["user"]
    ).get_investments(params=params_)

    return investments.model_dump(by_alias=True)


async def get_investment_statements_resolver(_, info: GraphQLResolveInfo, params):
    params_ = GetStatementsRequest.model_validate(params)

    statements = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statement(params=params_)

    return statements.model_dump(by_alias=True)


def bind_investment_deprecated_resovlers(query: QueryType, mutation: MutationType):
    query.set_field("getInvestments", resolver=get_investments_resolver)
    query.set_field(
        "getInvestmentStatements", resolver=get_investment_statements_resolver
    )
