from src.core.errors import DomainError, PasswordsDoNotMatchError
from src.core.ports.user_repository import UserRepository
from src.core.result import Result
from src.core.user import User


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.user_repo.load_for_auth(username)
        if user is None:
            return None

        if self.user_repo.verify_password(user, password):
            return user

    def register(
        self, username: str, email: str, password: str, password2: str
    ) -> Result[User, DomainError]:
        if password != password2:
            return Result.Err(PasswordsDoNotMatchError())

        return self.user_repo.register(username, email, password)
