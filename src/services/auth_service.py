from src.core.ports.user_repository import UserRepository
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
    ):
        user = self.user_repo.find_by_username_or_email(username)
        if password != password2:
            raise ValueError("Passwords do not match")

        return self.user_repo.register(username, email, password)
