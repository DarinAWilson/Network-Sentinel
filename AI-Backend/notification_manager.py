import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from email_notifier import send_email


NOTIFICATION_DB = os.getenv(
    "NOTIFICATION_DB",
    "/app/data/notification_state.db"
)

NOTIFICATION_RECIPIENT = os.getenv(
    "NOTIFICATION_RECIPIENT"
)

PORTAL_URL = os.getenv(
    "PORTAL_URL",
    ""
)

ALERT_NOTIFICATION_COOLDOWN_MINUTES = int(
    os.getenv(
        "ALERT_NOTIFICATION_COOLDOWN_MINUTES",
        "60"
    )
)


def get_connection():
    """
    Open the persistent notification-state database.
    """

    os.makedirs(
        os.path.dirname(NOTIFICATION_DB),
        exist_ok=True
    )

    connection = sqlite3.connect(
        NOTIFICATION_DB
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS notification_state (
            notification_key TEXT PRIMARY KEY,
            notification_type TEXT NOT NULL,
            state_value TEXT,
            sent_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    return connection


def _utc_now():
    return datetime.now(
        timezone.utc
    )


def _get_previous_state(notification_key):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                state_value,
                sent_at
            FROM notification_state
            WHERE notification_key = ?
            """,
            (notification_key,)
        ).fetchone()

        if not row:
            return None

        return {
            "state_value": row[0],
            "sent_at": datetime.fromisoformat(
                row[1]
            )
        }

    finally:
        connection.close()


def _save_state(
    notification_key,
    notification_type,
    state_value
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO notification_state (
                notification_key,
                notification_type,
                state_value,
                sent_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                notification_key,
                notification_type,
                state_value,
                _utc_now().isoformat()
            )
        )

        connection.commit()

    finally:
        connection.close()


def _build_alert_key(
    tenant_id,
    alert
):
    """
    Create a stable fingerprint for an alert.

    The fingerprint remains local and is not included
    in customer-facing email content.
    """

    fingerprint_data = {
        "tenant_id": tenant_id,
        "title": alert.get(
            "title",
            "Unknown Security Event"
        ),
        "risk": alert.get(
            "risk",
            "Unknown"
        ),
        "source": alert.get(
            "source",
            "Unknown"
        ),
        "target": alert.get(
            "target",
            "Unknown"
        ),
    }

    serialized = json.dumps(
        fingerprint_data,
        sort_keys=True
    )

    digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return f"alert:{digest}"


def notify_high_risk_alert(
    tenant_id,
    customer_name,
    alert
):
    """
    Send a notification for a High-risk alert.

    Duplicate alerts with the same signature/source/target
    are suppressed during the configured cooldown period.
    """

    if alert.get("risk") != "High":
        return False

    if not NOTIFICATION_RECIPIENT:
        raise RuntimeError(
            "NOTIFICATION_RECIPIENT is required"
        )

    notification_key = _build_alert_key(
        tenant_id,
        alert
    )

    previous = _get_previous_state(
        notification_key
    )

    if previous:
        cooldown = timedelta(
            minutes=ALERT_NOTIFICATION_COOLDOWN_MINUTES
        )

        if (
            _utc_now() - previous["sent_at"]
            < cooldown
        ):
            return False

    title = alert.get(
        "title",
        "Unknown Security Event"
    )

    source = alert.get(
        "source",
        "Unknown"
    )

    target = alert.get(
        "target",
        "Unknown"
    )

    subject = (
        f"[Network Sentinel] High-Risk Alert - "
        f"{customer_name}"
    )

    body = (
        "Network Sentinel detected a high-risk security event.\n\n"
        f"Customer: {customer_name}\n"
        f"Alert: {title}\n"
        f"Risk: High\n"
        f"Source: {source}\n"
        f"Target: {target}\n\n"
        "This alert should be reviewed promptly."
    )

    if PORTAL_URL:
        body += (
            f"\n\nOpen Network Sentinel:\n"
            f"{PORTAL_URL}"
        )

    send_email(
        recipient=NOTIFICATION_RECIPIENT,
        subject=subject,
        body=body
    )

    _save_state(
        notification_key=notification_key,
        notification_type="security_alert",
        state_value="high"
    )

    return True


def notify_health_status(
    tenant_id,
    customer_name,
    health_status
):
    """
    Send a notification when monitoring health changes
    into degraded or offline.

    Repeated checks of the same unhealthy state do not
    generate additional emails.
    """

    normalized_status = (
        health_status
        or "unknown"
    ).lower()

    if normalized_status not in {
        "degraded",
        "offline"
    }:
        return False

    if not NOTIFICATION_RECIPIENT:
        raise RuntimeError(
            "NOTIFICATION_RECIPIENT is required"
        )

    notification_key = (
        f"health:{tenant_id}"
    )

    previous = _get_previous_state(
        notification_key
    )

    if (
        previous
        and previous["state_value"]
        == normalized_status
    ):
        return False

    subject = (
        f"[Network Sentinel] Monitoring "
        f"{normalized_status.title()} - "
        f"{customer_name}"
    )

    if normalized_status == "offline":
        message = (
            "Network Sentinel cannot currently confirm "
            "that the monitoring service is operating normally."
        )
    else:
        message = (
            "Network Sentinel is online, but recent monitoring "
            "telemetry has not been detected."
        )

    body = (
        f"{message}\n\n"
        f"Customer: {customer_name}\n"
        f"Monitoring Status: {normalized_status.title()}\n\n"
        "Please review the Network Sentinel monitoring system."
    )

    if PORTAL_URL:
        body += (
            f"\n\nOpen Network Sentinel:\n"
            f"{PORTAL_URL}"
        )

    send_email(
        recipient=NOTIFICATION_RECIPIENT,
        subject=subject,
        body=body
    )

    _save_state(
        notification_key=notification_key,
        notification_type="monitoring_health",
        state_value=normalized_status
    )

    return True