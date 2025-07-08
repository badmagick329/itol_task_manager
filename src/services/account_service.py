from typing import Union

from src.core.errors import (
    ApplicationError,
    InvalidCredentialsError,
    PasswordsDoNotMatchError,
)
from src.core.ports.user_repository import RepositoryError, UserRepository
from src.core.result import Result
from src.core.user import User

RegistrationError = Union[RepositoryError, ApplicationError]


class AccountService:
    """
    Service responsible for user authentication and registration operations.
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialize AccountService with a user repository.

        Args:
            user_repo (UserRepository): Repository for user data operations.
        """
        self.user_repo = user_repo

    def authenticate(
        self, username: str, password: str
    ) -> Result[User, InvalidCredentialsError]:
        """
        Authenticate a user given a username (or email) and password.

        Args:
            username (str): Username or email to authenticate.
            password (str): Plain text password to verify.

        Returns:
            Result[User, InvalidCredentialsError]: Ok with User on success, Err with error on failure.
        """
        user = self.user_repo.load_for_auth(username)
        if user is not None and self.user_repo.verify_password(user, password):
            return Result.Ok(user)

        return Result.Err(InvalidCredentialsError())

    def register(
        self, username: str, email: str, password: str, password2: str
    ) -> Result[User, RegistrationError]:
        """
        Register a new user with provided credentials.

        Args:
            username (str): Desired username for the new user.
            email (str): Email address for the new user.
            password (str): Password for the new user.
            password2 (str): Password confirmation.

        Returns:
            Result[User, RegistrationError]: Ok with User on success, Err with error on failure.
        """
        if password != password2:
            return Result.Err(PasswordsDoNotMatchError())

        result = self.user_repo.register(username, email, password)
        if result.is_err:
            return Result.Err(result.unwrap_err())
        return Result.Ok(result.unwrap())
