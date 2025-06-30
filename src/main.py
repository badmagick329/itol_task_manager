from src.config import Config
from src.web.app import create_app

app = create_app(Config)

if __name__ == "__main__":
    app.run()
