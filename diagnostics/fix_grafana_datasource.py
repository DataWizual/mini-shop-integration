#!/usr/bin/env python3
import requests
import json
import time

def check_grafana_datasources():
    """Check datasources in Grafana"""
    print("🔍 Checking Grafana datasources...")
    
    try:
        # Get datasources list
        response = requests.get(
            "http://localhost:3000/api/datasources",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if response.status_code == 200:
            datasources = response.json()
            print(f"✅ Found {len(datasources)} datasources:")
            
            for ds in datasources:
                print(f"   • {ds['name']}: {ds['type']} (ID: {ds['id']})")
                
                # Check Loki datasource availability
                if ds['type'] == 'loki':
                    test_loki_datasource(ds['id'], ds['name'])
                    
        else:
            print(f"❌ Cannot get datasources: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Datasource check failed: {e}")

def test_loki_datasource(datasource_id, datasource_name):
    """Test Loki datasource"""
    print(f"\n🔍 Testing Loki datasource '{datasource_name}' (ID: {datasource_id})...")
    
    try:
        # Test query through Grafana
        test_query = "{job=\"docker\"}"
        response = requests.get(
            f"http://localhost:3000/api/datasources/proxy/{datasource_id}/loki/api/v1/query?query={test_query}",
            auth=('admin', 'admin'),
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['data']['result']:
                print(f"✅ Loki datasource WORKING: {len(data['data']['result'])} log streams")
                for stream in data['data']['result'][:3]:
                    print(f"   • {stream['stream'].get('container', 'unknown')}")
            else:
                print("⚠️  Loki datasource working but no results")
        else:
            print(f"❌ Loki datasource FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Loki datasource test failed: {e}")

def fix_loki_datasource():
    """Fix Loki datasource configuration"""
    print("\n🔧 Fixing Loki datasource configuration...")
    
    try:
        # Get current Loki datasource
        response = requests.get(
            "http://localhost:3000/api/datasources/name/Loki",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if response.status_code == 200:
            loki_ds = response.json()
            print(f"✅ Found Loki datasource (ID: {loki_ds['id']})")
            
            # Update URL if needed
            if loki_ds['url'] != 'http://loki:3100':
                loki_ds['url'] = 'http://loki:3100'
                print("   • Updated URL to http://loki:3100")
            
            # Save updated datasource
            update_response = requests.put(
                f"http://localhost:3000/api/datasources/{loki_ds['id']}",
                auth=('admin', 'admin'),
                json=loki_ds,
                timeout=15
            )
            
            if update_response.status_code == 200:
                print("✅ Loki datasource updated successfully")
            else:
                print(f"❌ Failed to update: HTTP {update_response.status_code}")
                
        else:
            print(f"❌ Cannot get Loki datasource: HTTP {response.status_code}")
            create_loki_datasource()
            
    except Exception as e:
        print(f"❌ Datasource fix failed: {e}")

def create_loki_datasource():
    """Create Loki datasource if it doesn't exist"""
    print("🔄 Creating new Loki datasource...")
    
    loki_datasource = {
        "name": "Loki",
        "type": "loki",
        "url": "http://loki:3100",
        "access": "proxy",
        "basicAuth": False,
        "isDefault": False,
        "jsonData": {
            "maxLines": 1000
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/datasources",
            auth=('admin', 'admin'),
            json=loki_datasource,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ Loki datasource created successfully")
        else:
            print(f"❌ Failed to create: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Datasource creation failed: {e}")

def update_dashboard_datasource():
    """Update datasource in logs dashboard"""
    print("\n🔄 Updating dashboard datasource references...")
    
    try:
        # Get Application Logs dashboard
        response = requests.get(
            "http://localhost:3000/api/dashboards/uid/f9d3d8f0-6697-471a-8887-1ad4ee8d5fe9",
            auth=('admin', 'admin'),
            timeout=15
        )
        
        if response.status_code == 200:
            dashboard_data = response.json()
            dashboard = dashboard_data['dashboard']
            
            # Get Loki datasource ID
            ds_response = requests.get(
                "http://localhost:3000/api/datasources/name/Loki",
                auth=('admin', 'admin'),
                timeout=10
            )
            
            if ds_response.status_code == 200:
                loki_ds = ds_response.json()
                loki_ds_id = loki_ds['id']
                
                # Update datasource in panels
                updated = False
                for panel in dashboard.get('panels', []):
                    if 'targets' in panel:
                        for target in panel['targets']:
                            if target.get('datasource') != loki_ds_id:
                                target['datasource'] = {'type': 'loki', 'uid': loki_ds['uid']}
                                updated = True
                                print(f"   • Updated datasource for panel '{panel.get('title')}'")
                
                if updated:
                    # Save updated dashboard
                    save_response = requests.post(
                        "http://localhost:3000/api/dashboards/db",
                        auth=('admin', 'admin'),
                        json=dashboard_data,
                        timeout=15
                    )
                    
                    if save_response.status_code == 200:
                        print("✅ Dashboard datasources updated successfully")
                    else:
                        print(f"❌ Failed to save: HTTP {save_response.status_code}")
                else:
                    print("⚠️  No datasource updates needed")
                    
        else:
            print(f"❌ Cannot get dashboard: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard update failed: {e}")

if __name__ == "__main__":
    check_grafana_datasources()
    fix_loki_datasource()
    update_dashboard_datasource()
    
    print("\n🎯 FINAL TEST:")
    print("1. Wait 30 seconds")
    print("2. Run: python3 check_panels.py")
    print("3. Check logs in Grafana: http://localhost:3000")
