import sqlite3

from flask import current_app, g
from flask_bcrypt import Bcrypt


def get_connection():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], check_same_thread=True
        )
        g.db.row_factory = sqlite3.Row
        for stmt in (
            "PRAGMA foreign_keys = ON",
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL",
            "PRAGMA busy_timeout = 5000",
        ):
            g.db.execute(f"{stmt};")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_teardown_handler(app):
    app.teardown_appcontext(close_db)


def init_db(bcrypt: Bcrypt):
    conn = get_connection()
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

    pw_hash = bcrypt.generate_password_hash("test123").decode()

    conn.execute(
        """
        INSERT OR IGNORE INTO users (username, email, pw_hash)
        VALUES (?, ?, ?)
        """,
        ("admin", "admin@admin.com", pw_hash),
    )
    conn.commit()
