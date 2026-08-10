from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/api/latest-alert")
def latest_alert():

    return jsonify({
        "title": "Network Scan Detected",
        "risk": "High",
        "source": "WORKSTATION-01",
        "target": "SERVER-01"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)