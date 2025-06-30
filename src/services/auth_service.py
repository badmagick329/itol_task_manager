from src.core.user import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str):
        user = self.user_repo.find_by_username(username)
        if user is None:
            return None

        if self.user_repo.verify_password(user, password):
            return user
