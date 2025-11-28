#!/usr/bin/env python3
import requests
import subprocess
import time
import json

def check_promtail_status():
    """Check Promtail container status"""
    print("🔍 Checking Promtail container status...")
    
    try:
        # Check Promtail container status
        result = subprocess.run([
            'docker', 'ps', '-a', '--filter', 'name=promtail', '--format', '{{.Names}} | {{.Status}} | {{.Ports}}'
        ], capture_output=True, text=True)
        
        print("📋 Promtail container status:")
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        else:
            print("   ❌ Promtail container not found")
            
        # Check Promtail logs
        logs_result = subprocess.run([
            'docker', 'logs', '--tail', '20', 'promtail'
        ], capture_output=True, text=True)
        
        if logs_result.returncode == 0:
            print("\n📋 Recent Promtail logs:")
            for line in logs_result.stdout.strip().split('\n')[-10:]:
                print(f"   {line}")
        else:
            print("   ❌ Cannot get Promtail logs")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def restart_promtail():
    """Restart Promtail"""
    print("\n🔄 Restarting Promtail...")
    
    try:
        # Stop Promtail
        stop_result = subprocess.run([
            'docker', 'stop', 'promtail'
        ], capture_output=True, text=True)
        
        if stop_result.returncode == 0:
            print("✅ Promtail stopped")
        else:
            print(f"⚠️  Stop failed: {stop_result.stderr}")
        
        # Remove container
        rm_result = subprocess.run([
            'docker', 'rm', 'promtail'
        ], capture_output=True, text=True)
        
        if rm_result.returncode == 0:
            print("✅ Promtail container removed")
        else:
            print(f"⚠️  Remove failed: {stop_result.stderr}")
        
        # Restart monitoring services
        print("🔄 Restarting monitoring services...")
        compose_result = subprocess.run([
            'docker', 'compose', 'up', '-d', 'promtail', 'loki'
        ], capture_output=True, text=True)
        
        if compose_result.returncode == 0:
            print("✅ Monitoring services restarted")
        else:
            print(f"❌ Restart failed: {compose_result.stderr}")
            
        # Wait for startup
        print("⏳ Waiting for Promtail to start...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Restart failed: {e}")

def verify_promtail_fix():
    """Verify Promtail is working"""
    print("\n🔍 Verifying Promtail fix...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            # Check Promtail readiness
            response = requests.get("http://localhost:9080/ready", timeout=5)
            if response.status_code == 200:
                print("✅ Promtail is now READY!")
                
                # Check metrics
                metrics_response = requests.get("http://localhost:9080/metrics", timeout=5)
                if metrics_response.status_code == 200:
                    print("✅ Promtail metrics available")
                    
                    # Check if logs are flowing to Loki
                    logs_response = requests.get(
                        "http://localhost:3100/loki/api/v1/query?query={job=\"docker\"}",
                        timeout=10
                    )
                    if logs_response.status_code == 200:
                        data = logs_response.json()
                        if data['data']['result']:
                            print(f"✅ Logs flowing to Loki: {len(data['data']['result'])} streams")
                        else:
                            print("⚠️  No log streams yet (might need time)")
                    
                    return True
                    
            print(f"   ⏳ Retry {i+1}/{max_retries}...")
            time.sleep(5)
            
        except Exception as e:
            print(f"   ⏳ Retry {i+1}/{max_retries}: {e}")
            time.sleep(5)
    
    print("❌ Promtail still not ready after retries")
    return False

def test_logs_in_grafana():
    """Test logs in Grafana"""
    print("\n📊 Testing logs in Grafana...")
    
    try:
        # Check updated dashboard
        response = requests.get(
            "http://localhost:3000/api/dashboards/uid/f9d3d8f0-6697-471a-8887-1ad4ee8d5fe9",
            auth=('admin', 'admin'),
            timeout=15
        )
        
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Logs dashboard is accessible")
            
            # Check panel queries
            panels = dashboard['dashboard'].get('panels', [])
            for panel in panels:
                if 'targets' in panel:
                    for target in panel['targets']:
                        if target.get('expr') == '{job="docker"}':
                            print(f"✅ Panel '{panel.get('title')}' has correct query")
        
        # Check if data is available through Grafana
        query_response = requests.get(
            "http://localhost:3000/api/datasources/proxy/2/api/v1/query?query={job=\"docker\"}",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if query_response.status_code == 200:
            data = query_response.json()
            if data['data']['result']:
                print("✅ Logs visible in Grafana!")
            else:
                print("⚠️  No logs in Grafana yet")
        else:
            print(f"❌ Grafana query failed: HTTP {query_response.status_code}")
            
    except Exception as e:
        print(f"❌ Grafana test failed: {e}")

if __name__ == "__main__":
    check_promtail_status()
    restart_promtail()
    
    if verify_promtail_fix():
        test_logs_in_grafana()
        
    print("\n🎯 FINAL CHECK:")
    print("1. Run: python3 check_panels.py")
    print("2. Check logs in Grafana: http://localhost:3000")
    print("3. Verify all components are working")
