from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from src.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from flask import current_app

    service: AuthService = current_app.extensions["auth_service"]
    if request.method == "POST":
        auth_result = service.authenticate(
            request.form["username"], request.form["password"]
        )
        if auth_result.is_err:
            return render_template(
                "auth/login.html", error=auth_result.unwrap_err()
            )
        login_user(auth_result.unwrap())
        return redirect(url_for("auth.protected"))
    return render_template("auth/login.html")


@auth_bp.route("/protected")
@login_required
def protected():
    return render_template(
        "protected/home.html", username=current_user.username
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

    auth_service: AuthService = current_app.extensions["auth_service"]
    user_result = auth_service.register(
        username=username, email=email, password=password, password2=password2
    )
    if user_result.is_err:
        return render_template(
            "auth/register.html", error=user_result.unwrap_err()
        )

    user = user_result.unwrap()

    login_user(user)

    return redirect(url_for("auth.protected"))
