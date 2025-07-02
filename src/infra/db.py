import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "app.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                pw_hash TEXT NOT NULL
            );
            """
        )

        # NOTE: Hardcoded admin for now. Remove later
        from flask_bcrypt import Bcrypt

        bcrypt = Bcrypt()
        pw_hash = bcrypt.generate_password_hash("test123").decode()
        conn.execute(
            """
            INSERT OR IGNORE INTO users (username, email, pw_hash)
            VALUES (?, ?, ?)
            """,
            ("admin", "admin@admin.com", pw_hash),
        )
        conn.commit()
