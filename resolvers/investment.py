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
from utils.graphql_input_validation import validate_graphql_input


@validate_graphql_input(CreateStatementRequest)
async def create_statement_resolver(
    _, info: GraphQLResolveInfo, statement: CreateStatementRequest
):
    result = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).create_statement(input_statement=statement)

    return result


@validate_graphql_input(UpdateStatementRequest)
async def update_statement_resolver(
    _, info: GraphQLResolveInfo, statement: UpdateStatementRequest
) -> dict:
    result = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).update_statement(input_statement=statement)

    return result


@validate_graphql_input(GetStatementByIdRequest)
async def get_statement_by_id(
    _, info: GraphQLResolveInfo, input: GetStatementByIdRequest
):
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
