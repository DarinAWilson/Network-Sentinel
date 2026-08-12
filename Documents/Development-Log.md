# Development Log

---

## 2026-06-25

### Architectural Decision #1

Network Sentinel will be developed as a cohesive platform rather than a collection of independent Docker containers.

#### Reasoning

The objective is to create a unified user experience similar to platforms such as TrueNAS, Proxmox, or pfSense. Rather than exposing users to individual tools, Network Sentinel will present them through a centralized portal.

---

### Future Considerations

- Custom branding
- Landing page
- AI integration workflow

---

## 2026-07-06

### Logging Pipeline Milestone

Successfully deployed Grafana Loki and Promtail as the centralized log collection pipeline for Network Sentinel.

#### Accomplishments

- Deployed Loki using Docker Compose.
- Deployed Promtail using Docker Compose.
- Established the logging pipeline between Suricata and Grafana.
- Confirmed both services were running successfully.

#### Technical Challenges and Resolution

Docker image downloads repeatedly failed when pulling larger container images from Docker Hub due to intermittent IPv6 connectivity issues during downloads from Docker's content delivery network (CDN). After updating the Docker daemon configuration and restarting the Docker service, image downloads completed successfully. This issue was documented for future troubleshooting and deployment reference.

#### Design Decision

Rather than rebuilding the existing monitoring stack, the logging components were deployed alongside the current Grafana environment. This approach reduced risk while allowing new functionality to be added incrementally. A unified Docker Compose deployment will be completed later in the project after all components have been validated.

#### Next Steps

- Verify Suricata log ingestion into Loki.
- Configure Grafana to use Loki as a data source.
- Create the first Network Sentinel security dashboard.

---

## 2026-07-07

### Suricata Log Visualization Milestone

Successfully verified end-to-end ingestion of Suricata IDS events through the Network Sentinel logging pipeline.

#### Accomplishments

- Confirmed Promtail successfully collected Suricata eve.json logs.
- Verified Loki was receiving and indexing Suricata security events.
- Connected Grafana to Loki as a log visualization source.
- Successfully queried Suricata events using LogQL.

#### Validation

The query `{job="suricata"}` successfully returned Suricata events containing security telemetry such as event types and system statistics.

#### Result

Network Sentinel now supports centralized security event collection and visualization. The next phase will focus on transforming raw IDS logs into security dashboards and actionable alert views.

---

---

## 2026-07-28

### Security Overview Dashboard Milestone

Completed the initial Security Overview dashboard for Network Sentinel, providing a centralized view of network security events and activity.

#### Accomplishments

- Created the Security Events Timeline panel to visualize security activity over time.
- Added an Alerts (24 Hours) panel to summarize detected security alerts.
- Created the Security Event Summary panel to categorize network activity.
- Added the Most Active Devices panel to identify systems generating the highest number of security events.
- Redesigned the Recent Security Activity panel using user-friendly event names instead of raw Suricata alert signatures.
- Implemented LogQL transformations to translate Suricata alert signatures into simplified Network Sentinel event descriptions.
- Added risk level translation from Suricata severity values into user-friendly High, Medium, and Low risk classifications.
- Added dashboard and panel descriptions to improve usability and documentation.
- Updated project screenshots for GitHub and project documentation.

#### Design Decision

The Security Overview dashboard was designed to present security information in terminology that is understandable to small business administrators and advanced home users. Instead of displaying raw intrusion detection signatures, Network Sentinel translates security events into meaningful descriptions while preserving the underlying technical information for analysis. This approach aligns with the project's goal of making security monitoring more accessible to users without requiring advanced cybersecurity knowledge.

#### Validation

Successfully generated Suricata alerts using network scanning and verified that:

- Promtail successfully collected new Suricata events.
- Loki indexed the collected security events.
- Grafana displayed live security events through LogQL queries.
- User-friendly event names and risk levels were translated correctly.
- Dashboard panels updated automatically as new security events were generated.
- Event summaries and device activity reflected current network activity.

#### Result

