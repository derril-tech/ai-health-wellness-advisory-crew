from fastapi import APIRouter

from app.api.v1.endpoints import health, programs, agents

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
