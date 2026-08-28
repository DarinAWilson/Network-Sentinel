import json
import time

import requests

from alert_filter import apply_noise_reduction


LOKI_URL = "http://loki:3100"


def _logql_string(value):
    """
    Safely format a value for use inside a LogQL string filter.
    """

    return json.dumps(
        str(value)
    )


def get_repeat_count(
    tenant_id,
    title,
    source,
    target
):
    """
    Count how many times the same Suricata alert signature,
    source IP, and destination IP occurred during the
    previous hour for the authenticated tenant.
    """

    if not tenant_id:
        raise ValueError(
            "A tenant ID is required for Loki queries"
        )

    title_filter = _logql_string(
        title
    )

    source_filter = _logql_string(
        source
    )

    target_filter = _logql_string(
        target
    )

    query = f"""
sum(
    count_over_time(
        {{job="suricata"}}
        | json
        | event_type="alert"
        | alert_signature={title_filter}
        | src_ip={source_filter}
        | dest_ip={target_filter}
        [1h]
    )
)
"""

    response = requests.get(
        f"{LOKI_URL}/loki/api/v1/query",
        params={
            "query": query
        },
        headers={
            "X-Scope-OrgID": tenant_id
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = (
        data
        .get("data", {})
        .get("result", [])
    )

    if not results:
        return 1

    try:
        count = int(
            float(
                results[0]["value"][1]
            )
        )
    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ):
        return 1

    return max(
        count,
        1
    )


def get_latest_alert(tenant_id):
    """
    Query Loki for the latest Suricata security alert
    belonging to the authenticated tenant.

    The returned alert also includes customer-facing
    noise-reduction metadata.
    """

    if not tenant_id:
        raise ValueError(
            "A tenant ID is required for Loki queries"
        )

    end_time = time.time_ns()

    # Search the previous 24 hours.
    start_time = (
        end_time
        - (
            24
            * 60
            * 60
            * 1_000_000_000
        )
    )

    query = (
        '{job="suricata"} '
        '| json '
        '| event_type="alert"'
    )

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
            "X-Scope-OrgID": tenant_id
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = (
        data
        .get("data", {})
        .get("result", [])
    )

    if not results:
        return {
            "title": "No Recent Alerts",
            "risk": "None",
            "source": "N/A",
            "target": "N/A"
        }

    # Get the newest log entry.
    log_line = (
        results[0]["values"][0][1]
    )

    alert = json.loads(
        log_line
    )

    alert_data = alert.get(
        "alert",
        {}
    )

    severity = alert_data.get(
        "severity"
    )

    risk_levels = {
        1: "High",
        2: "Medium",
        3: "Low"
    }

    risk = risk_levels.get(
        severity,
        "Unknown"
    )

    parsed_alert = {
        "title": alert_data.get(
            "signature",
            "Unknown Alert"
        ),
        "risk": risk,
        "source": alert.get(
            "src_ip",
            "Unknown"
        ),
        "target": alert.get(
            "dest_ip",
            "Unknown"
        )
    }

    repeat_count = get_repeat_count(
        tenant_id=tenant_id,
        title=parsed_alert["title"],
        source=parsed_alert["source"],
        target=parsed_alert["target"]
    )

    return apply_noise_reduction(
        parsed_alert,
        repeat_count=repeat_count
    )