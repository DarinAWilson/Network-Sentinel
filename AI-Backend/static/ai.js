// Stores the latest alert returned from the backend
let latestAlert = null;

// Network Sentinel AI Backend
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


// Retrieve the latest alert when the page loads
fetch(`${API_BASE_URL}/api/latest-alert`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Unable to retrieve latest alert.");
        }

        return response.json();
    })
    .then(data => {
        latestAlert = data;

        document.getElementById("latestAlert").innerHTML = `
            <h3>🔎 ${getFriendlyAlertTitle(data.title)}</h3>

            <p><strong>Risk:</strong> ${data.risk}</p>

            <p>
                <strong>Source:</strong> ${data.source}<br>
                <strong>Target:</strong> ${data.target}
            </p>
        `;
    })
    .catch(error => {
        console.error("Network Sentinel alert retrieval error:", error);

        document.getElementById("latestAlert").innerHTML = `
            <p>
                <strong>Unable to retrieve the latest security event.</strong>
            </p>

            <p>
                The Network Sentinel monitoring service could not be reached.
            </p>
        `;
    });


// Analyze the latest alert
document.getElementById("explainButton").addEventListener("click", function () {

    const output = document.getElementById("aiOutput");
    const button = document.getElementById("explainButton");

    button.disabled = true;
    button.textContent = "Analyzing...";

    output.innerHTML = `
        <p>
            <strong>Network Sentinel is analyzing this security event...</strong>
        </p>
    `;

    fetch(`${API_BASE_URL}/api/analyze-latest`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Unable to analyze latest alert.");
            }

            return response.json();
        })
        .then(data => {

            const actions = Array.isArray(data.recommended_actions)
                ? data.recommended_actions
                    .map(action => `<li>${action}</li>`)
                    .join("")
                : "";

            output.innerHTML = `
                <div class="section-heading">

                    <div>
                        <p class="eyebrow">SECURITY EVENT</p>

                        <h3>
                            ${getFriendlyAlertTitle(data.title)}
                        </h3>
                    </div>

                    <div class="risk-badge risk-${(data.risk || "unknown").toLowerCase()}">
                        ${data.risk || "Unknown"}
                    </div>

                </div>

                <h4>What Happened</h4>

                <p>
                    ${data.analysis}
                </p>

                <h4>Why This Matters</h4>

                <p>
                    ${data.why_it_matters}
                </p>

                <h4>Recommended Next Steps</h4>

                <ul>
                    ${actions}
                </ul>

                <hr>

                <div class="event-details">

                    <div class="event-detail">

                        <span class="detail-label">
                            Source
                        </span>

                        <span>
                            ${data.source || "Unknown"}
                        </span>

                    </div>


                    <div class="event-detail">

                        <span class="detail-label">
                            Target
                        </span>

                        <span>
                            ${data.target || "Unknown"}
                        </span>

                    </div>

                </div>

                <p>
                    <strong>Network Sentinel Guidance</strong>
                </p>

                <p>
                    Review this event alongside other recent network activity.
                    If the behavior is unexpected or continues repeatedly,
                    further investigation may be appropriate.
                </p>
            `;
        })
        .catch(error => {
            console.error("Network Sentinel analysis error:", error);

            output.innerHTML = `
                <p>
                    <strong>
                        Unable to analyze the latest security event.
                    </strong>
                </p>

                <p>
                    The original security event is still available for review.
                </p>
            `;
        })
        .finally(() => {
            button.disabled = false;
            button.textContent = "Explain This Alert";
        });
});

// Copy the explanation to the clipboard
document.getElementById("copyButton").addEventListener("click", async function () {

    const text = document.getElementById("aiOutput").innerText;
    const toast = document.getElementById("copyToast");

    try {

        // Preferred method for HTTPS / secure browser contexts
        if (navigator.clipboard && window.isSecureContext) {

            await navigator.clipboard.writeText(text);

        } else {

            // Fallback for local HTTP deployments
            const textArea = document.createElement("textarea");

            textArea.value = text;

            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            textArea.style.top = "-9999px";

            document.body.appendChild(textArea);

            textArea.focus();
            textArea.select();

            const copied = document.execCommand("copy");

            document.body.removeChild(textArea);

            if (!copied) {
                throw new Error("Fallback copy command failed");
            }
        }

        toast.textContent = "Copied!";
        toast.classList.add("show");

        setTimeout(() => {
            toast.classList.remove("show");
        }, 1500);

    } catch (error) {

        console.error("Clipboard error:", error);

        toast.textContent = "Unable to copy";
        toast.classList.add("show");

        setTimeout(() => {
            toast.classList.remove("show");
            toast.textContent = "Copied!";
        }, 2000);
    }
});