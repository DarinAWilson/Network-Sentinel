import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from loki_client import get_latest_alert
from ai_engine import generate_explanation


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
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


@app.route("/")
def portal_home():
    return render_template("index.html")


@app.route("/alert-analysis")
def alert_analysis():
    return render_template("ai-assistant.html")


@app.route("/api/latest-alert")
def latest_alert():
    return jsonify(get_latest_alert())


@app.route("/api/analyze-latest")
def analyze_latest():
    alert = get_latest_alert()
    explanation = generate_explanation(alert)

    return jsonify(explanation)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)