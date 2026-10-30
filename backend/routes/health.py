"""
Health Check Route.
"""

from fastapi import APIRouter
from backend.lifespan import state
from backend.schemas import HealthResponse

router = APIRouter(prefix="/api/health", tags=["System Health"])

@router.get("", response_model=HealthResponse)
async def get_health():
    """Kiểm tra tình trạng sức khỏe của hệ thống backend và tài nguyên máy."""
    return state.get_system_health()
