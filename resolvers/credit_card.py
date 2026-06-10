from ariadne import MutationType, QueryType
from graphql import GraphQLResolveInfo
from rolf_common.util.graphql_input_validation import validate_graphql_input

from schemas.request.credit_card import (
    CreateCreditCardTransactionRequest,
    GetCreditCardRequest,
    GetCreditCardTransactionsRequest,
    GetInstallmentsDueDatesRequest,
)
from services.credit_card import CreditCardService


# Credit Card Resolvers
@validate_graphql_input(GetCreditCardRequest)
async def get_credit_cards_resolver(
    _, info: GraphQLResolveInfo, params: GetCreditCardRequest
):
    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_credit_cards(params=params)

    return credit_cards


@validate_graphql_input(CreateCreditCardTransactionRequest)
async def create_credit_card_transaction_resolver(
    _, info: GraphQLResolveInfo, transaction: CreateCreditCardTransactionRequest
):
    new_transaction = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).create_transaction(transaction)

    return new_transaction


@validate_graphql_input(GetCreditCardTransactionsRequest)
async def get_credit_card_transaction_resolver(
    _, info: GraphQLResolveInfo, params: GetCreditCardTransactionsRequest
):
    return await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_transactions(params)


# Helper to get credit card installment due dates
@validate_graphql_input(GetInstallmentsDueDatesRequest)
async def get_installments_due_dates_resolver(
    _, info: GraphQLResolveInfo, params: GetInstallmentsDueDatesRequest
):
    credit_cards = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_installments_due_date(params=params)

    return credit_cards


async def get_credit_card_transaction_metadata_by_id(
    _, info: GraphQLResolveInfo, id: int
):
    transaction = await CreditCardService(
        session=info.context["session"], user=info.context["user"]
    ).get_transaction_metadata_by_id(id=id)

    return transaction


def bind_credit_card_resolvers(query: QueryType, mutation: MutationType):
    query.set_field("getCreditCards", resolver=get_credit_cards_resolver)
    query.set_field(
        "getCreditCardTransactions", resolver=get_credit_card_transaction_resolver
    )
    query.set_field(
        "getCreditCardInstallmentDueDates", resolver=get_installments_due_dates_resolver
    )

    query.set_field(
        "getCreditCardTransactionMetadataById",
        resolver=get_credit_card_transaction_metadata_by_id,
    )

    mutation.set_field(
        "createCreditCardTransaction",
        resolver=create_credit_card_transaction_resolver,
    )
