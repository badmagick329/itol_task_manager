from pathlib import Path

import sys

import pytest

BASE_DIR = Path(__file__).parent.parent / "src"
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    from src.config import TestConfig
    from src.web.app import create_app  # noqa: E402

    flask_app = create_app(TestConfig)
    from src.infra.db import init_db_teardown_handler

    init_db_teardown_handler(flask_app)

    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def bcrypt(app):
    from src.web.app import bcrypt as _bcrypt  # noqa: F401

    """A fixture to provide the bcrypt instance."""
    return _bcrypt


@pytest.fixture(autouse=True)
def db(app, bcrypt):
    from src.infra.db import (
        close_db,
        get_connection,
        init_db,
    )

    with app.app_context():
        init_db(bcrypt)
        yield get_connection()
        close_db()
