from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.settings import settings
from routers import account, credit_card, investment, integration, finance

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
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
