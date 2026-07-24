from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.auth import LoginRequest, Token
from app.services.auth_service import AuthService
from app.services.exceptions import InactiveUserError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db_session)) -> Token:
    service = AuthService(db)
    try:
        user = service.authenticate(credentials.email, credentials.password)
    except (InvalidCredentialsError, InactiveUserError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return Token(access_token=service.issue_token(user))
