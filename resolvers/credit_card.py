from ariadne import MutationType, QueryType

from schemas.request.credit_card import GetCreditCardRequest
from services.credit_card import CreditCardService


async def get_credit_cards_resolver(_, info, params):
    params_ = GetCreditCardRequest.model_validate(params)

    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_credit_cards(params=params_)

    return credit_cards.model_dump(by_alias=True)


def bind_credit_card_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCreditCards", resolver=get_credit_cards_resolver)
