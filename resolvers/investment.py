import uuid

from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.investment import (
    CreateStatementRequest,
    GetPerformanceRequest,
    GetStatementByIdRequest,
    GetStatementMetadata,
    UpdateStatementRequest,
)
from services.investment import InvestmentService


async def create_statement_resolver(_, info: GraphQLResolveInfo, statement):
    statement_ = CreateStatementRequest.model_validate(statement)

    result = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).create_statement(input_statement=statement_)

    return result.model_dump(by_alias=True)


async def update_statement_resolver(_, info: GraphQLResolveInfo, statement) -> dict:
    statement_ = UpdateStatementRequest.model_validate(statement)

    result = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).update_statement(input_statement=statement_)

    return result


async def get_statement_by_id(_, info: GraphQLResolveInfo, statement_id: uuid.UUID):
    input = GetStatementByIdRequest(statement_id=statement_id)

    statement = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statement_by_id(statement_id=input.statement_id)

    return statement


async def get_investment_performance_resolver(_, info: GraphQLResolveInfo, params):
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

    return metadata.model_dump()


def bind_investment_resovlers(query: QueryType, mutation: MutationType):
    query.set_field(
        "getInvestmentPerformance", resolver=get_investment_performance_resolver
    )
    query.set_field("getStatementMetadata", resolver=get_statement_metadata_resolver)
    query.set_field("getInvestmentStatementById", resolver=get_statement_by_id)

    mutation.set_field("createInvestmentStatement", resolver=create_statement_resolver)
    mutation.set_field("updateInvestmentStatement", resolver=update_statement_resolver)
