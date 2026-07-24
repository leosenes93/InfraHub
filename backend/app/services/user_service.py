from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.exceptions import EmailAlreadyExistsError


class UserService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repository.list(skip=skip, limit=limit)

    def create_user(self, data: UserCreate) -> User:
        if self.repository.get_by_email(data.email) is not None:
            raise EmailAlreadyExistsError(f"Ja existe um usuario com o e-mail {data.email}")

        user = User(
            email=data.email,
            full_name=data.full_name,
            role=data.role,
            hashed_password=hash_password(data.password),
        )
        return self.repository.add(user)

    def ensure_initial_admin(self, email: str, password: str, full_name: str) -> None:
        if self.repository.count() > 0:
            return

        admin = User(
            email=email,
            full_name=full_name,
            role=UserRole.ADMIN,
            hashed_password=hash_password(password),
        )
        self.repository.add(admin)
