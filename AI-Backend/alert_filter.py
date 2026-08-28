"""
Network Sentinel alert noise-reduction logic.

This module classifies alerts for customer-facing presentation
without deleting or modifying the original Suricata events stored
in Loki.
"""


NOISY_SIGNATURES = {
    "SURICATA Applayer Detect protocol only one direction": {
        "policy": "deduplicate",
        "reason": (
            "Frequently repeated protocol-detection event that can "
            "generate large volumes of low-value alerts."
        ),
    },

    "SURICATA STREAM Packet with invalid timestamp": {
        "policy": "deduplicate",
        "reason": (
            "Frequently repeated stream-processing event that may "
            "occur during otherwise normal network activity."
        ),
    },

    "SURICATA HTTP unable to match response to request": {
        "policy": "deduplicate",
        "reason": (
            "HTTP parser event that can repeat frequently and is more "
            "useful when summarized than shown individually."
        ),
    },
}


LOW_PRIORITY_SIGNATURES = {
    "ET INFO Internet Printing Protocol (IPP) Get-Printer-Attributes Outbound Request",
    "ET INFO Observed Cloudflare DNS over HTTPS Domain (cloudflare-dns .com in TLS SNI)",
}


def classify_alert(alert):
    """
    Determine how an alert should be presented to the customer.

    Raw alerts remain stored in Loki regardless of classification.
    """

    title = alert.get(
        "title",
        "Unknown Security Event"
    )

    if title in NOISY_SIGNATURES:
        rule = NOISY_SIGNATURES[title]

        return {
            "policy": rule["policy"],
            "priority": "low",
            "reason": rule["reason"],
        }

    if title in LOW_PRIORITY_SIGNATURES:
        return {
            "policy": "keep",
            "priority": "low",
            "reason": (
                "Informational activity worth retaining but not "
                "necessarily requiring immediate attention."
            ),
        }

    return {
        "policy": "keep",
        "priority": "normal",
        "reason": (
            "No noise-reduction rule currently applies to this alert."
        ),
    }


def apply_noise_reduction(
    alert,
    repeat_count=1
):
    """
    Add noise-reduction metadata to an alert.

    This does not delete or suppress the original event.
    """

    classification = classify_alert(
        alert
    )

    enriched_alert = dict(
        alert
    )

    enriched_alert["noise_reduction"] = {
        "policy": classification["policy"],
        "priority": classification["priority"],
        "reason": classification["reason"],
        "repeat_count": repeat_count,
        "is_repetitive": repeat_count > 1,
    }

    return enriched_alert