from sqlite3 import Connection

from flask_bcrypt import Bcrypt

from src.core.errors import (
    DomainError,
    UserCreationError,
    UsernameTaken,
    UserNotFoundError,
    ValidationError,
)
from src.core.ports.user_repository import RepositoryError, UserRepository
from src.core.result import Result
from src.core.user import User
from src.infra.db import get_connection


class SQLUserRepository(UserRepository):
    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt

    def find_by_username(self, username: str) -> User | None:
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
        return self.bcrypt.check_password_hash(user.pw_hash, password)

    def get_by_id(self, user_id: int) -> User | None:
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
        conn = self._get_connection()
        first_user = self._repo_is_empty(conn)

        if not first_user and self._username_is_taken(conn, username, email):
            return Result.Err(UsernameTaken(username))

        created_user_result = self._create_user(
            conn=conn,
            username=username,
            email=email,
            password=password,
            is_admin=first_user,
        )
        if created_user_result.is_err:
            # Convert ValidationError to the expected error type
            return Result.Err(created_user_result.unwrap_err())

        return Result.Ok(created_user_result.unwrap())

    def _repo_is_empty(self, conn: Connection) -> bool:
        cur = conn.execute(
            "SELECT COUNT(*) as count FROM users",
            (),
        )
        row = cur.fetchone()
        return row and row["count"] == 0

    def _username_is_taken(
        self, conn: Connection, username: str, email: str
    ) -> bool:
        cur = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE username = ? OR email = ?",
            (username, email),
        )

        return cur.fetchone()["count"] > 0

    def _create_user(
        self, conn, username: str, email: str, password: str, is_admin: bool
    ) -> Result[User, UserCreationError]:
        pw_hash = self.bcrypt.generate_password_hash(password).decode()

        created_user_result = User.create(
            id=0,  # ID will be assigned by the database
            username=username,
            email=email,
            pw_hash=pw_hash,
            is_admin=is_admin,
        )
        if created_user_result.is_err:
            # Convert ValidationError to the expected error type
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
        return get_connection()
