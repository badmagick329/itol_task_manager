import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "src"
if (str(BASE_DIR) not in sys.path):
    sys.path.append(str(BASE_DIR))


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    from main import app as flask_app
    
    flask_app.config.update({
        "TESTING": True,
    })
    
    return flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
