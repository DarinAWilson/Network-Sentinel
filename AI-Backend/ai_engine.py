"""
Network Sentinel AI Security Assistant

Provides plain-English explanations and recommended actions
for security alerts collected by Network Sentinel.
"""


def generate_explanation(alert):
    """
    Analyze a Network Sentinel alert and return a structured
    security explanation.
    """

    title = alert.get("title", "Unknown Security Event")
    risk = alert.get("risk", "Unknown")
    source = alert.get("source", "Unknown")
    target = alert.get("target", "Unknown")

    title_lower = title.lower()

    # Determine the type of security activity
    if "scan" in title_lower:
        analysis = (
            "Network Sentinel detected activity consistent with network "
            "scanning or reconnaissance. Scanning is commonly used to "
            "identify active systems, open ports, and available services."
        )

        why_it_matters = (
            "Network scans may be legitimate administrative activity, but "
            "unexpected scanning can also represent the reconnaissance "
            "stage of an attack."
        )

        actions = [
            "Verify whether the source device is trusted.",
            "Confirm that the scanning activity was authorized.",
            "Review related firewall and Suricata events.",
            "Monitor the source for additional suspicious activity."
        ]

    elif "http" in title_lower:
        analysis = (
            "Network Sentinel detected unusual HTTP communication. This "
            "may result from malformed requests, application errors, "
            "automated scanners, or unexpected web traffic."
        )

        why_it_matters = (
            "Repeated or unexpected HTTP anomalies can indicate application "
            "problems, reconnaissance, or attempts to interact with a web "
            "service in an unintended way."
        )

        actions = [
            "Verify the source and destination systems.",
            "Review related web server or application logs.",
            "Check for repeated HTTP alerts from the same source.",
            "Continue monitoring for additional suspicious activity."
        ]

    elif "dns" in title_lower:
        analysis = (
            "Network Sentinel detected DNS-related network activity. DNS is "
            "normally used to translate domain names into IP addresses, but "
            "unusual DNS activity can sometimes indicate suspicious network "
            "communication."
        )

        why_it_matters = (
            "Unexpected domains, unusually frequent requests, or repeated "
            "DNS alerts may warrant additional investigation."
        )

        actions = [
            "Review the domain or destination involved.",
            "Verify that the source device is expected to make the request.",
            "Monitor for repeated or unusual DNS activity."
        ]

    elif "file hosting" in title_lower:
        analysis = (
            "Network Sentinel detected communication with a known file-hosting "
            "service. File-hosting services are commonly used for legitimate "
            "software downloads and updates, but they can also be used to "
            "distribute unwanted or malicious files."
        )

        why_it_matters = (
            "This alert does not necessarily indicate an attack. The activity "
            "should be reviewed in context to determine whether the connection "
            "was expected."
        )

        actions = [
            "Identify the application or device responsible for the connection.",
            "Verify that the file-hosting domain is expected.",
            "Review related Suricata alerts for suspicious activity.",
            "Continue monitoring if the activity is unexpected."
        ]

    else:
        analysis = (
            "Network Sentinel detected a security event reported by Suricata. "
            "The event should be reviewed together with the source, destination, "
            "risk level, and surrounding network activity."
        )

        why_it_matters = (
            "A single security alert does not always indicate malicious "
            "activity. Reviewing the context of the event helps determine "
            "whether additional investigation is necessary."
        )

        actions = [
            "Verify the source and destination systems.",
            "Review related Suricata events.",
            "Determine whether the activity was expected.",
            "Continue monitoring for repeated alerts."
        ]

    return {
        "title": title,
        "risk": risk,
        "source": source,
        "target": target,
        "analysis": analysis,
        "why_it_matters": why_it_matters,
        "recommended_actions": actions
    }