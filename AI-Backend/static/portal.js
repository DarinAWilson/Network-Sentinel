// Network Sentinel Customer Portal

const API_BASE_URL = "";

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
            title.textContent =
                "A high-risk security event was detected";
            message.textContent =
                "Network Sentinel detected activity that should be reviewed promptly.";
            break;

        case "medium":
            badge.classList.add("status-warning");
            badge.textContent = "Review";
            title.textContent =
                "Security activity needs review";
            message.textContent =
                "Network Sentinel detected activity that may require investigation.";
            break;

        case "low":
            badge.classList.add("status-good");
            badge.textContent = "Monitoring";
            title.textContent =
                "No urgent threats detected";
            message.textContent =
                "Network Sentinel is actively monitoring your network. The latest event is low risk.";
            break;

        default:
            badge.classList.add("status-loading");
            badge.textContent = "Unknown";
            title.textContent =
                "Security status unavailable";
            message.textContent =
                "Network Sentinel could not determine the current security status.";
    }
}

function getEventSummary(data) {
    const noiseReduction = data.noise_reduction || {};

    const repeatCount = Number(
        noiseReduction.repeat_count || 1
    );

    const isRepetitive =
        noiseReduction.is_repetitive === true &&
        repeatCount > 1;

    if (isRepetitive) {
        return (
            `Network Sentinel detected this activity ` +
            `${repeatCount} times in the last hour. ` +
            `Repeated events are grouped to reduce alert noise.`
        );
    }

    return (
        "Network Sentinel detected this activity during network monitoring."
    );
}

function updateMonitoringHealth(data) {
    const badge = document.getElementById(
        "monitoringHealthBadge"
    );

    const message = document.getElementById(
        "monitoringHealthMessage"
    );

    const backendHealth = document.getElementById(
        "backendHealth"
    );

    const telemetryHealth = document.getElementById(
        "telemetryHealth"
    );

    const lokiHealth = document.getElementById(
        "lokiHealth"
    );

    const healthWindow = document.getElementById(
        "healthWindow"
    );

    badge.className = "status-badge";

    switch ((data.status || "").toLowerCase()) {
        case "healthy":
            badge.classList.add("status-good");
            badge.textContent = "Healthy";
            message.textContent =
                "Network Sentinel is operating normally and receiving recent monitoring data.";
            break;

        case "degraded":
            badge.classList.add("status-warning");
            badge.textContent = "Degraded";
            message.textContent =
                "Network Sentinel is online, but recent monitoring data has not been detected.";
            break;

        default:
            badge.classList.add("status-danger");
            badge.textContent = "Offline";
            message.textContent =
                "Network Sentinel cannot currently confirm that monitoring services are operating normally.";
    }

    backendHealth.textContent =
        data.backend === true
            ? "Online"
            : "Unavailable";

    telemetryHealth.textContent =
        data.recent_telemetry === true
            ? "Receiving data"
            : "No recent data";

    lokiHealth.textContent =
        data.loki === true
            ? "Available"
            : "Unavailable";

    if (data.telemetry_window_minutes) {
        healthWindow.textContent =
            `Telemetry health is based on activity received within the last ` +
            `${data.telemetry_window_minutes} minutes.`;
    } else {
        healthWindow.textContent = "";
    }
}

function setMonitoringHealthUnavailable() {
    const badge = document.getElementById(
        "monitoringHealthBadge"
    );

    badge.className =
        "status-badge status-danger";

    badge.textContent =
        "Unavailable";

    document.getElementById(
        "monitoringHealthMessage"
    ).textContent =
        "Network Sentinel could not retrieve monitoring health information.";

    document.getElementById(
        "backendHealth"
    ).textContent =
        "Unknown";

    document.getElementById(
        "telemetryHealth"
    ).textContent =
        "Unknown";

    document.getElementById(
        "lokiHealth"
    ).textContent =
        "Unknown";

    document.getElementById(
        "healthWindow"
    ).textContent = "";
}


// =====================================================
// Monitoring Health
// =====================================================

fetch(`${API_BASE_URL}/api/health`)
    .then(response => {
        if (!response.ok) {
            throw new Error(
                "Unable to retrieve monitoring health."
            );
        }

        return response.json();
    })
    .then(data => {
        updateMonitoringHealth(data);
    })
    .catch(error => {
        console.error(
            "Network Sentinel health error:",
            error
        );

        setMonitoringHealthUnavailable();
    });


// =====================================================
// Latest Security Event
// =====================================================

fetch(`${API_BASE_URL}/api/latest-alert`)
    .then(response => {
        if (!response.ok) {
            throw new Error(
                "Unable to retrieve latest security event."
            );
        }

        return response.json();
    })
    .then(data => {
        const riskBadge =
            document.getElementById("riskBadge");

        document.getElementById(
            "latestEventTitle"
        ).textContent =
            getFriendlyAlertTitle(data.title);

        document.getElementById(
            "latestEventSummary"
        ).textContent =
            getEventSummary(data);

        document.getElementById(
            "eventSource"
        ).textContent =
            data.source || "Unknown";

        document.getElementById(
            "eventTarget"
        ).textContent =
            data.target || "Unknown";

        riskBadge.textContent =
            data.risk || "Unknown";

        riskBadge.className =
            `risk-badge ${getRiskClass(data.risk)}`;

        updateSecurityStatus(
            data.risk
        );
    })
    .catch(error => {
        console.error(
            "Network Sentinel portal error:",
            error
        );

        document.getElementById(
            "latestEventTitle"
        ).textContent =
            "Unable to retrieve the latest security event";

        document.getElementById(
            "latestEventSummary"
        ).textContent =
            "The monitoring service could not be reached.";

        document.getElementById(
            "riskBadge"
        ).textContent =
            "Unavailable";

        document.getElementById(
            "riskBadge"
        ).className =
            "risk-badge risk-unknown";

        updateSecurityStatus(null);
    });