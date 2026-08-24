import json
import os
import time
import requests


LOKI_URL = "http://loki:3100"
LOKI_TENANT_ID = os.getenv("LOKI_TENANT_ID")

if not LOKI_TENANT_ID:
    raise RuntimeError("LOKI_TENANT_ID environment variable is required")


def get_latest_alert():
    """
    Query Loki for the latest Suricata security alert.
    """

    end_time = time.time_ns()

    # Search the previous 24 hours
    start_time = end_time - (24 * 60 * 60 * 1_000_000_000)

    query = '{job="suricata"} | json | event_type="alert"'

    params = {
        "query": query,
        "start": start_time,
        "end": end_time,
        "limit": 1,
        "direction": "backward"
    }

    response = requests.get(
        f"{LOKI_URL}/loki/api/v1/query_range",
        params=params,
        headers={
            "X-Scope-OrgID": LOKI_TENANT_ID
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("data", {}).get("result", [])

    if not results:
        return {
            "title": "No Recent Alerts",
            "risk": "None",
            "source": "N/A",
            "target": "N/A"
        }

    # Get the newest log entry
    log_line = results[0]["values"][0][1]
    alert = json.loads(log_line)

    alert_data = alert.get("alert", {})

    severity = alert_data.get("severity")

    risk_levels = {
        1: "High",
        2: "Medium",
        3: "Low"
    }

    risk = risk_levels.get(severity, "Unknown")

    return {
        "title": alert_data.get("signature", "Unknown Alert"),
        "risk": risk,
        "source": alert.get("src_ip", "Unknown"),
        "target": alert.get("dest_ip", "Unknown")
    }