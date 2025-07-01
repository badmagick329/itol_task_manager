from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from flask import current_app

    service = current_app.extensions["auth_service"]
    if request.method == "POST":
        user = service.authenticate(
            request.form["username"], request.form["password"]
        )
        if user:
            login_user(user)
            return redirect(url_for("main.protected"))
        abort(401)
    return render_template("auth/login.html")


@auth_bp.route("/protected")
@login_required
def protected():
    return render_template_string(f"Hello {current_user.username}!")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template_string("Logged out")
