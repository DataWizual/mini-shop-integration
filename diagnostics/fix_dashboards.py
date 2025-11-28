#!/usr/bin/env python3
import requests
import json
import time

def update_dashboard_metrics():
    """Update dashboard metrics from app_* to minishop_*"""
    print("🔄 Updating dashboard metrics from app_* to minishop_*...")
    
    # Mapping old metrics to new ones
    metric_mapping = {
        'app_requests_total': 'minishop_requests_total',
        'app_errors_total': 'minishop_errors_total', 
        'app_request_latency_seconds_sum': 'minishop_request_latency_seconds_sum',
        'app_request_latency_seconds_count': 'minishop_request_latency_seconds_count',
        'app_products_total': 'minishop_products_total',
        'app_business_orders_total': 'minishop_business_orders_total'
    }
    
    try:
        # Get dashboard list
        dashboards = requests.get(
            "http://localhost:3000/api/search",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if dashboards.status_code == 200:
            for board in dashboards.json():
                if 'app' in board['title'].lower() or 'metric' in board['title'].lower():
                    print(f"\n🔧 Updating dashboard: {board['title']}")
                    update_single_dashboard(board['uid'], metric_mapping)
        
        print("\n✅ Dashboard update completed!")
        print("💡 Restart Grafana or wait for cache refresh")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")

def update_single_dashboard(dashboard_uid, metric_mapping):
    """Update single dashboard"""
    try:
        # Get dashboard
        response = requests.get(
            f"http://localhost:3000/api/dashboards/uid/{dashboard_uid}",
            auth=('admin', 'admin'),
            timeout=15
        )
        
        if response.status_code == 200:
            dashboard_data = response.json()
            dashboard = dashboard_data['dashboard']
            updated = False
            
            # Find and replace metrics in all panels
            for panel in dashboard.get('panels', []):
                if 'targets' in panel:
                    for target in panel['targets']:
                        expr = target.get('expr', '')
                        if expr:
                            new_expr = expr
                            for old_metric, new_metric in metric_mapping.items():
                                if old_metric in new_expr:
                                    new_expr = new_expr.replace(old_metric, new_metric)
                                    updated = True
                                    print(f"   • {panel.get('title', 'Unknown')}: {old_metric} → {new_metric}")
                            
                            target['expr'] = new_expr
            
            # Save updated dashboard
            if updated:
                save_response = requests.post(
                    "http://localhost:3000/api/dashboards/db",
                    auth=('admin', 'admin'),
                    json=dashboard_data,
                    timeout=15
                )
                
                if save_response.status_code == 200:
                    print(f"   ✅ Dashboard updated successfully")
                else:
                    print(f"   ❌ Failed to save: HTTP {save_response.status_code}")
            else:
                print(f"   ⚠️  No metrics to update")
                
    except Exception as e:
        print(f"   ❌ Update failed: {e}")

def create_minishop_dashboard():
    """Create specialized dashboard for MiniShop"""
    print("\n🎨 Creating MiniShop-specific dashboard...")
    
    minishop_dashboard = {
        "dashboard": {
            "title": "MiniShop Metrics",
            "tags": ["minishop", "application"],
            "timezone": "browser",
            "panels": [
                {
                    "title": "MiniShop Total Requests",
                    "type": "stat",
                    "targets": [{
                        "expr": "sum(minishop_requests_total)",
                        "legendFormat": "Total Requests"
                    }]
                },
                {
                    "title": "MiniShop Request Rate", 
                    "type": "graph",
                    "targets": [{
                        "expr": "rate(minishop_requests_total[1m])",
                        "legendFormat": "{{endpoint}}"
                    }]
                },
                {
                    "title": "MiniShop Errors",
                    "type": "stat", 
                    "targets": [{
                        "expr": "sum(minishop_errors_total)",
                        "legendFormat": "Total Errors"
                    }]
                },
                {
                    "title": "MiniShop Products",
                    "type": "stat",
                    "targets": [{
                        "expr": "minishop_products_total", 
                        "legendFormat": "Products in DB"
                    }]
                }
            ]
        },
        "overwrite": False
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/dashboards/db",
            auth=('admin', 'admin'),
            json=minishop_dashboard,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ MiniShop dashboard created!")
        else:
            print(f"❌ Failed to create dashboard: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard creation failed: {e}")

if __name__ == "__main__":
    update_dashboard_metrics()
    create_minishop_dashboard()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Wait 30 seconds for Grafana cache refresh")
    print("2. Run: python3 check_panels.py")
    print("3. Check http://localhost:3000 for updated dashboards")
