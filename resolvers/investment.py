from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo
from rolf_common.util.graphql_input_validation import validate_graphql_input

from schemas.request.investment import (
    CreateStatementRequest,
    GetInvestmentRequest,
    GetObjectiveRequest,
    GetPerformanceRequest,
    GetStatementByIdRequest,
    GetStatementMetadata,
    GetStatementsRequest,
    UpdateStatementRequest,
)
from services.investment import InvestmentService
from services.investment_deprecated import InvestmentServiceDeprecated


# Investment resolvers
@validate_graphql_input(GetInvestmentRequest)
async def get_investments_resolver(
    _, info: GraphQLResolveInfo, params: GetInvestmentRequest
):
    investments = await InvestmentServiceDeprecated(
        session=info.context["session"], user=info.context["user"]
    ).get_investments(params=params)

    return investments


# Statement resolvers
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


@validate_graphql_input(GetStatementsRequest)
async def get_investment_statements_resolver(
    _, info: GraphQLResolveInfo, params: GetStatementsRequest
):
    statements = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statements(params=params)

    return statements


@validate_graphql_input(GetStatementByIdRequest)
async def get_statement(_, info: GraphQLResolveInfo, params: GetStatementByIdRequest):
    statement = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statement(id=params.id)

    return statement


async def get_statement_metadata_resolver(_, info: GraphQLResolveInfo, params: dict):
    params_ = GetStatementMetadata.model_validate(params)

    metadata = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_statement_metadata(investment_id=params_.investment_id)

    return metadata


# Outro resolvers
@validate_graphql_input(GetPerformanceRequest)
async def get_investment_performance_resolver(
    _, info: GraphQLResolveInfo, params: GetPerformanceRequest
):
    performance = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_performance(params=params)

    return performance


@validate_graphql_input(GetObjectiveRequest)
async def get_investment_objectives(
    _, info: GraphQLResolveInfo, params: GetObjectiveRequest
):
    objectives = await InvestmentService(
        session=info.context["session"], user=info.context["user"]
    ).get_objectives(params=params)

    return objectives if objectives else []


def bind_investment_resovlers(query: QueryType, mutation: MutationType):
    query.set_field("getInvestments", resolver=get_investments_resolver)
    query.set_field(
        "getInvestmentPerformance", resolver=get_investment_performance_resolver
    )
    query.set_field("getStatementMetadata", resolver=get_statement_metadata_resolver)
    query.set_field(
        "getInvestmentStatements", resolver=get_investment_statements_resolver
    )
    query.set_field("getInvestmentStatement", resolver=get_statement)
    query.set_field("getInvestmentObjectives", resolver=get_investment_objectives)

    mutation.set_field("createInvestmentStatement", resolver=create_statement_resolver)
    mutation.set_field("updateInvestmentStatement", resolver=update_statement_resolver)
