#!/bin/bash
echo "🤖 DEVOPS AI MONITOR - MAIN CONTROL PANEL"
echo "================================================"
echo "Version: 2.1 | $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. SERVICE CHECK
echo "🔌 SERVICE STATUS:"
echo "-------------------"
check_service() {
    local name=$1 url=$2
    if curl -s --max-time 3 "$url" >/dev/null; then
        echo "   • $name: ✅ AVAILABLE"
        return 0
    else
        echo "   • $name: ❌ UNAVAILABLE"
        return 1
    fi
}

check_service "Application" "http://localhost:5000/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Loki" "http://localhost:3100/ready"
check_service "Grafana" "http://localhost:3000/api/health"

# 2. CONTAINERS
echo ""
echo "🐳 CONTAINERS:"
echo "--------------"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(prometheus|devops_app|loki|promtail|grafana|node-exporter|cadvisor)"

# 3. BUSINESS METRICS
echo ""
echo "📊 BUSINESS ACTIVITY:"
echo "---------------------"
business_data=$(curl -s "http://localhost:9090/api/v1/query?query=app_business_requests_total")
if echo "$business_data" | grep -q '"result":'; then
    echo "$business_data" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        total = sum(int(r['value'][1]) for r in data['data']['result'])
        print(f'   • Business requests: {total}')
        for result in data['data']['result']:
            request_type = result['metric'].get('request_type', 'unknown')
            count = result['value'][1]
            print(f'     - {request_type}: {count}')
    else:
        print('   • Business activity: 📊 waiting for data')
except Exception as e:
    print('   • Business activity: 🔄 data not ready yet')
"
else
    echo "   • Business activity: 🔄 waiting for Prometheus data"
fi

# 4. SYSTEM RESOURCES
echo ""
echo "🖥️  SYSTEM RESOURCES:"
echo "----------------------"
memory_data=$(curl -s "http://localhost:9090/api/v1/query?query=node_memory_MemTotal_bytes")
if echo "$memory_data" | grep -q '"result":'; then
    echo "$memory_data" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        total_bytes = int(data['data']['result'][0]['value'][1])
        print(f'   • Memory: {total_bytes / 1024/1024/1024:.1f} GB total')
    else:
        print('   • Memory: 🔄 collecting data')
except Exception as e:
    print('   • Memory: 🔄 processing data...')
"
else
    echo "   • Memory: 🔄 waiting for node-exporter data"
fi

# 5. SUMMARY
echo ""
echo "🎯 SUMMARY:"
echo "----------"
app_status=$(curl -s --max-time 2 http://localhost:5000/health >/dev/null && echo -n "✅ " || echo -n "❌ ")
prom_status=$(curl -s --max-time 2 http://localhost:9090/-/healthy >/dev/null && echo -n "✅ " || echo -n "❌ ")
loki_status=$(curl -s --max-time 2 http://localhost:3100/ready >/dev/null && echo -n "✅ " || echo -n "❌ ")
grafana_status=$(curl -s --max-time 2 http://localhost:3000/api/health >/dev/null && echo -n "✅" || echo -n "❌")

services="$app_status$prom_status$loki_status$grafana_status"
containers=$(docker ps --filter name=prometheus --filter name=devops_app --filter name=loki --filter name=promtail --filter name=grafana --filter name=node-exporter --filter name=cadvisor | wc -l)
containers=$((containers - 1))

echo "   • Services: $services"
echo "   • Containers: $containers/7"

if [ "$services" = "✅ ✅ ✅ ✅" ]; then
    echo "   • Status: 🟢 SYSTEM OPERATIONAL"
else
    echo "   • Status: 🟡 PARTIALLY OPERATIONAL"
fi

echo ""
echo "🧠 AI BRIDGE INTEGRATION:"
echo "------------------------"
python3 -c "
import sys
import os
sys.path.append(os.getcwd())  # Use getcwd() instead of dot
try:
    from monitoring_bridge import bridge
    
    print('⚡ Quick status via bridge:')
    quick = bridge.get_quick_status()
    print('   • Response time: {}ms'.format(quick['response_time_ms']))
    print('   • Status: {}'.format(quick['status']))
    
    print('📊 Metrics via bridge:')
    metrics = bridge.get_system_metrics()
    if 'output' in metrics:
        lines = metrics['output'].split('\n')
        for line in lines[3:6]:
            if line.strip() and not line.startswith('---'):
                print('   • {}'.format(line))
    
except Exception as e:
    print('   • Bridge temporarily unavailable: {}'.format(e))
"

echo ""
echo "🧠 AI SYSTEM ANALYSIS:"
echo "---------------------"
cd /home/eldorz/devops-ai-monitor

# Quick AI analysis (without detailed report)
python3 -c "
import sys
sys.path.append('.')
try:
    from monitoring_bridge import bridge
    from master_analyzer import MasterAnalyzer
    
    # Quick status via bridge
    quick = bridge.get_quick_status()
    print('⚡ Status: {} ({}ms)'.format(quick['status'], quick['response_time_ms']))
    print('📊 Services: {}/{} | Containers: {}/{}'.format(
        quick['services']['available'], 
        quick['services']['total'],
        quick['containers']['running'], 
        quick['containers']['expected']
    ))
    
    # Quick health analysis
    analyzer = MasterAnalyzer(use_ai=False)
    health = analyzer.analyze_system_health()
    print('💚 Health: {} ({}/100)'.format(health['health_level'], health['health_score']))
    
    # Recommendations based on quick analysis
    if health['health_score'] == 100:
        print('🎯 Recommendation: System perfect - maintain current state')
    elif health['health_score'] >= 80:
        print('🎯 Recommendation: System stable - continue monitoring')
    else:
        print('🎯 Recommendation: Attention required - check services')
        
except Exception as e:
    print('❌ AI analysis temporarily unavailable: {}'.format(str(e)))
"

echo ""
echo "🔧 ADDITIONAL COMMANDS:"
echo "  ./quick_check.sh          - Quick check"
echo "  ./quick_ai_check.sh       - Quick AI analysis"
echo "  ./scripts/metrics_system.sh - Detailed system metrics"
echo "  ./scripts/metrics_containers.sh - Container metrics"
echo "  python3 master_analyzer.py - Full AI report"
echo "  python3 master_analyzer.py --email - Report + email"
echo ""
echo "📁 SCRIPT MANAGER:"
echo "  python3 script_manager.py list    - 📋 All scripts"
echo "  python3 script_manager.py check   - 🔍 Check scripts" 
echo "  python3 script_manager.py fix     - 🔧 Fix scripts"
echo "  python3 script_manager.py find    - 🔍 Search scripts"
echo "  python3 script_manager.py run <script> - 🚀 Run script"
