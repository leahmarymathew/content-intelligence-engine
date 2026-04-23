from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness endpoint for service health checks."""

    return {"status": "backend running"}