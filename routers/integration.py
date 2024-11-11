from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from schemas.request.integration import CreateIndexerSeriesRequest
from services.integration import BcbIntegrationService

router = APIRouter(prefix="/integration", tags=['Integrations'])


@router.post('/indexer/series')
async def update_index_series(
        params: CreateIndexerSeriesRequest,
        session: AsyncSession = Depends(get_session)
):
    await BcbIntegrationService(session=session).get_indexer(params=params)
