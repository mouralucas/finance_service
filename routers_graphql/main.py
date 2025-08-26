import uuid
from ariadne import MutationType, QueryType, graphql, load_schema_from_path, make_executable_schema
from ariadne.explorer import ExplorerGraphiQL
from fastapi import APIRouter, Depends, Request, Security
from sqlalchemy.ext.asyncio import AsyncSession
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from starlette.responses import HTMLResponse, JSONResponse

from backend.database import get_session
from resolvers.account import bind_account_resolvers
from resolvers.finance import bind_finance_dashboard_resolvers

router = APIRouter(tags=["GraphQL"], prefix='/graphql')

type_defs = (
    load_schema_from_path("schemas_graphql/schema.graphql") +
    load_schema_from_path("schemas_graphql/account.graphql") +
    load_schema_from_path("schemas_graphql/finance.graphql")
)

query = QueryType()
mutation = MutationType()

bind_finance_dashboard_resolvers(query, mutation)
bind_account_resolvers(query, mutation)

schema = make_executable_schema(type_defs, query, mutation)

@router.post('', description='The graphql endpoint')
async def finance_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_session),
    #user: RequiredUser = Security(get_user)
):
    user = RequiredUser(user_id=uuid.uuid4())

    data = await request.json()
    value = {"request": request, "session": session, "user": user}
    success, result = await graphql(schema, data, context_value=value, debug=True)

    status_code = 200 if success else 400
    return JSONResponse(result, status_code=status_code)

playground_html = ExplorerGraphiQL().html(None)

@router.get('', description='The GraphQL playground page')
async def graphql_playground():
    # TODO: edit to render GraphiQL playground
    return HTMLResponse(playground_html)
