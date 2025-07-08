from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from src.services.account_service import AccountService
from src.services.api_response_service import ApiResponseService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    from flask import current_app

    account_service: AccountService = current_app.extensions["account_service"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    auth_result = account_service.authenticate(
        request.form["username"], request.form["password"]
    )

    if auth_result.is_err:
        return api_response_service.to_response(
            ok=False,
            status=401,
            message="Login failed",
            error=str(auth_result.unwrap_err()),
        )
    login_user(auth_result.unwrap())

    return api_response_service.to_response(
        ok=True,
        status=200,
        redirect=url_for("task.dashboard"),
        message="Login successful",
    )


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    password2 = request.form["password2"]

    from flask import current_app

    account_service: AccountService = current_app.extensions["account_service"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    user_result = account_service.register(
        username=username, email=email, password=password, password2=password2
    )
    if user_result.is_err:
        return api_response_service.to_response(
            ok=False,
            status=400,
            message="Registration failed",
            error=str(user_result.unwrap_err()),
        )

    user = user_result.unwrap()

    login_user(user)

    return api_response_service.to_response(
        ok=True,
        status=201,
        redirect=url_for("task.dashboard"),
        message="Registration successful",
    )


# TEST ROUTE
@auth_bp.route("/protected")
@login_required
def protected():
    return render_template(
        "protected/home.html", username=current_user.username
    )
