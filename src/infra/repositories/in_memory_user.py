from flask_bcrypt import Bcrypt

from src.core.ports.user_repository import UserRepository
from src.core.user import User


class InMemoryUserRepository(UserRepository):
    _current_id = 1

    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt
        self.users: dict[str, User] = {}
        # NOTE: hardcoded admin value
        # pw_hash = self.bcrypt.generate_password_hash("test123").decode()
        # self.users = {
        #     "admin": User(
        #         id=1,
        #         username="admin",
        #         email="admin@admin.com",
        #         pw_hash=pw_hash,
        #     ),
        # }

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

    def register(self, username: str, email: str, password: str) -> User:
        if username in self.users:
            raise ValueError("User already exists")

        pw_hash = self.bcrypt.generate_password_hash(password).decode()
        user = User(
            id=self._current_id,
            username=username,
            email=email,
            pw_hash=pw_hash,
        )
        if self._current_id == 1:
            user.is_admin = True
        self._current_id += 1
        self.users[username] = user
        return user

    def delete(self, username_or_email: str) -> None:
        user = self.find_by_username_or_email(username_or_email)
        if user is None:
            raise ValueError("User not found")

        del self.users[user.username]
