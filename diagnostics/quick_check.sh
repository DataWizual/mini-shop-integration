#!/bin/bash
set -e

echo "⚡ QUICK CHECK - $(date '+%H:%M:%S')"
echo "======================================"

# Super-fast check (only critical)
services=0
curl -s --max-time 2 http://localhost:5000/health >/dev/null && services=$((services + 1))
curl -s --max-time 2 http://localhost:9090/-/healthy >/dev/null && services=$((services + 1))
curl -s --max-time 2 http://localhost:3100/ready >/dev/null && services=$((services + 1))
curl -s --max-time 2 http://localhost:3000/api/health >/dev/null && services=$((services + 1))

containers=$(docker ps --filter "name=prometheus|devops_app|grafana|loki" --quiet | wc -l)

echo "Services: $services/4 ✅"
echo "Containers: $containers/4 🐳"

if [ $services -eq 4 ] && [ $containers -eq 4 ]; then
    echo "Status: 🟢 OK"
elif [ $services -ge 2 ]; then
    echo "Status: 🟡 PARTIAL"
else
    echo "Status: 🔴 CRITICAL"
fi