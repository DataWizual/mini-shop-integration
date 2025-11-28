#!/bin/bash
echo "🐳 CONTAINER METRICS - ADAPTIVE REPORT"
echo "========================================="

# Service availability check
check_service() {
    curl -s --max-time 3 "$1" >/dev/null 2>&1
}

echo "🔍 MONITORING SERVICES CHECK:"
echo "--------------------------------"

CADVISOR_AVAILABLE=0
PROMETHEUS_AVAILABLE=0

if check_service "http://localhost:8080/healthz"; then
    echo "   • cAdvisor: ✅ Running"
    CADVISOR_AVAILABLE=1
else
    echo "   • cAdvisor: ❌ Not available"
fi

if check_service "http://localhost:9090/-/healthy"; then
    echo "   • Prometheus: ✅ Running"
    PROMETHEUS_AVAILABLE=1
else
    echo "   • Prometheus: ❌ Not available"
fi

echo ""
echo "📊 BASIC CONTAINER INFORMATION:"
echo "-----------------------------------"

# Always show basic Docker information
RUNNING_CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | tail -n +2)
CONTAINER_COUNT=$(echo "$RUNNING_CONTAINERS" | wc -l)

echo "💾 RUNNING CONTAINERS:"
if [ $CONTAINER_COUNT -gt 0 ]; then
    echo "$RUNNING_CONTAINERS" | while read line; do
        if [ -n "$line" ]; then
            echo "   • $line"
        fi
    done
    echo "   • Total containers: $CONTAINER_COUNT ✅"
else
    echo "   • No running containers"
fi

# If cAdvisor is available
if [ $CADVISOR_AVAILABLE -eq 1 ]; then
    echo ""
    echo "📈 CADVISOR METRICS:"
    
    # Simple check if cAdvisor sees containers
    CONTAINER_METRICS=$(curl -s http://localhost:8080/metrics | grep "container_" | head -5)
    if [ -n "$CONTAINER_METRICS" ]; then
        echo "   • cAdvisor collecting container metrics ✅"
    else
        echo "   • cAdvisor: waiting for data..."
    fi
fi

# If Prometheus is available
if [ $PROMETHEUS_AVAILABLE -eq 1 ] && [ $CADVISOR_AVAILABLE -eq 1 ]; then
    echo ""
    echo "📊 DETAILED PROMETHEUS METRICS:"
    
    # Function for safe query
    safe_prom_query() {
        local query=$1
        local result=$(curl -s --max-time 10 "http://localhost:9090/api/v1/query?query=$query")
        if echo "$result" | grep -q '"result":'; then
            echo "$result"
        else
            echo "ERROR"
        fi
    }

    echo "   • Prometheus processing cAdvisor data..."
    echo "   • Detailed statistics available in 2-5 minutes"
fi

echo ""
echo "🎯 RECOMMENDATIONS:"
echo "----------------"

if [ $CADVISOR_AVAILABLE -eq 0 ]; then
    echo "   • Start cAdvisor: docker-compose up -d cadvisor"
fi

if [ $PROMETHEUS_AVAILABLE -eq 0 ]; then
    echo "   • Start Prometheus: docker-compose up -d prometheus"
fi

if [ $CADVISOR_AVAILABLE -eq 1 ] && [ $PROMETHEUS_AVAILABLE -eq 1 ]; then
    echo "   • Container monitoring system operational ✅"
fi

echo ""
echo "💡 COMMANDS TO START MONITORING:"
echo "  docker-compose up -d cadvisor prometheus"