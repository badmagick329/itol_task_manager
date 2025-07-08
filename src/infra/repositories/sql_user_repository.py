from sqlite3 import Connection

from flask_bcrypt import Bcrypt

from src.core.errors import (
    DomainError,
    EmailTaken,
    InvalidPassword,
    UserCreationError,
    UsernameTaken,
    UserNotFoundError,
)
from src.core.ports.user_repository import RepositoryError, UserRepository
from src.core.result import Result
from src.core.user import User
from src.infra.db import get_connection


class SQLUserRepository(UserRepository):
    """SQL (SQLite) implementation of UserRepository using Flask-Bcrypt for password hashing."""

    def __init__(self, bcrypt: Bcrypt):
        """Initialize the SQL user repository.

        Args:
            bcrypt (Bcrypt): The Flask-Bcrypt instance for password hashing.
        """
        self.bcrypt = bcrypt

    def find_by_username(self, username: str) -> User | None:
        """Find a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The User object if found, otherwise None.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, username, email, is_admin FROM users WHERE username = ?",
            (username,),
        )

        row = cur.fetchone()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
            is_admin=bool(row["is_admin"]),
        )

    def find_by_username_or_email(self, username_or_email: str) -> User | None:
        """Find a user by username or email.

        Args:
            username_or_email (str): The username or email to search for.

        Returns:
            User | None: The User object if found, otherwise None.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, username, email, is_admin FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email),
        )

        row = cur.fetchone()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
            is_admin=bool(row["is_admin"]),
        )

    def load_for_auth(self, username_or_email: str) -> User | None:
        """Load a user with password hash for authentication.

        Args:
            username_or_email (str): The username or email of the user.

        Returns:
            User | None: The User object with pw_hash if found, otherwise None.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, username, email, pw_hash, is_admin FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email),
        )

        row = cur.fetchone()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=row["pw_hash"],
            is_admin=bool(row["is_admin"]),
        )

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
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, username, email, is_admin FROM users WHERE id = ?",
            (user_id,),
        )

        row = cur.fetchone()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
            is_admin=bool(row["is_admin"]),
        )

    def list_all(self) -> list[User]:
        """List all users in the repository.

        Returns:
            list[User]: A list of all users.
        """
        conn = self._get_connection()
        cur = conn.execute("SELECT id, username, email, is_admin FROM users")
        return [
            User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                pw_hash=None,
                is_admin=bool(row["is_admin"]),
            )
            for row in cur.fetchall()
        ]

    def register(
        self, username: str, email: str, password: str
    ) -> Result[User, RepositoryError]:
        """Register a new user in the repository.

        Args:
            username (str): The desired username.
            email (str): The user's email address.
            password (str): The plaintext password.

        Returns:
            Result[User, RepositoryError]: The created User or an error if registration failed.
        """
        conn = self._get_connection()
        first_user = self._repo_is_empty(conn)

        if not first_user and self._username_is_taken(conn, username):
            return Result.Err(UsernameTaken(username))

        if not first_user and self._email_is_taken(conn, email):
            return Result.Err(EmailTaken(email))

        if self._password_is_too_short(password):
            return Result.Err(InvalidPassword(password))

        created_user_result = self._create_user(
            conn=conn,
            username=username,
            email=email,
            password=password,
            is_admin=first_user,
        )
        if created_user_result.is_err:
            return Result.Err(created_user_result.unwrap_err())

        return Result.Ok(created_user_result.unwrap())

    def _repo_is_empty(self, conn: Connection) -> bool:
        """Check if the users repository is empty.

        Args:
            conn (Connection): The SQLite database connection.

        Returns:
            bool: True if no users exist in the repository, False otherwise.
        """
        cur = conn.execute(
            "SELECT COUNT(*) as count FROM users",
            (),
        )
        row = cur.fetchone()
        return row and row["count"] == 0

    def _username_is_taken(self, conn: Connection, username: str) -> bool:
        """Check if a username is already taken.

        Args:
            conn (Connection): The SQLite database connection.
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        cur = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE username = ?",
            (username,),
        )

        return cur.fetchone()["count"] > 0

    def _email_is_taken(self, conn: Connection, email: str) -> bool:
        """Check if an email is already taken.

        Args:
            conn (Connection): The SQLite database connection.
            email (str): The email to check.

        Returns:
            bool: True if the email exists, False otherwise.
        """
        cur = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE email = ?",
            (email,),
        )
        return cur.fetchone()["count"] > 0

    def _create_user(
        self, conn, username: str, email: str, password: str, is_admin: bool
    ) -> Result[User, UserCreationError]:
        """Insert a new user into the database and return the created user.

        Args:
            conn (Connection): The SQLite database connection.
            username (str): The desired username.
            email (str): The user's email address.
            password (str): The plaintext password.
            is_admin (bool): Whether the user should have admin privileges.

        Returns:
            Result[User, UserCreationError]: Ok(User) if creation succeeded, Err on validation or insertion error.
        """
        pw_hash = self.bcrypt.generate_password_hash(password).decode()

        created_user_result = User.create(
            id=0,  # ID will be assigned by the database
            username=username,
            email=email,
            pw_hash=pw_hash,
            is_admin=is_admin,
        )
        if created_user_result.is_err:
            return Result.Err(created_user_result.unwrap_err())

        created_user = created_user_result.unwrap()

        conn.execute(
            "INSERT INTO users (username, email, pw_hash, is_admin) VALUES (?, ?, ?, ?)",
            (created_user.username, created_user.email, pw_hash, is_admin),
        )
        conn.commit()

        cur = conn.execute(
            "SELECT id, username, email, is_admin FROM users WHERE username = ?",
            (username,),
        )

        row = cur.fetchone()
        if not row:
            return Result.Err(UserCreationError())

        return Result.Ok(
            User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                pw_hash=None,
                is_admin=bool(row["is_admin"]),
            )
        )

    def delete(self, username_or_email: str) -> None | DomainError:
        """Delete a user by username or email.

        Args:
            username_or_email (str): The username or email of the user to delete.

        Returns:
            None | DomainError: None if deletion was successful, UserNotFoundError if not found.
        """
        conn = self._get_connection()
        user = self.find_by_username_or_email(username_or_email)
        if not user:
            return UserNotFoundError(username_or_email)

        conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user.id,),
        )
        conn.commit()

    def _get_connection(self) -> Connection:
        """Get a new SQLite database connection.

        Returns:
            Connection: A connection object to the SQLite database.
        """
        return get_connection()

    def _password_is_too_short(self, password: str) -> bool:
        """Determine if a password is shorter than the minimum allowed length.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password length is less than the minimum, False otherwise.
        """
        return len(password) < self.min_password_length
