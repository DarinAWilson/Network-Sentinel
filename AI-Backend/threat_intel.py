import ipaddress
import os


THREAT_LIST_PATH = os.getenv(
    "THREAT_LIST_PATH",
    "/app/data/spamhaus_drop.txt"
)


def load_threat_networks():
    """
    Load malicious IP networks from the local Spamhaus DROP file.
    """

    networks = []

    if not os.path.exists(THREAT_LIST_PATH):
        return networks

    with open(THREAT_LIST_PATH, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith(";"):
                continue

            cidr = line.split(";", 1)[0].strip()

            try:
                networks.append(
                    ipaddress.ip_network(cidr, strict=False)
                )
            except ValueError:
                continue

    return networks


def check_ip_reputation(ip_address, threat_networks):
    """
    Check whether an IP belongs to a known malicious network.
    """

    try:
        ip = ipaddress.ip_address(ip_address)
    except ValueError:
        return {
            "checked": False,
            "malicious": False,
            "matched_network": None
        }

    for network in threat_networks:
        if ip in network:
            return {
                "checked": True,
                "malicious": True,
                "matched_network": str(network)
            }

    return {
        "checked": True,
        "malicious": False,
        "matched_network": None
    }


def enrich_alert(alert):
    """
    Add threat-intelligence reputation results to an alert.
    """

    threat_networks = load_threat_networks()

    source_ip = alert.get("source")
    target_ip = alert.get("target")

    source_reputation = check_ip_reputation(
        source_ip,
        threat_networks
    )

    target_reputation = check_ip_reputation(
        target_ip,
        threat_networks
    )

    enriched_alert = dict(alert)

    enriched_alert["threat_intel"] = {
        "source": source_reputation,
        "target": target_reputation,
        "known_bad_match": (
            source_reputation["malicious"]
            or target_reputation["malicious"]
        ),
        "source_name": "Spamhaus DROP"
    }

    return enriched_alert