from pathlib import Path

from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import click

from src.config import Config
from src.infra.repositories.in_memory_user import InMemoryUserRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository
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
    # app config
    app.config.from_object(config_class)

    # extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore

    # db setup
    from src.infra.db import init_db_teardown_handler

    init_db_teardown_handler(app)

    app.cli.add_command(init_db_command)

    # ports and services
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    auth_service = AuthService(user_repo)
    app.extensions["auth_service"] = auth_service

    # user loader
    @login_manager.user_loader
    def load_user(user_id: int):
        return user_repo.get_by_id(user_id)

    # register blueprints
    from src.web.routes.auth import auth_bp
    from src.web.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    from src.infra.db import init_db

    init_db(bcrypt)
    click.echo("Initialized the database.")
