import base64
import os
from functools import wraps

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_cors import CORS
from werkzeug.security import check_password_hash

from loki_client import get_latest_alert
from ai_engine import generate_explanation


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
AUTH_USERNAME = os.getenv("NS_AUTH_USERNAME")
AUTH_PASSWORD_HASH_B64 = os.getenv("NS_AUTH_PASSWORD_HASH_B64")

AUTH_PASSWORD_HASH = (
    base64.b64decode(AUTH_PASSWORD_HASH_B64).decode()
    if AUTH_PASSWORD_HASH_B64
    else None
)

if not SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY environment variable is required")

if not AUTH_USERNAME:
    raise RuntimeError("NS_AUTH_USERNAME environment variable is required")

if not AUTH_PASSWORD_HASH:
    raise RuntimeError(
        "NS_AUTH_PASSWORD_HASH_B64 environment variable is required"
    )


app.secret_key = SECRET_KEY

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)


ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS
        }
    }
)


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("authenticated"):

            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "Authentication required"
                }), 401

            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        valid_username = username == AUTH_USERNAME
        valid_password = check_password_hash(
            AUTH_PASSWORD_HASH,
            password
        )

        if valid_username and valid_password:

            session.clear()

            session["authenticated"] = True
            session["username"] = AUTH_USERNAME

            return redirect(url_for("portal_home"))

        error = "Invalid username or password."

    return render_template(
        "login.html",
        error=error
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/")
@login_required
def portal_home():

    return render_template("index.html")


@app.route("/alert-analysis")
@login_required
def alert_analysis():

    return render_template("ai-assistant.html")


@app.route("/api/latest-alert")
@login_required
def latest_alert():

    return jsonify(get_latest_alert())


@app.route("/api/analyze-latest")
@login_required
def analyze_latest():

    alert = get_latest_alert()
    explanation = generate_explanation(alert)

    return jsonify(explanation)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )