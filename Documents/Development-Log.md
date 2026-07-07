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