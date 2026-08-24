#!/bin/bash

set -e

VALIDATE_ONLY=false

if [ "$1" = "--validate" ]; then
    VALIDATE_ONLY=true
fi

echo

if [ -f "assets/logo-ascii.txt" ]; then
    cat assets/logo-ascii.txt
    echo
fi

echo "        NETWORK SENTINEL"
echo "        Sentinel Node Installer"
echo

# Make sure script is being run from the Sentinel-Node directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: Run this installer from the Sentinel-Node directory."
    exit 1
fi

# Verify Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker is not installed."
    exit 1
fi

# Verify Docker Compose
if ! docker compose version >/dev/null 2>&1; then
    echo "ERROR: Docker Compose is not available."
    exit 1
fi

# Create runtime directories
echo "Creating runtime directories..."

mkdir -p logs
mkdir -p secrets/alloy
mkdir -p secrets/tls

# Create .env from template if it does not exist
if [ ! -f ".env" ]; then
    cp .env.example .env

    echo
    echo "A new .env file was created."
    echo "IMPORTANT: Edit .env with the correct customer and network settings."
    echo
    echo "Available network interfaces:"
    ip -br link
    echo
    echo "Then run the installer again."
    exit 0
fi

# Verify required secret files
if [ ! -f "secrets/alloy/telemetry-token" ]; then
    echo "ERROR: Missing secrets/alloy/telemetry-token"
    exit 1
fi

if [ ! -f "secrets/tls/telemetry.crt" ]; then
    echo "ERROR: Missing secrets/tls/telemetry.crt"
    exit 1
fi

# Validate Docker Compose
echo "Validating Sentinel Node configuration..."

docker compose config >/dev/null

# Stop here when running validation-only mode
if [ "$VALIDATE_ONLY" = true ]; then
    echo
    echo "======================================"
    echo " Sentinel Node validation passed"
    echo "======================================"
    echo
    echo "No containers were started."
    exit 0
fi

# Pull container images
echo "Downloading required container images..."

docker compose pull

# Start Sentinel Node
echo "Starting Network Sentinel Node..."

docker compose up -d

echo
echo "======================================"
echo " Sentinel Node installation complete"
echo "======================================"
echo
echo "Run:"
echo "  ./scripts/health-check.sh"
echo
echo "to verify node health."#!/bin/bash

set -e

VALIDATE_ONLY=false

if [ "$1" = "--validate" ]; then
    VALIDATE_ONLY=true
fi

echo

if [ -f "assets/logo-ascii.txt" ]; then
    cat assets/logo-ascii.txt
    echo
fi

echo "        NETWORK SENTINEL"
echo "        Sentinel Node Installer"
echo

# Make sure script is being run from the Sentinel-Node directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: Run this installer from the Sentinel-Node directory."
    exit 1
fi

# Verify Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker is not installed."
    exit 1
fi

# Verify Docker Compose
if ! docker compose version >/dev/null 2>&1; then
    echo "ERROR: Docker Compose is not available."
    exit 1
fi

# Create runtime directories
echo "Creating runtime directories..."

mkdir -p logs
mkdir -p secrets/alloy
mkdir -p secrets/tls

# Create .env from template if it does not exist
if [ ! -f ".env" ]; then
    cp .env.example .env

    echo
    echo "A new .env file was created."
    echo "IMPORTANT: Edit .env with the correct customer and network settings."
    echo
    echo "Available network interfaces:"
    ip -br link
    echo
    echo "Then run the installer again."
    exit 0
fi

# Verify required secret files
if [ ! -f "secrets/alloy/telemetry-token" ]; then
    echo "ERROR: Missing secrets/alloy/telemetry-token"
    exit 1
fi

if [ ! -f "secrets/tls/telemetry.crt" ]; then
    echo "ERROR: Missing secrets/tls/telemetry.crt"
    exit 1
fi

# Validate Docker Compose
echo "Validating Sentinel Node configuration..."

docker compose config >/dev/null

# Stop here when running validation-only mode
if [ "$VALIDATE_ONLY" = true ]; then
    echo
    echo "======================================"
    echo " Sentinel Node validation passed"
    echo "======================================"
    echo
    echo "No containers were started."
    exit 0
fi

# Pull container images
echo "Downloading required container images..."

docker compose pull

# Start Sentinel Node
echo "Starting Network Sentinel Node..."

docker compose up -d

echo
echo "======================================"
echo " Sentinel Node installation complete"
echo "======================================"
echo
echo "Run:"
echo "  ./scripts/health-check.sh"
echo
echo "to verify node health."