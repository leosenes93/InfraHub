import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_roles
from app.models.audit_log import AuditLog
from app.models.user import UserRole
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogRead

router = APIRouter(
    prefix="/audit-logs", tags=["audit"], dependencies=[Depends(require_roles(UserRole.ADMIN))]
)


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    action: str | None = None,
    resource_type: str | None = None,
    user_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
) -> list[AuditLog]:
    return AuditLogRepository(db).list_filtered(
        action=action, resource_type=resource_type, user_id=user_id, skip=skip, limit=limit
    )
