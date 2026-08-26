from flask import Flask, jsonify
from flask_cors import CORS

from loki_client import get_latest_alert
from ai_engine import generate_explanation

app = Flask(__name__)
CORS(app)


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