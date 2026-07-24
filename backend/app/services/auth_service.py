from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.exceptions import InactiveUserError, InvalidCredentialsError


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User:
        user = self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("E-mail ou senha invalidos")
        if not user.is_active:
            raise InactiveUserError("Usuario inativo")
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
