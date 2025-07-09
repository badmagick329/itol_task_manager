"""
Entry point for the Flask application. Loads environment variables and starts the Flask server.
"""

from pathlib import Path

import os
import sys

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from src.config import Config  # noqa: E402
from src.web.app import create_app  # noqa: E402

if __name__ == "__main__":
    load_dotenv()
    secret = os.environ.get("SECRET_KEY")
    if secret:
        Config.inject_secret(secret)
    app = create_app(Config)
    use_reloader = os.environ.get("USE_RELOADER") == "1"
    debug = os.environ.get("DEBUG") == "1"
    app.run(debug=debug, use_reloader=use_reloader)
