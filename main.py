import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from rolf_common.base_middleware import LogsMiddleware
from starlette.middleware.cors import CORSMiddleware

from backend.settings import settings
from lifespan import start_log_service, shutdown_log_service
from routers import (account, credit_card, core,
                     investment, integration, finance)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        start_log_service(),
    )

    try:
        yield
    finally:
        await asyncio.gather(
            shutdown_log_service(),
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
app.add_middleware(LogsMiddleware)


# Include all routers
app.include_router(account.router)
app.include_router(credit_card.router)
app.include_router(investment.router)
app.include_router(integration.router)
app.include_router(finance.router)
app.include_router(core.router)
