from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_client_ip, get_db_session
from app.schemas.auth import LoginRequest, Token
from app.services.audit_service import record_audit_event
from app.services.auth_service import AuthService
from app.services.exceptions import InactiveUserError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest, request: Request, db: Session = Depends(get_db_session)
) -> Token:
    service = AuthService(db)
    ip_address = get_client_ip(request)
    try:
        user = service.authenticate(credentials.email, credentials.password)
    except (InvalidCredentialsError, InactiveUserError) as exc:
        record_audit_event(
            db,
            action="auth.login_failed",
            actor_email=credentials.email,
            ip_address=ip_address,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    record_audit_event(db, action="auth.login_succeeded", actor=user, ip_address=ip_address)
    return Token(access_token=service.issue_token(user))
