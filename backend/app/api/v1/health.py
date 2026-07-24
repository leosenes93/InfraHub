import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.redis import get_redis_client
from app.schemas.health import HealthResponse, ReadinessResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
def readiness(db: Session = Depends(get_db_session)) -> ReadinessResponse:
    db_ok = True
    redis_ok = True

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Falha no health check do banco de dados")
        db_ok = False

    try:
        get_redis_client().ping()
    except Exception:
        logger.exception("Falha no health check do Redis")
        redis_ok = False

    overall_status = "ok" if db_ok and redis_ok else "degraded"
    return ReadinessResponse(status=overall_status, database=db_ok, redis=redis_ok)
