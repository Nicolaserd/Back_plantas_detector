# app/api/health_routes.py
from fastapi import APIRouter
from app.core import config

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "mode": "realtime-only"
    }
