class Config:
    SECRET_KEY = "replace-this-with-a-real-secret"
    DATABASE = "app.db"
    TESTING = False


class TestConfig(Config):
    TESTING = True
    DATABASE = ":memory:"
