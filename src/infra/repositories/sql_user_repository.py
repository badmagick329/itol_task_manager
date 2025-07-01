from sqlite3 import Connection

from src.core.ports.user_repository import UserRepository
from src.core.user import User as DomainUser
from src.infra.db import get_connection


class SQLUserRepository(UserRepository):
    def __init__(self, conn: Connection | None):
        self.conn = conn or get_connection()

    def get_by_id(self, user_id: int) -> DomainUser | None:
        cur = self.conn.execute(
            "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
        )

        row = cur.fetchone()

        if not row:
            return None

        return DomainUser(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            pw_hash=None,
        )

    def add(self, user: DomainUser) -> None:
        self.conn.execute(
            "INSERT INTO users (?,?,?,?)",
            (user.id, user.username, user.email, user.pw_hash),
        )
        self.conn.commit()

    def list_all(self) -> list[DomainUser]:
        cur = self.conn.execute("SELECT id, name, email FROM users")
        return [
            DomainUser(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                pw_hash=None,
            )
            for row in cur.fetchall()
        ]