Network Sentinel now provides a polished Security Overview dashboard that summarizes network activity, visualizes security trends, highlights the most active devices, and presents security alerts using clear, user-friendly terminology. This milestone establishes the foundation for the upcoming AI-assisted alert explanation feature, which will provide users with plain-language explanations and recommended actions for detected security events.

#### Next Steps

- Develop the AI-assisted alert explanation feature.
- Continue refining dashboard visualizations and user experience.
- Integrate AI-generated explanations into the Security Overview dashboard.
- Begin completing the remaining capstone documentation and deployment guides.

---

## 2026-08-01

### AI Security Assistant and Portal Enhancement Milestone

Completed the first working prototype of the Network Sentinel AI Security Assistant and enhanced the web portal to provide centralized access to project dashboards and security analysis.

#### Accomplishments

- Developed the AI Security Assistant web interface using HTML, CSS, and JavaScript.
- Implemented interactive security event selection with AI-generated explanations.
- Added user-friendly explanations, risk levels, investigation guidance, and recommended actions for supported security events.
- Implemented a Copy Explanation feature to simplify sharing and documentation.
- Redesigned the AI Assistant interface to match the overall Network Sentinel branding and visual style.
- Updated the Network Sentinel Portal to provide working navigation buttons for:
  - Security Overview Dashboard
  - System Health Dashboard
  - Uptime Kuma
  - AI Security Assistant
- Added navigation back to the Network Sentinel home page by making the project logo clickable.
- Updated project documentation and screenshots to reflect the latest application interface.

#### Design Decision

The AI Security Assistant was intentionally implemented as a prototype using predefined explanations instead of a live AI service. This approach demonstrates the intended user experience while keeping the project achievable within the capstone timeline. The interface was designed so that a future AI model can replace the static explanations with minimal changes to the front-end.

#### Validation

Successfully verified that:

- All portal navigation buttons open the correct application pages.
- Dashboard navigation works correctly.
- The AI Security Assistant generates explanations for all supported security events.
- Copy Explanation successfully copies generated analysis.
- Navigation between the portal and AI Assistant functions correctly.

#### Next Steps

- Integrate live security events from Grafana/Loki into the AI Security Assistant.
- Allow users to analyze actual detected security alerts instead of selecting predefined events.
- Complete final testing and demonstration materials.

## 2026-08-10

### Live Security Alert Integration and Backend Analysis Milestone

Completed the integration of live Suricata security alerts into the Network Sentinel AI Security Assistant. The portal can now retrieve actual security events from Loki through the Flask backend and provide plain-English security analysis and recommended actions.

#### Accomplishments

- Added the Python `requests` library to support communication between the Flask backend and Loki.
- Replaced placeholder alert data in the AI backend with live queries to the Loki HTTP API.
- Implemented Loki `query_range` requests to retrieve the most recent Suricata security alert.
- Configured the AI backend to communicate with Loki through the existing `network-sentinel` Docker network.
- Parsed live Suricata alert data including:
  - Alert signature
  - Severity and risk level
  - Source IP address
  - Destination IP address
- Added the `/api/analyze-latest` Flask endpoint for analyzing the latest detected security event.
- Expanded the security explanation engine to provide:
  - Plain-English security analysis
  - Risk information
  - Explanation of why the event matters
  - Recommended investigation actions
- Updated the AI Assistant interface to retrieve and display live security alerts.
- Connected the **Analyze Latest Alert** button to the backend analysis API.
- Maintained the **Copy Explanation** feature for sharing or documenting analysis results.
- Sanitized the public GitHub configuration by replacing the internal Server02 address with a `YOUR_SERVER_IP` placeholder.

#### Design Decisions

The final capstone prototype uses a rule-based security explanation engine rather than relying on an external generative AI service. This approach provides consistent and reliable security explanations while avoiding external API dependencies during the final demonstration. The Flask backend and modular `ai_engine.py` design allow a generative AI service or local language model to replace or extend the current explanation engine in a future version.

