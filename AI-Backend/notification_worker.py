import json
import os
import time

import requests

from notification_manager import (
    notify_health_status,
    notify_high_risk_alert,
)


LOKI_URL = "http://loki:3100"

TENANT_ID = os.getenv(
    "NS_AUTH_TENANT_ID"
)

CUSTOMER_NAME = os.getenv(
    "NS_CUSTOMER_NAME",
    TENANT_ID
)

ALERT_LOOKBACK_MINUTES = int(
    os.getenv(
        "NOTIFICATION_ALERT_LOOKBACK_MINUTES",
        "10"
    )
)


def check_loki_health():
    """
    Confirm Loki is reachable.
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
    Confirm Suricata telemetry has arrived recently
    for the customer tenant.
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

    try:
        response = requests.get(
            f"{LOKI_URL}/loki/api/v1/query_range",
            params={
                "query": '{job="suricata"}',
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


def get_health_status(
    tenant_id
):
    """
    Determine the current monitoring health state.
    """

    loki_healthy = check_loki_health()

    if not loki_healthy:
        return "offline"

    recent_telemetry = check_recent_telemetry(
        tenant_id
    )

    if not recent_telemetry:
        return "degraded"

    return "healthy"


def get_recent_high_risk_alerts(
    tenant_id,
    minutes=10
):
    """
    Retrieve High-risk Suricata alerts seen within
    the configured lookback window.

    Suricata severity 1 maps to Network Sentinel High risk.
    """

    if not tenant_id:
        raise ValueError(
            "A tenant ID is required for Loki queries"
        )

    end_time = time.time_ns()

    start_time = (
        end_time
        - (
            minutes
            * 60
            * 1_000_000_000
        )
    )

    query = (
        '{job="suricata"} '
        '| json '
        '| event_type="alert" '
        '| alert_severity="1"'
    )

    response = requests.get(
        f"{LOKI_URL}/loki/api/v1/query_range",
        params={
            "query": query,
            "start": start_time,
            "end": end_time,
            "limit": 100,
            "direction": "backward"
        },
        headers={
            "X-Scope-OrgID": tenant_id
        },
        timeout=10
    )

    response.raise_for_status()

    results = (
        response
        .json()
        .get("data", {})
        .get("result", [])
    )

    alerts = []

    for stream in results:
        for value in stream.get(
            "values",
            []
        ):
            try:
                event = json.loads(
                    value[1]
                )
            except (
                json.JSONDecodeError,
                IndexError,
                TypeError
            ):
                continue

            alert_data = event.get(
                "alert",
                {}
            )

            alerts.append({
                "title": alert_data.get(
                    "signature",
                    "Unknown Alert"
                ),
                "risk": "High",
                "source": event.get(
                    "src_ip",
                    "Unknown"
                ),
                "target": event.get(
                    "dest_ip",
                    "Unknown"
                )
            })

    return alerts


def run_notification_check():
    """
    Perform one Network Sentinel notification check.
    """

    if not TENANT_ID:
        raise RuntimeError(
            "NS_AUTH_TENANT_ID is required"
        )

    # -------------------------------------------------
    # High-risk security alert checks
    # -------------------------------------------------

    high_risk_alerts = []

    if check_loki_health():
        high_risk_alerts = (
            get_recent_high_risk_alerts(
                tenant_id=TENANT_ID,
                minutes=ALERT_LOOKBACK_MINUTES
            )
        )

    alert_emails_sent = 0

    for alert in high_risk_alerts:

        sent = notify_high_risk_alert(
            tenant_id=TENANT_ID,
            customer_name=CUSTOMER_NAME,
            alert=alert
        )

        if sent:
            alert_emails_sent += 1

    # -------------------------------------------------
    # Monitoring health check
    # -------------------------------------------------

    health_status = get_health_status(
        TENANT_ID
    )

    health_sent = notify_health_status(
        tenant_id=TENANT_ID,
        customer_name=CUSTOMER_NAME,
        health_status=health_status
    )

    print(
        f"Notification check complete. "
        f"Health={health_status}, "
        f"High-risk alerts found={len(high_risk_alerts)}, "
        f"Alert emails sent={alert_emails_sent}, "
        f"Health email sent={health_sent}"
    )


if __name__ == "__main__":
    run_notification_check()