from pathlib import Path

import os
import sys

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from src.config import Config  # noqa: E402
from src.web.app import create_app  # noqa: E402

app = create_app(Config)

if __name__ == "__main__":
    load_dotenv()
    use_reloader = os.environ.get("USE_RELOADER") == "1"
    debug = os.environ.get("DEBUG") == "1"
    app.run(debug=debug, use_reloader=use_reloader)
