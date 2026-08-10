def get_latest_alert():
    """
    Placeholder function.

    This will eventually query Loki for the latest
    Suricata security event.
    """

    return {
        "title": "Network Scan Detected",
        "risk": "High",
        "source": "WORKSTATION-01",
        "target": "SERVER-01"
    }