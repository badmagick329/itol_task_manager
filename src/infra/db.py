import sqlite3

from flask import current_app, g
from flask_bcrypt import Bcrypt


def get_connection():
    """Get a database connection from the Flask application context.

    Returns:
        sqlite3.Connection: The database connection.
    """
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
    """Close the database connection if it exists in the Flask application context.

    Args:
        e (Exception, optional): An exception that may have occurred. Defaults to None.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_teardown_handler(app):
    """Register a teardown handler to close the database connection.

    Args:
        app (Flask): The Flask application instance.
    """
    app.teardown_appcontext(close_db)


def init_db():
    """
    Initialize the database by creating necessary tables. This will typically be called with the Flask CLI
    command `flask init-db`.
    """
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            pw_hash TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL CHECK (LENGTH(title) <= 100),
            description TEXT CHECK (LENGTH(description) <= 500),
            due_date DATE NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('To Do', 'In Progress', 'Completed')),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()


def create_test_admin(
    bcrypt: Bcrypt, username: str, email: str, password: str
):
    conn = get_connection()
    pw_hash = bcrypt.generate_password_hash(password).decode()
    conn.execute(
        """
        INSERT OR IGNORE INTO users (username, email, pw_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """,
        (username, email, pw_hash, True),
    )
    conn.commit()
