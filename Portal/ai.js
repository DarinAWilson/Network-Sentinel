// Stores the latest alert returned from the backend
let latestAlert = null;

// Network Sentinel AI Backend
// Replace SERVER_IP with the IP address of the Network Sentinel server.
const API_BASE_URL = "http://SERVER_IP:5000";


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
            <h3>🔎 ${data.title}</h3>

            <p><strong>Risk:</strong> ${data.risk}</p>
            <p><strong>Source:</strong> ${data.source}</p>
            <p><strong>Target:</strong> ${data.target}</p>
        `;
    })
    .catch(error => {
        console.error(error);

        document.getElementById("latestAlert").innerHTML = `
            <p><strong>Unable to retrieve the latest security event.</strong></p>
        `;
    });


// Analyze the latest alert
document.getElementById("explainButton").addEventListener("click", function () {

    const output = document.getElementById("aiOutput");

    output.innerHTML = `
        <p><strong>🤖 Network Sentinel is analyzing the latest alert...</strong></p>
    `;

    fetch(`${API_BASE_URL}/api/analyze-latest`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Unable to analyze latest alert.");
            }

            return response.json();
        })
        .then(data => {

            const actions = data.recommended_actions
                .map(action => `<li>${action}</li>`)
                .join("");

            output.innerHTML = `
                <h3>🛡️ ${data.title}</h3>

                <p><strong>Risk Level:</strong> ${data.risk}</p>

                <p>
                    <strong>Source:</strong> ${data.source}<br>
                    <strong>Target:</strong> ${data.target}
                </p>

                <h4>🤖 Security Analysis</h4>
                <p>${data.analysis}</p>

                <h4>⚠️ Why This Matters</h4>
                <p>${data.why_it_matters}</p>

                <h4>✅ Recommended Actions</h4>
                <ul>
                    ${actions}
                </ul>

                <hr>

                <p>
                    <strong>🛡 Network Sentinel Recommendation</strong>
                </p>

                <p>
                    Review this event in context with other recent network
                    activity and investigate further if the activity was
                    unexpected.
                </p>
            `;
        })
        .catch(error => {
            console.error(error);

            output.innerHTML = `
                <p><strong>Unable to analyze the latest security event.</strong></p>
            `;
        });
});


// Copy the explanation to the clipboard
document.getElementById("copyButton").addEventListener("click", function () {

    navigator.clipboard.writeText(
        document.getElementById("aiOutput").innerText
    );

    alert("AI explanation copied to clipboard.");
});