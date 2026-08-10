from flask import Flask, jsonify
from flask_cors import CORS

from loki_client import get_latest_alert

app = Flask(__name__)
CORS(app)


@app.route("/api/latest-alert")
def latest_alert():

    return jsonify(get_latest_alert())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)