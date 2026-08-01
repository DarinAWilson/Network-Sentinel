document.getElementById("explainButton").addEventListener("click", function () {

    const event = document.getElementById("eventSelect").value;
    const output = document.getElementById("aiOutput");

    let explanation = "";

    switch (event) {

        case "Network Scan Detected":
            explanation = `
                <h3>🔍 Network Scan Detected</h3>

                <p><strong>🔴 Risk Level:</strong> High</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                A device on your network appears to be scanning another system
                to discover open ports and services. This activity is commonly
                performed during network administration but may also represent
                the reconnaissance phase of a cyberattack.
                </p>

                <h4>⚠️ Why This Matters</h4>

                <p>
                Attackers frequently perform network scans before attempting to
                exploit vulnerable services. Unexpected scans should always be
                reviewed to determine whether they were authorized.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Verify the source device is trusted.</li>
                    <li>Confirm the scan was authorized.</li>
                    <li>Review firewall and IDS logs.</li>
                    <li>Continue monitoring for additional activity.</li>
                </ul>

                <hr>

                <p><strong>🛡 Network Sentinel Recommendation</strong></p>

                <p>
                If this activity originated from an unknown device, investigate
                immediately and monitor for additional reconnaissance attempts.
                </p>
            `;
            break;

        case "Malformed HTTP Request":
            explanation = `
                <h3>🌐 Malformed HTTP Request</h3>

                <p><strong>🟡 Risk Level:</strong> Medium</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                An HTTP request was received that did not follow expected
                protocol standards. This may be caused by vulnerability scanners,
                misconfigured software, or intentionally malformed traffic.
                </p>

                <h4>⚠️ Why This Matters</h4>

                <p>
                Repeated malformed requests may indicate reconnaissance or an
                attempt to identify vulnerable web services.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Review the source device.</li>
                    <li>Check web server logs.</li>
                    <li>Monitor for repeated requests.</li>
                </ul>
            `;
            break;

        case "HTTP Communication Error":
            explanation = `
                <h3>🌐 HTTP Communication Error</h3>

                <p><strong>🟢 Risk Level:</strong> Low</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                Network Sentinel detected an unexpected HTTP communication
                issue. Most occurrences are caused by configuration problems,
                interrupted connections, or temporary service issues.
                </p>

                <h4>⚠️ Why This Matters</h4>

                <p>
                Although usually benign, repeated communication errors may
                indicate a larger application or network problem.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Verify the web service is available.</li>
                    <li>Review application logs.</li>
                    <li>Continue monitoring for recurring issues.</li>
                </ul>
            `;
            break;

        case "Protocol Communication Issue":
            explanation = `
                <h3>🔄 Protocol Communication Issue</h3>

                <p><strong>🟡 Risk Level:</strong> Medium</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                A protocol conversation did not complete normally. This may
                indicate malformed traffic, software compatibility problems,
                or network scanning activity.
                </p>

                <h4>⚠️ Why This Matters</h4>

                <p>
                Frequent protocol anomalies can indicate communication issues
                or attempts to bypass normal protocol behavior.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Review the affected systems.</li>
                    <li>Check recent network activity.</li>
                    <li>Investigate repeated occurrences.</li>
                </ul>
            `;
            break;

        case "DNS Activity":
            explanation = `
                <h3>🌍 DNS Activity</h3>

                <p><strong>🟢 Risk Level:</strong> Informational</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                DNS traffic was detected on the network. DNS requests are
                normally generated whenever devices resolve hostnames into
                IP addresses.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>No immediate action is required.</li>
                    <li>Monitor for unusually large volumes of DNS traffic.</li>
                </ul>
            `;
            break;

        case "SSH Activity":
            explanation = `
                <h3>🔐 SSH Activity</h3>

                <p><strong>🟢 Risk Level:</strong> Informational</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                Secure Shell (SSH) traffic was detected. SSH is commonly used
                for secure remote administration of Linux systems.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Verify the connection is expected.</li>
                    <li>Review authentication logs if necessary.</li>
                </ul>
            `;
            break;

        case "SMB Activity":
            explanation = `
                <h3>📁 SMB Activity</h3>

                <p><strong>🟢 Risk Level:</strong> Informational</p>

                <h4>🤖 AI Analysis</h4>

                <p>
                SMB traffic was detected. SMB is commonly used for Windows
                file sharing, printer access, and network authentication.
                </p>

                <h4>✅ Recommended Actions</h4>

                <ul>
                    <li>Verify expected file sharing activity.</li>
                    <li>Monitor for unusual SMB traffic patterns.</li>
                </ul>
            `;
            break;

    }

    output.innerHTML = explanation;

});

document.getElementById("copyButton").addEventListener("click", function () {

    navigator.clipboard.writeText(
        document.getElementById("aiOutput").innerText
    );

    alert("AI explanation copied to clipboard.");

});