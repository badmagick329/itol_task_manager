import pytest

from src.main import app


class TestDummyTests:
    """Dummy test class to verify pytest setup."""

    def test_dummy_assertion(self):
        """Test that basic assertions work."""
        assert True
        assert 1 + 1 == 2
        assert "hello" in "hello world"

    def test_dummy_with_fixture(self, sample_data):
        """Test using a fixture."""
        assert sample_data["name"] == "test"
        assert sample_data["value"] == 42

    @pytest.mark.slow
    def test_dummy_marked_slow(self):
        """Test with a custom marker."""
        assert len("pytest") == 6


class TestFlaskApp:
    """Test class for Flask application."""

    def test_app_exists(self):
        """Test that the Flask app exists."""
        assert app is not None
        assert app.name == "src.main"

    def test_app_config(self, app):
        """Test Flask app configuration."""
        assert app.config.get("TESTING", False)

    def test_hello_world_route(self, client):
        """Test the hello world route."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Hello, World!" in response.data

    def test_client_uses_testing_config(self, client, app):
        """Test that the client uses the testing configuration."""
        assert app.config["TESTING"] is True

        response = client.get("/")
        assert response.status_code == 200


@pytest.fixture
def sample_data():
    """Fixture providing sample data for tests."""
    return {"name": "test", "value": 42, "items": [1, 2, 3, 4, 5]}
