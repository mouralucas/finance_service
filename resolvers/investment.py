from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.investment import (
    CreateStatementRequest,
    GetPerformanceRequest,
    GetStatementMetadata,
)
from services.investment import InvestmentService


async def get_investment_performance_resolver(_, info, params):
    params_ = GetPerformanceRequest.model_validate(params)

    performance = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_performance(params=params_)

    return performance.model_dump(by_alias=True)


async def get_statement_metadata_resolver(_, info: GraphQLResolveInfo, params: dict):
    params_ = GetStatementMetadata.model_validate(params)

    metadata = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statement_metadata(investment_id=params_.investment_id)

    return metadata.model_dump(by_alias=True)


async def create_statement_resolver(_, info, statement):
    statement_ = CreateStatementRequest.model_validate(statement)

    result = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).create_statement(input_statement=statement_)

    return result.model_dump(by_alias=True)


def bind_investment_resovlers(query: QueryType, mutation: MutationType):
    query.set_field(
        "getInvestmentPerformance", resolver=get_investment_performance_resolver
    )
    query.set_field("getStatementMetadata", resolver=get_statement_metadata_resolver)

    mutation.set_field("createInvestmentStatement", resolver=create_statement_resolver)
