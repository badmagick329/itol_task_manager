from flask import Blueprint, render_template, render_template_string
from flask.helpers import redirect, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def hello_world():
    return redirect(url_for("task.dashboard"))


# TEST ROUTE
@main_bp.route("/hello/")
@main_bp.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", name=name)
