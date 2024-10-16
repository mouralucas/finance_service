from fastapi import FastAPI

from backend.settings import settings
from routers import account, credit_card, investment

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    docs_url="/",
    redoc_url="/redoc",
)

# Include all routers
app.include_router(account.router)
app.include_router(credit_card.router)
app.include_router(investment.router)
