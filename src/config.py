class Config:
    """
    Base configuration class containing default settings for the application.
    """

    DATABASE = "app.db"
    TESTING = False

    @classmethod
    def inject_secret(cls, secret: str):
        cls.SECRET_KEY = secret


class TestConfig(Config):
    """
    Configuration class for testing, inherits from Config and enables testing mode with in-memory database.
    """

    SECRET_KEY = "replace-this-with-a-real-secret"
    TESTING = True
    DATABASE = ":memory:"