The AI backend was also connected to Loki through the dedicated `network-sentinel` Docker network rather than communicating through a hardcoded host address. This keeps internal container communication isolated and makes the Docker architecture more portable and reproducible.

#### Troubleshooting and Validation

During integration, the AI backend initially could not resolve the Loki hostname because the containers were running on separate Docker networks. The issue was identified through Flask container logs and resolved by attaching the AI backend to the existing `network-sentinel` Docker network.

Successfully verified that:

- Loki returns live Suricata security events through its API.
- The Flask backend retrieves the latest real Suricata alert.
- Suricata severity values are translated into user-friendly risk levels.
- The `/api/latest-alert` endpoint returns live alert information.
- The `/api/analyze-latest` endpoint returns a structured security explanation.
- The Network Sentinel portal displays the latest real security alert.
- **Analyze Latest Alert** provides analysis and recommended actions for the live event.
- The frontend communicates successfully with the Flask backend.
- GitHub contains a sanitized server configuration rather than the private Server02 IP address.

#### Next Steps

- Perform final end-to-end functional testing.
- Verify multiple Suricata alert types and security explanations.
- Verify the **Copy Explanation** feature.
- Capture final screenshots and demonstration evidence.
- Complete administrator handoff documentation.
- Prepare the final stakeholder presentation and audio transcript.

## 2026-08-12

### Final Integration Testing and Suricata Logging Repair

Performed final end-to-end testing of the Network Sentinel monitoring and AI Security Assistant pipeline in preparation for the final stakeholder presentation.

#### Final Testing

Verified the operation of the Network Sentinel security monitoring pipeline:

- Confirmed all major Docker containers were running successfully.
- Verified Suricata was actively monitoring the Server02 network interface.
- Verified the Flask AI backend remained operational after extended runtime.
- Tested the `/api/latest-alert` endpoint.
- Tested the `/api/analyze-latest` endpoint.
- Verified live Suricata security events could be retrieved through Loki.
- Verified the AI Security Assistant displayed current security events.
- Verified the AI explanation engine generated:
  - Security analysis
  - Risk level
  - Source and destination information
  - Explanation of why the event matters
  - Recommended investigation actions
  - Network Sentinel recommendation
- Verified the Copy Explanation feature successfully copied generated security analysis.

#### Issue Identified During Testing

Final testing identified a broken Suricata logging path caused by an older Suricata deployment referencing the previous lowercase `network-sentinel` directory.

The running Suricata and Promtail containers were configured to use:

`/home/daw/network-sentinel/suricata/logs`

The active project repository is located at:

`/home/daw/Network-Sentinel`

Because the old directory had been removed during project cleanup, Suricata could no longer provide new log data to Promtail. Previously collected alerts remained available in Loki, but new alerts were no longer entering the monitoring pipeline.

#### Resolution

Reconstructed the Suricata deployment inside the active Network Sentinel project using the configuration recovered from the existing Docker container.

Created a permanent Suricata deployment under:

`Network-Sentinel/Docker/suricata/`

The reconstructed deployment retained:

- Suricata 7.0
- Host network mode
- Monitoring of the `wlp2s0` network interface
- Required Linux networking capabilities
- Persistent configuration and log directories
- Automatic container restart policy

Updated the Promtail Docker configuration to read Suricata logs from the new permanent location.

Successfully verified that Promtail detected and began monitoring the new `eve.json` file.

#### End-to-End Validation

After completing the repair, Network Sentinel successfully detected and processed new live security events.

The validated data flow was:

`Network Traffic → Suricata → eve.json → Promtail → Loki → Flask API → AI Security Assistant`

A new Suricata HTTP security event was successfully displayed by the Network Sentinel portal and processed by the AI explanation engine.

This confirmed that the complete monitoring and security analysis pipeline was operational following the final configuration repair.

#### Final Status

The core Network Sentinel prototype is functionally complete and ready for final presentation preparation.

Remaining project activities include:

- Final dashboard and navigation verification
- Capture final presentation screenshots
- Complete administrator documentation
- Prepare the stakeholder PowerPoint presentation
- Prepare and record the presentation transcript and narration