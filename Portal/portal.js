// Network Sentinel Customer Portal

//const API_BASE_URL =
    //`${window.location.protocol}//${window.location.hostname}:5000`;
// Network Sentinel Customer Portal

const API_BASE_URL = "http://SERVER_IP:5000";

function getFriendlyAlertTitle(title) {
    const rawTitle = (title || "").toLowerCase();

    if (rawTitle.includes("applayer detect protocol only one direction")) {
        return "One-Way Network Communication Detected";
    }

    if (rawTitle.includes("cloudflare dns over https")) {
        return "Encrypted DNS Activity Detected";
    }

    if (rawTitle.includes("nmap")) {
        return "Network Scan Detected";
    }

    if (rawTitle.includes("malformed http")) {
        return "Unusual Web Traffic Detected";
    }

    if (rawTitle.includes("unable to match response to request")) {
        return "Web Communication Issue Detected";
    }

    if (rawTitle.includes("invalid timestamp")) {
        return "Unusual Network Packet Timing Detected";
    }

    return title || "Security Event Detected";
}

function getRiskClass(risk) {
    switch ((risk || "").toLowerCase()) {
        case "high":
            return "risk-high";

        case "medium":
            return "risk-medium";

        case "low":
            return "risk-low";

        default:
            return "risk-unknown";
    }
}

function updateSecurityStatus(risk) {
    const badge = document.getElementById("securityStatusBadge");
    const title = document.getElementById("securityStatusTitle");
    const message = document.getElementById("securityStatusMessage");

    badge.className = "status-badge";

    switch ((risk || "").toLowerCase()) {
        case "high":
            badge.classList.add("status-danger");
            badge.textContent = "Attention";
            title.textContent = "A high-risk security event was detected";
            message.textContent =
                "Network Sentinel detected activity that should be reviewed promptly.";
            break;

        case "medium":
            badge.classList.add("status-warning");
            badge.textContent = "Review";
            title.textContent = "Security activity needs review";
            message.textContent =
                "Network Sentinel detected activity that may require investigation.";
            break;

        case "low":
            badge.classList.add("status-good");
            badge.textContent = "Monitoring";
            title.textContent = "No urgent threats detected";
            message.textContent =
                "Network Sentinel is actively monitoring your network. The latest event is low risk.";
            break;

        default:
            badge.classList.add("status-loading");
            badge.textContent = "Unknown";
            title.textContent = "Security status unavailable";
            message.textContent =
                "Network Sentinel could not determine the current security status.";
    }
}

fetch(`${API_BASE_URL}/api/latest-alert`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Unable to retrieve latest security event.");
        }

        return response.json();
    })
    .then(data => {
        const riskBadge = document.getElementById("riskBadge");

        document.getElementById("latestEventTitle").textContent =
            getFriendlyAlertTitle(data.title);

        document.getElementById("latestEventSummary").textContent =
            "Network Sentinel detected this activity during network monitoring.";

        document.getElementById("eventSource").textContent =
            data.source || "Unknown";

        document.getElementById("eventTarget").textContent =
            data.target || "Unknown";

        riskBadge.textContent = data.risk || "Unknown";
        riskBadge.className =
            `risk-badge ${getRiskClass(data.risk)}`;

        updateSecurityStatus(data.risk);
    })
    .catch(error => {
        console.error("Network Sentinel portal error:", error);

        document.getElementById("latestEventTitle").textContent =
            "Unable to retrieve the latest security event";

        document.getElementById("latestEventSummary").textContent =
            "The monitoring service could not be reached.";

        document.getElementById("riskBadge").textContent =
            "Unavailable";

        document.getElementById("riskBadge").className =
            "risk-badge risk-unknown";

        updateSecurityStatus(null);
    });