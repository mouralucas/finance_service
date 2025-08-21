from ariadne import MutationType, QueryType


async def resolve_hello_world(_, info):
    print('Opa')
    return "Hello you MF"


def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    query.set_field('getHelloWorld', resolver=resolve_hello_world)
