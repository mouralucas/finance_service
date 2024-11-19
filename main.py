import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from rolf_common.backend.nosql_database import NoSqlDatabaseSessionManager
from starlette.middleware.cors import CORSMiddleware

from backend.nosql_database import mongo_session_manager
from backend.settings import settings
from routers import (account, credit_card, core,
                     investment, integration, finance)


# TODO: maybe create a file with all startup functions
async def start_log_database():
    if settings.log_database_url is None and settings.log_database_name is None:
        print('Log database not defined')
        return
    else:
        await mongo_session_manager.initialize()


async def shutdown_log_database():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        await mongo_session_manager.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        start_log_database(),
    )

    try:
        yield
    finally:
        await asyncio.gather(
            shutdown_log_database(),
        )


app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    docs_url="/",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(account.router)
app.include_router(credit_card.router)
app.include_router(investment.router)
app.include_router(integration.router)
app.include_router(finance.router)
app.include_router(core.router)
