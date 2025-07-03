from sqlite3 import Connection

from flask_bcrypt import Bcrypt

from src.core.ports.user_repository import UserRepository
from src.core.user import User
from src.infra.db import get_connection


class SQLUserRepository(UserRepository):
    def __init__(self, bcrypt: Bcrypt):
        self.bcrypt = bcrypt

    def find_by_username(self, username: str) -> User | None:
        conn = get_connection()
        cur = conn.execute(
            "SELECT id, username, email FROM users WHERE username = ?",
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
        )

    def find_by_username_or_email(self, username_or_email: str) -> User | None:
        conn = get_connection()
        cur = conn.execute(
            "SELECT id, username, email FROM users WHERE username = ? OR email = ?",
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
        )

    def load_for_auth(self, username_or_email: str) -> User | None:
        conn = get_connection()
        cur = conn.execute(
            "SELECT id, username, email, pw_hash FROM users WHERE username = ? OR email = ?",
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
        )

    def verify_password(self, user: User, password: str) -> bool:
        return self.bcrypt.check_password_hash(user.pw_hash, password)

    def get_by_id(self, user_id: int) -> User | None:
        conn = get_connection()
        cur = conn.execute(
            "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
        )

        row = cur.fetchone()

        if not row:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
        )

    def add(self, user: User) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (?,?,?,?)",
            (user.id, user.username, user.email, user.pw_hash),
        )
        conn.commit()

    def list_all(self) -> list[User]:
        conn = get_connection()
        cur = conn.execute("SELECT id, name, email FROM users")
        return [
            User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                pw_hash=None,
            )
            for row in cur.fetchall()
        ]

    def register(self, username: str, email: str, password: str) -> User:
        pw_hash = self.bcrypt.generate_password_hash(password).decode()
        conn = get_connection()
        cur = conn.execute(
            "SELECT id, username, email FROM users WHERE username = ? OR email = ?",
            (username, email),
        )

        if cur.fetchone() is not None:
            raise ValueError("User already exists")

        conn.execute(
            "INSERT INTO users (username, email, pw_hash) VALUES (?, ?, ?)",
            (username, email, pw_hash),
        )
        conn.commit()

        cur = conn.execute(
            "SELECT id, username, email FROM users WHERE username = ?",
            (username,),
        )

        row = cur.fetchone()
        if not row:
            raise ValueError("Could not create user entry during registration")

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
        )
