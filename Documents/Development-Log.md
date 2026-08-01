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