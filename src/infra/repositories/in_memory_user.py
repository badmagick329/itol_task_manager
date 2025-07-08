from flask_bcrypt import Bcrypt

from src.core.errors import (
    DomainError,
    UsernameTaken,
    UserNotFoundError,
)
from src.core.ports.user_repository import RepositoryError, UserRepository
from src.core.result import Result
from src.core.user import User


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository that stores users in memory and uses Flask-Bcrypt for password hashing."""

    _current_id = 1

    def __init__(self, bcrypt: Bcrypt):
        """Initialize the in-memory user repository.

        Args:
            bcrypt (Bcrypt): The Flask-Bcrypt instance for hashing passwords.
        """
        self.bcrypt = bcrypt
        self.users: dict[str, User] = {}

    def find_by_username(self, username: str) -> User | None:
        """Find a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The User object if found, otherwise None.
        """
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
        """Find a user by username or email.

        Args:
            username_or_email (str): The username or email to search for.

        Returns:
            User | None: The User object if a match is found, otherwise None.
        """
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
        """Load a user with password hash for authentication.

        Args:
            username_or_email (str): The username or email of the user.

        Returns:
            User | None: The User object with pw_hash if found, otherwise None.
        """
        for user in self.users.values():
            if (
                user.username == username_or_email
                or user.email == username_or_email
            ):
                return user

    def verify_password(self, user: User, password: str) -> bool:
        """Verify a user's password against the stored hash.

        Args:
            user (User): The user whose password is to be verified.
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.bcrypt.check_password_hash(user.pw_hash, password)

    def get_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The User object if found, otherwise None.
        """
        for user in self.users.values():
            if user.id == user_id:
                return user

    def list_all(self) -> list[User]:
        """List all users in the repository.

        Returns:
            list[User]: A list of all users.
        """
        return list(self.users.values())

    def register(
        self, username: str, email: str, password: str
    ) -> Result[User, RepositoryError]:
        """Register a new user in the repository.

        Args:
            username (str): The desired username.
            email (str): The user's email address.
            password (str): The plaintext password.

        Returns:
            Result[User, RepositoryError]: Ok(User) if registration succeeds, Err if it fails.
        """
        if username in self.users:
            return Result.Err(UsernameTaken(username))

        # NOTE: validation would go here but this is just a demo class
        pw_hash = self.bcrypt.generate_password_hash(password).decode()
        user_result = User.create(
            id=self._current_id,
            username=username,
            email=email,
            pw_hash=pw_hash,
        )
        if user_result.is_err:
            return Result.Err(user_result.unwrap_err())

        user = user_result.unwrap()
        if self._current_id == 1:
            user.is_admin = True
        self._current_id += 1
        self.users[username] = user
        return Result.Ok(user)

    def delete(self, username_or_email: str) -> None | DomainError:
        """Delete a user by username or email.

        Args:
            username_or_email (str): The username or email of the user to delete.

        Returns:
            None | DomainError: None if deletion is successful, UserNotFoundError if the user is not found.
        """
        user = self.find_by_username_or_email(username_or_email)
        if user is None:
            return UserNotFoundError(username_or_email)

        del self.users[user.username]
