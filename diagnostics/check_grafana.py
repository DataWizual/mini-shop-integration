#!/usr/bin/env python3
import requests
import json

def check_grafana():
    print("🔍 Checking Grafana...")
    
    # 1. Check Grafana health
    try:
        health = requests.get("http://localhost:3000/api/health", timeout=5)
        print(f"✅ Grafana health: HTTP {health.status_code}")
    except Exception as e:
        print(f"❌ Grafana health: {e}")
        return
    
    # 2. Check datasources
    try:
        datasources = requests.get(
            "http://localhost:3000/api/datasources",
            auth=('admin', 'admin'),
            timeout=5
        )
        if datasources.status_code == 200:
            print("✅ Datasources accessible")
            for ds in datasources.json():
                print(f"   • {ds['name']}: {ds['type']} ({ds['url']})")
        else:
            print(f"❌ Datasources error: HTTP {datasources.status_code}")
    except Exception as e:
        print(f"❌ Datasources check failed: {e}")
    
    # 3. Check if minishop metrics are visible to Grafana
    try:
        query = requests.get(
            "http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=minishop_requests_total",
            auth=('admin', 'admin'),
            timeout=10
        )
        if query.status_code == 200:
            data = query.json()
            if data['data']['result']:
                print("✅ Minishop metrics found in Grafana!")
                for result in data['data']['result'][:3]:
                    metric = result['metric']
                    value = result['value'][1]
                    print(f"   • {metric.get('endpoint', 'unknown')}: {value}")
            else:
                print("❌ No minishop metrics in Grafana")
        else:
            print(f"❌ Query failed: HTTP {query.status_code}")
    except Exception as e:
        print(f"❌ Metrics query failed: {e}")

if __name__ == "__main__":
    check_grafana()
