from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.credit_card import (
    GetCreditCardRequest,
    GetInstallmentsDueDatesRequest,
)
from services.credit_card import CreditCardService
from utils.graphql_input_validation import validate_graphql_input


# Credit Card Resolvers
@validate_graphql_input(GetCreditCardRequest)
async def get_credit_cards_resolver(
    _, info: GraphQLResolveInfo, params: GetCreditCardRequest
):
    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_credit_cards(params=params)

    return credit_cards


# Helper to get credit card installment due dates
@validate_graphql_input(GetInstallmentsDueDatesRequest)
async def get_installments_due_dates_resolver(
    _, info: GraphQLResolveInfo, params: GetInstallmentsDueDatesRequest
):
    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_installments_due_date(params=params)

    return credit_cards


def bind_credit_card_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCreditCards", resolver=get_credit_cards_resolver)
    query.set_field(
        "getCreditCardInstallmentDueDates", resolver=get_installments_due_dates_resolver
    )
