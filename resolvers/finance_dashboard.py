from ariadne import QueryType, MutationType

async def resolve_hello_world(_, info):
    return "Hello you MF"


def bind_finance_dashboard_resolvers(query: QueryType, mutation: MutationType):
    query.set_field('helloWorld', resolver=resolve_hello_world)
