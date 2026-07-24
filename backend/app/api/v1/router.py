from fastapi import APIRouter

from app.api.v1 import (
    assets,
    attachments,
    audit_logs,
    auth,
    docker,
    health,
    monitoring,
    search,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(attachments.router)
api_router.include_router(docker.router)
api_router.include_router(audit_logs.router)
api_router.include_router(search.router)
api_router.include_router(monitoring.router)
