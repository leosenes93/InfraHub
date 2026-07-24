from fastapi import APIRouter

from app.api.v1 import assets, attachments, auth, health, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(attachments.router)
