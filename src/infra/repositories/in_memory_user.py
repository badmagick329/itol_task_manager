from flask_bcrypt import Bcrypt

from src.core.ports.user_repository import UserRepository
from src.core.user import User


class InMemoryUserRepository(UserRepository):
    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt
        # NOTE: hardcoded admin value
        pw_hash = bcrypt.generate_password_hash("test123").decode()
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
