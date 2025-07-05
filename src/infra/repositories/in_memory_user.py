from flask_bcrypt import Bcrypt

from src.core.errors import DomainError, UsernameTaken, UserNotFoundError
from src.core.ports.user_repository import UserRepository
from src.core.result import Result
from src.core.user import User


class InMemoryUserRepository(UserRepository):
    _current_id = 1

    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt
        self.users: dict[str, User] = {}

    def find_by_username(self, username: str) -> User | None:
        result = self.users.get(username)
        if result is None:
            return None

        return User(
            id=result.id,
            username=result.username,
            email=result.email,
            pw_hash=None,
        )

    def find_by_username_or_email(self, username_or_email: str) -> User | None:
        for user in self.users.values():
            if (
                user.username == username_or_email
                or user.email == username_or_email
            ):
                return User(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    pw_hash=None,
                )

    def load_for_auth(self, username_or_email: str) -> User | None:
        for user in self.users.values():
            if (
                user.username == username_or_email
                or user.email == username_or_email
            ):
                return user

    def verify_password(self, user: User, password: str) -> bool:
        return self.bcrypt.check_password_hash(user.pw_hash, password)

    def get_by_id(self, user_id: int) -> User | None:
        for user in self.users.values():
            if user.id == user_id:
                return user

    def list_all(self) -> list[User]:
        return list(self.users.values())

    def register(
        self, username: str, email: str, password: str
    ) -> Result[User, DomainError]:
        if username in self.users:
            return Result.Err(UsernameTaken(username))

        pw_hash = self.bcrypt.generate_password_hash(password).decode()
        user_result = User.create(
            id=self._current_id,
            username=username,
            email=email,
            pw_hash=pw_hash,
        )
        if user_result.is_err:
            return user_result

        user = user_result.unwrap()
        if self._current_id == 1:
            user.is_admin = True
        self._current_id += 1
        self.users[username] = user
        return Result.Ok(user)

    def delete(self, username_or_email: str) -> None | DomainError:
        user = self.find_by_username_or_email(username_or_email)
        if user is None:
            return UserNotFoundError(username_or_email)

        del self.users[user.username]
