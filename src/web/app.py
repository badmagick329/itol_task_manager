from pathlib import Path

from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import click

from src.config import Config
from src.infra.repositories.in_memory_user import InMemoryUserRepository
from src.infra.repositories.sql_task_repository import SQLTaskRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository
from src.services.account_service import AccountService
from src.services.api_response_service import ApiResponseService

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
    task_repo = SQLTaskRepository()
    account_service = AccountService(user_repo)
    app.extensions["account_service"] = account_service
    app.extensions["user_repo"] = user_repo
    app.extensions["task_repo"] = task_repo
    app.extensions["api_response_service"] = ApiResponseService()

    # user loader
    @login_manager.user_loader
    def load_user(user_id: int):
        return user_repo.get_by_id(user_id)

    # register blueprints
    from src.web.routes.auth import auth_bp
    from src.web.routes.main import main_bp
    from src.web.routes.task import task_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    from src.infra.db import init_db

    init_db()
    click.echo("Initialized the database.")
