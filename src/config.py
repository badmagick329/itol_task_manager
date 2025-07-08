class Config:
    """
    Base configuration class containing default settings for the application.
    """

    SECRET_KEY = "replace-this-with-a-real-secret"
    DATABASE = "app.db"
    TESTING = False


class TestConfig(Config):
    """
    Configuration class for testing, inherits from Config and enables testing mode with in-memory database.
    """

    TESTING = True
    DATABASE = ":memory:"
