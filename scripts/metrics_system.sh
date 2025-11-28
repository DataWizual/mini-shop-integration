#!/bin/bash
echo "🖥️  SYSTEM METRICS - ADAPTIVE REPORT"
echo "========================================"

# Service availability check
check_service() {
    curl -s --max-time 3 "$1" >/dev/null 2>&1
}

echo "🔍 MONITORING SERVICES CHECK:"
echo "--------------------------------"

PROMETHEUS_AVAILABLE=0
NODE_EXPORTER_AVAILABLE=0

if check_service "http://localhost:9090/-/healthy"; then
    echo "   • Prometheus: ✅ Running"
    PROMETHEUS_AVAILABLE=1
else
    echo "   • Prometheus: ❌ Not available"
fi

if check_service "http://localhost:9100/metrics"; then
    echo "   • Node Exporter: ✅ Running" 
    NODE_EXPORTER_AVAILABLE=1
else
    echo "   • Node Exporter: ❌ Not available"
fi

echo ""
echo "📊 AVAILABLE SYSTEM DATA:"
echo "------------------------------"

# Basic system information (always available)
echo "💾 BASIC INFORMATION:"
echo "   • Uptime: $(uptime -p 2>/dev/null || echo 'unavailable')"

# Load average - fixed version
LOAD_AVG=$(uptime 2>/dev/null | sed 's/.*load average: //' 2>/dev/null || echo "unavailable")
echo "   • System load: $LOAD_AVG"

# Memory - fixed version
MEM_INFO=$(free -h 2>/dev/null | grep Mem || echo "unavailable")
if [ "$MEM_INFO" != "unavailable" ]; then
    MEM_TOTAL=$(echo "$MEM_INFO" | awk '{print $2}')
    MEM_USED=$(echo "$MEM_INFO" | awk '{print $3}')
    echo "   • Memory: Used $MEM_USED of $MEM_TOTAL"
else
    echo "   • Memory: unavailable"
fi

# If node-exporter is available
if [ $NODE_EXPORTER_AVAILABLE -eq 1 ]; then
    echo ""
    echo "📈 NODE-EXPORTER METRICS:"
    
    # Memory
    MEM_TOTAL=$(curl -s http://localhost:9100/metrics | grep "node_memory_MemTotal_bytes" | head -1 | awk '{print $2}')
    MEM_AVAILABLE=$(curl -s http://localhost:9100/metrics | grep "node_memory_MemAvailable_bytes" | head -1 | awk '{print $2}')
    
    if [ -n "$MEM_TOTAL" ]; then
        MEM_TOTAL_GB=$(echo "scale=1; $MEM_TOTAL / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "?")
        echo "   • Total memory: ${MEM_TOTAL_GB} GB"
        
        if [ -n "$MEM_AVAILABLE" ]; then
            MEM_USED_GB=$(echo "scale=1; ($MEM_TOTAL - $MEM_AVAILABLE) / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "?")
            MEM_USED_PERCENT=$(echo "scale=1; ($MEM_TOTAL - $MEM_AVAILABLE) * 100 / $MEM_TOTAL" | bc 2>/dev/null || echo "?")
            echo "   • Used: ${MEM_USED_GB} GB (${MEM_USED_PERCENT}%)"
        fi
    fi
    
    # Load average
    LOAD1=$(curl -s http://localhost:9100/metrics | grep "^node_load1 " | awk '{print $2}')
    if [ -n "$LOAD1" ]; then
        echo "   • Load average (1min): ${LOAD1}"
    fi
fi

# If Prometheus is available
if [ $PROMETHEUS_AVAILABLE -eq 1 ]; then
    echo ""
    echo "📊 PROMETHEUS METRICS:"
    echo "   • Prometheus collecting data..."
fi

echo ""
echo "🎯 RECOMMENDATIONS:"
echo "----------------"

if [ $NODE_EXPORTER_AVAILABLE -eq 0 ]; then
    echo "   • Start node-exporter: docker-compose up -d node-exporter"
fi

if [ $PROMETHEUS_AVAILABLE -eq 0 ]; then
    echo "   • Start Prometheus: docker-compose up -d prometheus"
fi

if [ $NODE_EXPORTER_AVAILABLE -eq 1 ] && [ $PROMETHEUS_AVAILABLE -eq 1 ]; then
    echo "   • Monitoring system operational ✅"
    echo "   • Full statistics available in 2-5 minutes of data collection"
fi

echo ""
echo "💡 COMMANDS TO START MONITORING:"
echo "  docker-compose up -d node-exporter prometheus cadvisor"