#!/usr/bin/env python3
import json
import requests
import docker

# Configuration
GRAFANA_URL = "http://localhost:3000"
AUTH = ("admin", "admin")

def detect_running_containers():
    """Auto-detect running containers"""
    print("🔍 Auto-detecting containers...")
    
    try:
        client = docker.from_env()
        containers = {}
        
        for container in client.containers.list():
            # Look for applications (not infrastructure services)
            if not any(service in container.name for service in 
                      ['prometheus', 'loki', 'grafana', 'promtail', 'cadvisor', 'node-exporter']):
                containers[container.name] = {
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'status': container.status
                }
                print(f"   ✅ Found application: {container.name}")
        
        return containers
        
    except Exception as e:
        print(f"❌ Container detection error: {e}")
        return {}

def get_available_loki_labels():
    """Get available labels from Loki"""
    print("🔍 Getting available labels from Loki...")
    
    try:
        response = requests.get("http://localhost:3100/loki/api/v1/labels", timeout=10)
        if response.status_code == 200:
            labels = response.json()['data']
            print(f"   ✅ Available labels: {', '.join(labels)}")
            return labels
        else:
            print(f"❌ Error getting labels: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Loki connection error: {e}")
        return []

def find_working_log_query():
    """Find working log query"""
    print("🔍 Finding working log query...")
    
    test_queries = [
        '{job="docker"}',
        '{container=~".+"}',
        '{service!=""}',
        '{app!=""}'
    ]
    
    for query in test_queries:
        try:
            response = requests.get(
                f"http://localhost:3100/loki/api/v1/query?query={query}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data['data']['result']:
                    print(f"   ✅ Working query: {query} ({len(data['data']['result'])} streams)")
                    return query
        except:
            continue
    
    print("   ⚠️  No working query found, using universal one")
    return '{container=~".+"}'

def get_all_dashboards():
    """Get all dashboards"""
    try:
        response = requests.get(f"{GRAFANA_URL}/api/search", auth=AUTH, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting dashboards: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Grafana connection error: {e}")
        return []

def fix_dashboard_queries(dashboard_uid, working_query):
    """Fix queries in dashboard"""
    print(f"\n🔧 Fixing dashboard {dashboard_uid}...")
    
    try:
        # Get dashboard
        response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}", auth=AUTH)
        if response.status_code != 200:
            print(f"❌ Cannot get dashboard {dashboard_uid}")
            return False

        dashboard_data = response.json()
        dashboard = dashboard_data['dashboard']
        dashboard_title = dashboard.get('title', 'Unknown')
        
        print(f"📊 Dashboard: {dashboard_title}")
        
        # Fix queries in panels
        fixed_panels = 0
        for panel in dashboard.get('panels', []):
            panel_title = panel.get('title', 'Unknown Panel')
            
            for target in panel.get('targets', []):
                old_expr = target.get('expr', '')
                
                # Replace outdated queries
                if old_expr and any(bad_query in old_expr for bad_query in 
                                   ['job="containerlogs"', 'container="devops_app"', 'app_requests_total']):
                    
                    # Universal replacement
                    new_expr = old_expr
                    
                    # Replace outdated job names
                    if 'job="containerlogs"' in new_expr:
                        new_expr = new_expr.replace('job="containerlogs"', 'job="docker"')
                    
                    # Replace outdated container names
                    if 'container="devops_app"' in new_expr:
                        # Auto-replace with working query
                        new_expr = working_query
                    
                    # Replace outdated metrics
                    if 'app_' in new_expr and 'minishop_' not in new_expr:
                        new_expr = new_expr.replace('app_', 'minishop_')
                    
                    if new_expr != old_expr:
                        target['expr'] = new_expr
                        fixed_panels += 1
                        print(f"   ✅ Fixed panel '{panel_title}':")
                        print(f"       Was: {old_expr}")
                        print(f"       Now: {new_expr}")
        
        if fixed_panels > 0:
            # Save updated dashboard
            update_data = {
                "dashboard": dashboard,
                "message": f"Auto-fixed {fixed_panels} panels with universal queries",
                "overwrite": True
            }

            update_response = requests.post(f"{GRAFANA_URL}/api/dashboards/db", 
                                          auth=AUTH, 
                                          json=update_data)

            if update_response.status_code == 200:
                print(f"🎉 Dashboard '{dashboard_title}' updated! ({fixed_panels} panels fixed)")
                return True
            else:
                print(f"❌ Update error: HTTP {update_response.status_code}")
                return False
        else:
            print(f"   ⚠️  No fixes needed for dashboard '{dashboard_title}'")
            return True
            
    except Exception as e:
        print(f"❌ Dashboard processing error: {e}")
        return False

def create_universal_dashboard(working_query):
    """Create universal dashboard"""
    print("\n🎨 Creating universal dashboard...")
    
    universal_dashboard = {
        "dashboard": {
            "title": "Universal Container Logs",
            "tags": ["logs", "containers", "universal", "auto-detected"],
            "timezone": "browser",
            "panels": [
                {
                    "title": "All Container Logs (Universal)",
                    "type": "logs",
                    "targets": [{
                        "expr": working_query,
                        "refId": "A"
                    }],
                    "options": {
                        "showTime": True,
                        "wrapLogMessage": True,
                        "showLabels": True,
                        "showCommonLabels": False,
                        "prettifyLogMessage": True,
                        "enableLogDetails": True,
                        "dedupStrategy": "none"
                    }
                },
                {
                    "title": "Application Logs Filter", 
                    "type": "logs",
                    "targets": [{
                        "expr": working_query + ' |~ ".*(ERROR|WARN|Exception|error).*"',
                        "refId": "A"
                    }],
                    "options": {
                        "showTime": True,
                        "wrapLogMessage": True,
                        "showLabels": True
                    }
                }
            ]
        },
        "overwrite": False
    }
    
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db",
            auth=AUTH,
            json=universal_dashboard,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ Universal dashboard created!")
            return True
        else:
            print(f"❌ Creation error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard creation error: {e}")
        return False

def main():
    print("🔄 UNIVERSAL DASHBOARD FIXER")
    print("=============================")
    
    # 1. Auto-detect environment
    containers = detect_running_containers()
    labels = get_available_loki_labels()
    working_query = find_working_log_query()
    
    print(f"\n🎯 WORKING QUERY: {working_query}")
    
    # 2. Get all dashboards
    dashboards = get_all_dashboards()
    
    if not dashboards:
        print("❌ No dashboards found to fix")
        return
    
    # 3. Fix each dashboard
    fixed_count = 0
    for dashboard in dashboards:
        if fix_dashboard_queries(dashboard['uid'], working_query):
            fixed_count += 1
    
    # 4. Create universal dashboard
    create_universal_dashboard(working_query)
    
    print(f"\n🎉 COMPLETED! Fixed dashboards: {fixed_count}/{len(dashboards)}")
    print("🔧 System now automatically adapts to any application!")
    
    # 5. Show recommendations
    print("\n📋 RECOMMENDATIONS:")
    print("   • Use '{job=\"docker\"}' for container logs")
    print("   • Use '{container=~\".+\"}' for all containers") 
    print("   • Use 'minishop_' prefix for application metrics")
    print("   • Universal dashboard created: 'Universal Container Logs'")

if __name__ == "__main__":
    main()
