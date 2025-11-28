#!/usr/bin/env python3
import requests
import time

def check_promtail_port():
    print("🔍 Checking Promtail port 9080...")
    
    try:
        response = requests.get("http://localhost:9080/ready", timeout=5)
        if response.status_code == 200:
            print("✅ Promtail port 9080 is OPEN and ready!")
            return True
        else:
            print(f"❌ Promtail responded but with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Promtail port 9080 not accessible: {e}")
    
    return False

def check_promtail_metrics():
    print("\n📊 Checking Promtail metrics...")
    
    try:
        response = requests.get("http://localhost:9080/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Promtail metrics available")
            # Check if there are active targets
            if 'promtail_target_sync_length' in response.text:
                print("✅ Promtail is processing targets")
            else:
                print("⚠️  Promtail has no active targets")
        else:
            print(f"❌ Promtail metrics: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Promtail metrics check failed: {e}")

def check_loki_logs():
    print("\n📋 Checking Loki logs...")
    
    try:
        response = requests.get(
            "http://localhost:3100/loki/api/v1/query?query={job=\"docker\"}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['data']['result']:
                print(f"✅ Logs in Loki: {len(data['data']['result'])} streams")
                for stream in data['data']['result'][:3]:
                    labels = stream['stream']
                    print(f"   • {labels.get('container', 'unknown')}: {labels.get('job')}")
            else:
                print("⚠️  No logs in Loki yet")
        else:
            print(f"❌ Loki query failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Loki check failed: {e}")

if __name__ == "__main__":
    if check_promtail_port():
        check_promtail_metrics()
        check_loki_logs()
        
    print("\n🎯 Final check:")
    print("python3 check_panels.py")
