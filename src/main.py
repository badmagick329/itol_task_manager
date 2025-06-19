from flask import Flask, request, redirect, url_for, abort, render_template_string

from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "replace-this-with-a-real-secret"
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login" # type:ignore

class User(UserMixin):
    def __init__(self, id, username, pw_hash):
        self.id = id
        self.username = username
        self.pw_hash = pw_hash

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pw_hash, password)

# NOTE: hardcoded value for now
_admin_hash = bcrypt.generate_password_hash("test123").decode()
_admin = User(id=1, username="admin", pw_hash=_admin_hash)

@login_manager.user_loader
def load_user(user_id):
    return _admin if str(_admin.id) == str(user_id) else None

@app.route("/")
def hello_world():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hello</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <p>Hello, World!</p>
    </body>
    </html>
    ''')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = _admin
        form_u = request.form.get("username", "")
        form_p = request.form.get("password", "")
        if form_u == user.username and user.check_password(form_p):
            login_user(user)
            return redirect(url_for("protected"))
        else:
            abort(401)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <form method="post">
          <input name="username" placeholder="username" autocomplete="off">
          <input name="password" type="password" placeholder="password" autocomplete="off">
          <button type="submit">Log In</button>
        </form>
    </body>
    </html>
    ''')

@app.route("/protected")
@login_required
def protected():
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Protected</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <p>Hello, {current_user.username}!</p>
        <a href="/logout">Logout</a>
    </body>
    </html>
    ''')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Logged out</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <p>Logged out</p>
    </body>
    </html>
    ''')
