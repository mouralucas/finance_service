from fastapi import APIRouter, Depends, Security
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from schemas.response.core import GetCountryResponse
from services.core import CoreService

router = APIRouter(prefix="/core", tags=["Core"])


@router.get("/country", summary="Get available countries")
async def get_countries(
    session: AsyncSession = Depends(get_session),
    user: RequiredUser = Security(get_user),
) -> GetCountryResponse:
    return await CoreService(session=session, user=user).get_countries()
