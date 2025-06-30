from flask_bcrypt import Bcrypt

from src.core.user import User, UserRepository


class InMemoryUser(UserRepository):
    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt
        # NOTE: hardcoded for now
        pw_hash = bcrypt.generate_password_hash("test123").decode()
        self.users = {
            "admin": User(id=1, username="admin", pw_hash=pw_hash),
        }

    def find_by_username(self, username: str) -> User | None:
        return self.users.get(username)

    def verify_password(self, user: User, password: str) -> bool:
        return self.bcrypt.check_password_hash(user.pw_hash, password)
