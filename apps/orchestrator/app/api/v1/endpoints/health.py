from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "version": "1.0.0"
    }
