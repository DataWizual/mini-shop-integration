#!/bin/bash
echo "⚡ AI QUICK CHECK - $(date '+%H:%M:%S')"
echo "======================================"

cd /home/eldorz/devops-ai-monitor

python3 -c "
import sys
sys.path.append('.')
try:
    from monitoring_bridge import bridge
    quick = bridge.get_quick_status()
    
    # Color indicators
    if quick['status'] == '🟢 OK':
        status_color='\033[32m'
    elif 'PARTIAL' in quick['status']:
        status_color='\033[33m'
    else:
        status_color='\033[31m'
    
    print('{}🤖 STATUS: {}\033[0m'.format(status_color, quick['status']))
    print('📊 Services: {}/{}'.format(quick['services']['available'], quick['services']['total']))
    print('🐳 Containers: {}/{}'.format(quick['containers']['running'], quick['containers']['expected']))
    print('⚡ Response time: {}ms'.format(quick['response_time_ms']))
    
    # Simple recommendations
    if quick['services']['available'] < quick['services']['total']:
        print('🚨 Action: Check unavailable services')
    elif quick['containers']['running'] < quick['containers']['expected']:
        print('🚨 Action: Restart containers')
    else:
        print('✅ Action: Continue monitoring')
        
except Exception as e:
    print('❌ AI analysis error: {}'.format(str(e)))
"