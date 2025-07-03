from flask_bcrypt import Bcrypt

from src.core.ports.user_repository import UserRepository
from src.core.user import User


class InMemoryUserRepository(UserRepository):
    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt
        # NOTE: hardcoded admin value
        pw_hash = self.bcrypt.generate_password_hash("test123").decode()
        self.users = {
            "admin": User(
                id=1,
                username="admin",
                email="admin@admin.com",
                pw_hash=pw_hash,
            ),
        }

    def find_by_username(self, username: str) -> User | None:
        return self.users.get(username)

    def find_by_username_or_email(self, username_or_email: str) -> User | None:
        for user in self.users.values():
            if (
                user.username == username_or_email
                or user.email == username_or_email
            ):
                return user

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

    def add(self, user: User) -> None:
        if user.username in self.users:
            raise ValueError("User already exists")
        self.users[user.username] = user

    def list_all(self) -> list[User]:
        return list(self.users.values())

    def register(self, username: str, email: str, password: str) -> User:
        if username in self.users:
            raise ValueError("User already exists")

        pw_hash = self.bcrypt.generate_password_hash(password).decode()
        user = User(id=1, username=username, email=email, pw_hash=pw_hash)
        self.users[username] = user
        return user
