import base64
import os
import time
from functools import wraps

import requests

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

from ai_engine import generate_explanation
from loki_client import get_latest_alert
from threat_intel import enrich_alert


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
AUTH_USERNAME = os.getenv("NS_AUTH_USERNAME")
AUTH_PASSWORD_HASH_B64 = os.getenv("NS_AUTH_PASSWORD_HASH_B64")
AUTH_TENANT_ID = os.getenv("NS_AUTH_TENANT_ID")

CUSTOMER_NAME = os.getenv(
    "NS_CUSTOMER_NAME",
    AUTH_TENANT_ID
)

LOKI_URL = "http://loki:3100"


AUTH_PASSWORD_HASH = (
    base64.b64decode(
        AUTH_PASSWORD_HASH_B64
    ).decode()
    if AUTH_PASSWORD_HASH_B64
    else None
)


if not SECRET_KEY:
    raise RuntimeError(
        "FLASK_SECRET_KEY environment variable is required"
    )

if not AUTH_USERNAME:
    raise RuntimeError(
        "NS_AUTH_USERNAME environment variable is required"
    )

if not AUTH_PASSWORD_HASH:
    raise RuntimeError(
        "NS_AUTH_PASSWORD_HASH_B64 environment variable is required"
    )

if not AUTH_TENANT_ID:
    raise RuntimeError(
        "NS_AUTH_TENANT_ID environment variable is required"
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

            return redirect(
                url_for("login")
            )

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view


def check_loki_health():
    """
    Confirm that Loki is reachable from the AI backend.
    """

    try:
        response = requests.get(
            f"{LOKI_URL}/ready",
            timeout=5
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


def check_recent_telemetry(
    tenant_id,
    minutes=15
):
    """
    Confirm that Suricata telemetry has arrived in Loki
    recently for the authenticated tenant.
    """

    if not tenant_id:
        return False

    end_time = time.time_ns()

    start_time = (
        end_time
        - (
            minutes
            * 60
            * 1_000_000_000
        )
    )

    query = '{job="suricata"}'

    try:
        response = requests.get(
            f"{LOKI_URL}/loki/api/v1/query_range",
            params={
                "query": query,
                "start": start_time,
                "end": end_time,
                "limit": 1,
                "direction": "backward"
            },
            headers={
                "X-Scope-OrgID": tenant_id
            },
            timeout=5
        )

        response.raise_for_status()

        results = (
            response
            .json()
            .get("data", {})
            .get("result", [])
        )

        return bool(results)

    except requests.RequestException:
        return False


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        valid_username = (
            username == AUTH_USERNAME
        )

        valid_password = check_password_hash(
            AUTH_PASSWORD_HASH,
            password
        )

        if valid_username and valid_password:

            session.clear()

            session["authenticated"] = True
            session["username"] = AUTH_USERNAME
            session["tenant_id"] = AUTH_TENANT_ID

            return redirect(
                url_for("portal_home")
            )

        error = (
            "Invalid username or password."
        )

    return render_template(
        "login.html",
        error=error
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


@app.route("/")
@login_required
def portal_home():

    return render_template(
        "index.html",
        customer_name=CUSTOMER_NAME,
        tenant_id=session.get(
            "tenant_id"
        )
    )


@app.route("/alert-analysis")
@login_required
def alert_analysis():

    return render_template(
        "ai-assistant.html",
        customer_name=CUSTOMER_NAME,
        tenant_id=session.get(
            "tenant_id"
        )
    )


@app.route("/api/health")
@login_required
def health():

    tenant_id = session.get(
        "tenant_id"
    )

    loki_healthy = (
        check_loki_health()
    )

    recent_telemetry = False

    if loki_healthy:
        recent_telemetry = (
            check_recent_telemetry(
                tenant_id
            )
        )

    if (
        loki_healthy
        and recent_telemetry
    ):
        overall_status = "healthy"

    elif loki_healthy:
        overall_status = "degraded"

    else:
        overall_status = "offline"

    return jsonify({
        "status": overall_status,
        "backend": True,
        "loki": loki_healthy,
        "recent_telemetry": recent_telemetry,
        "telemetry_window_minutes": 15,
        "tenant_id": tenant_id
    })


@app.route("/api/latest-alert")
@login_required
def latest_alert():

    tenant_id = session.get(
        "tenant_id"
    )

    return jsonify(
        get_latest_alert(
            tenant_id
        )
    )


@app.route("/api/analyze-latest")
@login_required
def analyze_latest():

    tenant_id = session.get(
        "tenant_id"
    )

    alert = get_latest_alert(
        tenant_id
    )

    enriched_alert = enrich_alert(
        alert
    )

    explanation = generate_explanation(
        enriched_alert
    )

    return jsonify(
        explanation
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )