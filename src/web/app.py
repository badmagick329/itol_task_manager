from pathlib import Path

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from src.config import Config
from src.infra.in_memory_user import InMemoryUser
from src.services.auth_service import AuthService

bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_class=Config):
    # configure template and static folders to correct src locations
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(Path(base_dir, "templates")),
        static_folder=str(Path(base_dir, "static")),
    )
    app.config.from_object(config_class)

    # extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore

    # ports and services
    user_repo = InMemoryUser(bcrypt)
    # register AuthService as a Flask extension so blueprints can access it
    auth_service = AuthService(user_repo)
    app.extensions["auth_service"] = auth_service

    # user loader
    @login_manager.user_loader
    def load_user(user_id):
        user = user_repo.find_by_username("admin")
        return user if user and str(user.id) == str(user_id) else None

    # register blueprints
    from src.web.routes.auth import auth_bp
    from src.web.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
