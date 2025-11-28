#!/usr/bin/env python3
import requests
import json

def check_dashboards():
    print("🔍 Checking Grafana Dashboards...")
    
    try:
        # Get all dashboards
        dashboards = requests.get(
            "http://localhost:3000/api/search",
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if dashboards.status_code == 200:
            boards = dashboards.json()
            print(f"✅ Found {len(boards)} dashboards:")
            
            minishop_boards = []
            for board in boards:
                title = board.get('title', 'Unknown')
                print(f"   • {title}")
                if 'minishop' in title.lower() or 'app' in title.lower():
                    minishop_boards.append(title)
            
            if minishop_boards:
                print(f"\n🎯 Minishop-related dashboards: {', '.join(minishop_boards)}")
            else:
                print("\n⚠️  No Minishop-specific dashboards found")
                
            # Check if we can access a dashboard
            if boards:
                first_board = boards[0]
                dashboard_detail = requests.get(
                    f"http://localhost:3000/api/dashboards/uid/{first_board['uid']}",
                    auth=('admin', 'admin'),
                    timeout=10
                )
                if dashboard_detail.status_code == 200:
                    print("✅ Dashboards are accessible")
                else:
                    print("❌ Cannot access dashboard details")
                    
        else:
            print(f"❌ Cannot fetch dashboards: HTTP {dashboards.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard check failed: {e}")

def test_minishop_queries():
    print("\n🔍 Testing Minishop queries in Grafana...")
    
    test_queries = [
        "minishop_requests_total",
        "minishop_errors_total", 
        "minishop_products_total",
        "minishop_request_latency_seconds_count"
    ]
    
    for query in test_queries:
        try:
            result = requests.get(
                f"http://localhost:3000/api/datasources/proxy/1/api/v1/query?query={query}",
                auth=('admin', 'admin'),
                timeout=10
            )
            if result.status_code == 200:
                data = result.json()
                if data['data']['result']:
                    print(f"✅ {query}: {len(data['data']['result'])} time series")
                else:
                    print(f"⚠️  {query}: No data (might be normal)")
            else:
                print(f"❌ {query}: HTTP {result.status_code}")
        except Exception as e:
            print(f"❌ {query}: {e}")

if __name__ == "__main__":
    check_dashboards()
    test_minishop_queries()
