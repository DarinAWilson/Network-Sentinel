#!/bin/bash

echo "======================================"
echo " Network Sentinel Node Health Check"
echo "======================================"
echo

FAILURES=0

check_container() {
    NAME="$1"

    if docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
        echo "[OK] $NAME is running"
    else
        echo "[FAIL] $NAME is not running"
        FAILURES=$((FAILURES + 1))
    fi
}

check_container "sentinel-suricata"
check_container "sentinel-alloy"

echo

if [ -f "logs/eve.json" ]; then
    echo "[OK] Suricata eve.json exists"

    if [ -s "logs/eve.json" ]; then
        echo "[OK] Suricata eve.json contains data"
    else
        echo "[WARN] Suricata eve.json exists but is empty"
    fi
else
    echo "[FAIL] Suricata eve.json does not exist"
    FAILURES=$((FAILURES + 1))
fi

echo

echo "Recent Alloy errors:"
docker logs sentinel-alloy --since 5m 2>&1 | grep -iE "error|failed|tls|unauthorized" | tail -10

echo

if [ "$FAILURES" -eq 0 ]; then
    echo "======================================"
    echo " Sentinel Node appears healthy"
    echo "======================================"
    exit 0
else
    echo "======================================"
    echo " Sentinel Node has $FAILURES problem(s)"
    echo "======================================"
    exit 1
fi