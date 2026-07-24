from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead
from app.services.audit_service import record_audit_event
from app.services.exceptions import EmailAlreadyExistsError
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get(
    "",
    response_model=list[UserRead],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def list_users(db: Session = Depends(get_db_session)) -> list[User]:
    return UserService(db).list_users()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> User:
    try:
        new_user = UserService(db).create_user(data)
    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    record_audit_event(
        db,
        action="user.created",
        actor=current_user,
        resource_type="user",
        resource_id=new_user.id,
        details={"email": new_user.email, "role": new_user.role.value},
    )
    return new_user
