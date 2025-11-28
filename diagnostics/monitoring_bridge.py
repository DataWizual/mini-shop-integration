#!/usr/bin/env python3
"""
Bridge between bash scripts and AI components
Thin stateless proxy, no background processes
"""

import requests
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import json

# Add paths to AI component folders
sys.path.append('ai-reporter')
sys.path.append('ai-analysis')

class MonitoringBridge:
    """Thin bridge for combining monitoring components"""
    
    def __init__(self):
        # LAZY initialization - import only when called
        self._insight_gen = None
        self._log_analyzer = None
    
    @property
    def insight_gen(self):
        if self._insight_gen is None:
            try:
                from insight_generator import InsightGenerator
                self._insight_gen = InsightGenerator(use_ai=False)  # AI only on request
            except ImportError as e:
                print(f"⚠️ InsightGenerator unavailable: {e}")
                self._insight_gen = None
        return self._insight_gen
    
    @property
    def log_analyzer(self):
        if self._log_analyzer is None:
            try:
                from smart_analyzer import LogAnalyzer
                self._log_analyzer = LogAnalyzer()
            except ImportError as e:
                print(f"⚠️ LogAnalyzer unavailable: {e}")
                self._log_analyzer = None
        return self._log_analyzer

    def _fast_curl_check(self, url: str, timeout: int = 2) -> bool:
        """Fast service check like in bash scripts"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False

    def get_quick_status(self) -> Dict[str, Any]:
        """⚡ QUICK status (analog of quick_check.sh)"""
        start_time = datetime.now()
        
        # Check services in parallel (like in scripts)
        services = {
            'app': self._fast_curl_check("http://localhost:5000/health"),
            'prometheus': self._fast_curl_check("http://localhost:9090/-/healthy"),
            'loki': self._fast_curl_check("http://localhost:3100/ready"),
            'grafana': self._fast_curl_check("http://localhost:3000/api/health")
        }
        
        # Count containers
        try:
            result = subprocess.run([
                'docker', 'ps', '--filter', 
                'name=prometheus|devops_app|grafana|loki', '--quiet'
            ], capture_output=True, text=True, timeout=5)
            container_count = len([line for line in result.stdout.strip().split('\n') if line])
        except:
            container_count = 0

        services_ok = sum(services.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'services': {
                'total': 4,
                'available': services_ok,
                'details': services
            },
            'containers': {
                'running': container_count,
                'expected': 4
            },
            'status': '🟢 OK' if services_ok == 4 else '🟡 PARTIAL' if services_ok >= 2 else '🔴 CRITICAL'
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """📊 System metrics (analog of metrics_system.sh)"""
        try:
            script_path = './scripts/metrics_system.sh'
            
            if not os.path.exists(script_path):
                return {'error': f'metrics_system.sh not found at {script_path}'}
                
            # Make script executable if needed
            if not os.access(script_path, os.X_OK):
                os.chmod(script_path, 0o755)
                
            result = subprocess.run(
                [script_path], 
                capture_output=True, text=True, timeout=10
            )
            return {
                'source': 'bash_script',
                'script_path': script_path,
                'output': result.stdout,
                'return_code': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Script execution failed: {str(e)}'}

    def get_container_metrics(self) -> Dict[str, Any]:
        """🐳 Container metrics (analog of metrics_containers.sh)"""
        try:
            script_path = './scripts/metrics_containers.sh'
            
            if not os.path.exists(script_path):
                return {'error': f'metrics_containers.sh not found at {script_path}'}
                
            if not os.access(script_path, os.X_OK):
                os.chmod(script_path, 0o755)
                
            result = subprocess.run(
                [script_path], 
                capture_output=True, text=True, timeout=10
            )
            return {
                'source': 'bash_script',
                'script_path': script_path,
                'output': result.stdout,
                'return_code': result.returncode
            }
        except Exception as e:
            return {'error': f'Script execution failed: {str(e)}'}

    def get_detailed_report(self, use_ai: bool = False) -> Dict[str, Any]:
        """📈 DETAILED report (only on explicit request)"""
        start_time = datetime.now()
        
        base_status = self.get_quick_status()
        
        # Heavy operations - only if explicitly requested
        detailed_data = {
            **base_status,
            'system_metrics': self.get_system_metrics(),
            'generation_time_seconds': (datetime.now() - start_time).total_seconds()
        }
        
        if use_ai and self.insight_gen:
            # Enable AI only if explicitly requested and component available
            try:
                self.insight_gen.use_ai = True
                detailed_data['ai_analysis'] = self.insight_gen.generate_report()
            except Exception as e:
                detailed_data['ai_analysis_error'] = str(e)
        
        return detailed_data


# Global instance (lightweight)
bridge = MonitoringBridge()

if __name__ == "__main__":
    # Testing bridge
    print("🚀 Testing Monitoring Bridge...")
    
    print("\n⚡ Quick Status:")
    quick = bridge.get_quick_status()
    print(json.dumps(quick, indent=2, ensure_ascii=False))
    
    print("\n📊 System Metrics:")
    metrics = bridge.get_system_metrics()
    if 'output' in metrics:
        print(metrics['output'][:500] + '...')
    else:
        print(f"Error: {metrics.get('error', 'Unknown')}")
    
    print(f"\n🔍 AI Components:")
    print(f"   InsightGenerator: {'✅' if bridge.insight_gen else '❌'}")
    print(f"   LogAnalyzer: {'✅' if bridge.log_analyzer else '❌'}")