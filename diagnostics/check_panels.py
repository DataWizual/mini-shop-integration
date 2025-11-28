#!/usr/bin/env python3
import requests
import json
import time

def check_dashboard_panels(dashboard_uid):
    """Check functionality of all panels in dashboard"""
    print(f"\n🔍 Checking panels in dashboard {dashboard_uid}...")
    
    try:
        # Get full dashboard information
        response = requests.get(
            f"http://localhost:3000/api/dashboards/uid/{dashboard_uid}",
            auth=('admin', 'admin'),
            timeout=15
        )
        
        if response.status_code == 200:
            dashboard = response.json()['dashboard']
            panels = dashboard.get('panels', [])
            print(f"📊 Found {len(panels)} panels in '{dashboard['title']}'")
            
            working_panels = 0
            problematic_panels = []
            
            for panel in panels:
                panel_title = panel.get('title', 'Unknown Panel')
                panel_id = panel.get('id')
                
                # Check panel metrics
                if 'targets' in panel:
                    metrics_working = check_panel_metrics(panel['targets'], panel_title)
                    if metrics_working:
                        working_panels += 1
                    else:
                        problematic_panels.append(panel_title)
                else:
                    print(f"   ⚠️  {panel_title}: No metrics configured")
            
            print(f"✅ Working panels: {working_panels}/{len(panels)}")
            if problematic_panels:
                print(f"❌ Problematic panels: {', '.join(problematic_panels)}")
                
        else:
            print(f"❌ Cannot access dashboard: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard check failed: {e}")

def check_panel_metrics(targets, panel_title):
    """Check metrics for specific panel"""
    try:
        all_targets_working = True
        
        for target in targets:
            # Extract Prometheus query from panel
            expr = target.get('expr', '')
            if expr:
                # Execute query through Grafana
                result = requests.get(
                    f"http://localhost:3000/api/datasources/proxy/1/api/v1/query?query={expr}",
                    auth=('admin', 'admin'),
                    timeout=10
                )
                
                if result.status_code == 200:
                    data = result.json()
                    if data['data']['result']:
                        print(f"   ✅ {panel_title}: Data available ({len(data['data']['result'])} series)")
                    else:
                        print(f"   ⚠️  {panel_title}: No data for query: {expr[:50]}...")
                        all_targets_working = False
                else:
                    print(f"   ❌ {panel_title}: Query failed: {expr[:50]}...")
                    all_targets_working = False
        
        return all_targets_working
        
    except Exception as e:
        print(f"   ❌ {panel_title}: Check failed: {e}")
        return False

def test_real_time_updates():
    """Test real-time data updates"""
    print("\n🔄 Testing real-time data updates...")
    
    # Query current metrics
    initial_query = "minishop_requests_total"
    
    try:
        # First query
        result1 = requests.get(
            f"http://localhost:3000/api/datasources/proxy/1/api/v1/query?query={initial_query}",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if result1.status_code == 200:
            data1 = result1.json()
            initial_count = sum(int(r['value'][1]) for r in data1['data']['result']) if data1['data']['result'] else 0
            print(f"   • Initial request count: {initial_count}")
            
            # Wait a bit
            print("   • Waiting 10 seconds for new data...")
            time.sleep(10)
            
            # Second query
            result2 = requests.get(
                f"http://localhost:3000/api/datasources/proxy/1/api/v1/query?query={initial_query}",
                auth=('admin', 'admin'),
                timeout=10
            )
            
            if result2.status_code == 200:
                data2 = result2.json()
                new_count = sum(int(r['value'][1]) for r in data2['data']['result']) if data2['data']['result'] else 0
                print(f"   • New request count: {new_count}")
                
                if new_count > initial_count:
                    print("   ✅ Real-time updates: WORKING")
                else:
                    print("   ⚠️  Real-time updates: No new data (might be normal)")
            else:
                print("   ❌ Real-time updates: Second query failed")
        else:
            print("   ❌ Real-time updates: First query failed")
            
    except Exception as e:
        print(f"   ❌ Real-time updates test failed: {e}")

def main():
    print("🔍 DEEP DASHBOARD PANELS CHECK")
    print("==============================")
    
    # Get dashboard list
    try:
        dashboards = requests.get(
            "http://localhost:3000/api/search",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if dashboards.status_code == 200:
            for board in dashboards.json():
                if 'app' in board['title'].lower() or 'metric' in board['title'].lower():
                    check_dashboard_panels(board['uid'])
        
        test_real_time_updates()
        
    except Exception as e:
        print(f"❌ Main check failed: {e}")

if __name__ == "__main__":
    main()
