from fastapi import APIRouter, Request

from app.core.config import settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=request.app.state.provider.provider_name,
        version=settings.APP_VERSION,
    )
