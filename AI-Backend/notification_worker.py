import os
import time

import requests

from loki_client import get_latest_alert
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


def run_notification_check():
    """
    Perform one Network Sentinel notification check.
    """

    if not TENANT_ID:
        raise RuntimeError(
            "NS_AUTH_TENANT_ID is required"
        )

    # -------------------------------------------------
    # Security alert check
    # -------------------------------------------------

    alert = get_latest_alert(
        TENANT_ID
    )

    alert_sent = notify_high_risk_alert(
        tenant_id=TENANT_ID,
        customer_name=CUSTOMER_NAME,
        alert=alert
    )

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
        f"Alert email sent={alert_sent}, "
        f"Health email sent={health_sent}"
    )


if __name__ == "__main__":
    run_notification_check()