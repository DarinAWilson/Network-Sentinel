# Network Sentinel Node

The Network Sentinel Node is the customer-side component of Network Sentinel.

It passively monitors network traffic using Suricata and forwards security telemetry to the central Network Sentinel platform using Grafana Alloy.

## Components

- Suricata IDS
- Grafana Alloy
- Docker Compose
- Encrypted HTTPS telemetry
- Per-node authentication

## Requirements

- Linux host
- Docker
- Docker Compose
- Supported network interface connected to the monitored network
- Network visibility through a switch mirror/SPAN port or equivalent
- Outbound HTTPS connectivity to the Network Sentinel telemetry gateway

## Installation

1. Copy or clone the Sentinel-Node directory to the target system.

2. Enter the directory:

```bash
cd Sentinel-Node