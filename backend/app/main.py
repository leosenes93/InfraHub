import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.services.user_service import UserService

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    db = SessionLocal()
    try:
        UserService(db).ensure_initial_admin(
            email=settings.initial_admin_email,
            password=settings.initial_admin_password,
            full_name=settings.initial_admin_full_name,
        )
        logger.info("startup_complete", extra={"environment": settings.environment})
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.project_name,
    description="API central de inventario, documentacao e monitoramento de infraestrutura de TI.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router, prefix=settings.api_v1_prefix)

# Exposto apenas na rede interna do Docker (Nginx nao faz proxy de /metrics) -
# somente o Prometheus alcanca este endpoint.
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
