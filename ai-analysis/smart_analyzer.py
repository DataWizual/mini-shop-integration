#!/usr/bin/env python3
import re
import json
from datetime import datetime, timedelta
import requests

class LogAnalyzer:
    def __init__(self):
        self.patterns = {
            'database_errors': [r'connection.*failed', r'timeout', r'deadlock'],
            'performance_issues': [r'high.*response', r'slow', r'timeout'],
            'security_issues': [r'unauthorized', r'forbidden', r'invalid.*token'],
            'application_errors': [r'exception', r'error', r'failed']
        }
    
    def analyze_with_patterns(self, logs_text):
        """Fast pattern-based log analysis"""
        if not logs_text.strip():
            return {
                "timestamp": datetime.now().isoformat(),
                "total_entries": 0,
                "levels": {"INFO": 0, "WARNING": 0, "ERROR": 0},
                "detected_patterns": [],
                "alert_level": "INFO",
                "summary": "No logs available for analysis"
            }
            
        lines = logs_text.strip().split('\n')
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(lines),
            "levels": {
                "INFO": len([l for l in lines if 'INFO' in l]),
                "WARNING": len([l for l in lines if 'WARNING' in l]),
                "ERROR": len([l for l in lines if 'ERROR' in l])
            },
            "detected_patterns": [],
            "alert_level": "INFO",
            "summary": "All systems operating normally"
        }
        
        # Check for problem patterns
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, logs_text, re.IGNORECASE):
                    results["detected_patterns"].append(pattern_type)
                    break
        
        # Determine alert level
        if results["levels"]["ERROR"] > 0:
            results["alert_level"] = "ERROR"
            results["summary"] = "Critical errors detected"
        elif results["levels"]["WARNING"] > 0:
            results["alert_level"] = "WARNING" 
            results["summary"] = "Warnings present"
        
        return results
    
    def get_loki_logs(self, hours=1):
        """Fetch logs from Loki for specified time range"""
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Convert to nanoseconds (Loki format)
            start_ns = int(start_time.timestamp() * 1e9)
            end_ns = int(end_time.timestamp() * 1e9)
            
            url = "http://localhost:3100/loki/api/v1/query_range"
            params = {
                'query': '{job="containerlogs"}',
                'limit': 50,
                'start': start_ns,
                'end': end_ns
            }
            
            print(f"🔍 Loki query: {params}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Check for HTTP errors
            
            data = response.json()
            print(f"✅ Loki response received: {len(data.get('data', {}).get('result', []))} results")
            
            return data
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

# Create global analyzer instance
analyzer = LogAnalyzer()

if __name__ == "__main__":
    print("🔍 Testing Loki integration...")
    
    # Get logs from last hour
    logs_data = analyzer.get_loki_logs(hours=1)
    
    if "error" not in logs_data:
        # Extract log text from Loki response
        log_entries = []
        for result in logs_data.get("data", {}).get("result", []):
            for value in result.get("values", []):
                log_entries.append(value[1])  # log text
        
        logs_text = "\n".join(log_entries[:20])  # Take first 20 entries
        print(f"📊 Log entries received: {len(log_entries)}")
        
        if logs_text.strip():
            analysis = analyzer.analyze_with_patterns(logs_text)
            print("\n📊 Analysis results:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print("❌ No logs available for analysis")
    else:
        print(f"❌ Error: {logs_data['error']}")