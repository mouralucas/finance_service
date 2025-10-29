from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo

from schemas.request.credit_card import (
    GetCreditCardRequest,
    GetInstallmentsDueDatesRequest,
)
from services.credit_card import CreditCardService


async def get_credit_cards_resolver(_, info: GraphQLResolveInfo, params):
    params_ = GetCreditCardRequest.model_validate(params)

    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_credit_cards(params=params_)

    return credit_cards.model_dump(by_alias=True)


async def get_installments_due_dates_resolver(_, info: GraphQLResolveInfo, params):
    params_ = GetInstallmentsDueDatesRequest.model_validate(params)

    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_installments_due_date(params=params_)

    return credit_cards.model_dump(by_alias=True)


def bind_credit_card_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCreditCards", resolver=get_credit_cards_resolver)
    query.set_field(
        "getCreditCardInstallmentDueDates", resolver=get_installments_due_dates_resolver
    )
