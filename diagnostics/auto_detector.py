#!/usr/bin/env python3
import docker
import requests
import yaml
from pathlib import Path
import subprocess
import json

def diagnose_healthcheck(container_name):
    """Diagnose healthcheck problems"""
    print(f"\n🔍 HEALTHCHECK DIAGNOSIS for {container_name}:")
    
    try:
        # Get detailed container information
        result = subprocess.run([
            'docker', 'inspect', container_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            container_info = json.loads(result.stdout)[0]
            health = container_info.get('State', {}).get('Health', {})
            
            if health:
                print(f"   • Status: {health.get('Status', 'unknown')}")
                print(f"   • Failing Streak: {health.get('FailingStreak', 0)}")
                print(f"   • Logs:")
                
                # Show recent healthcheck logs
                for log_entry in health.get('Log', [])[-3:]:  # Last 3 checks
                    output = log_entry.get('Output', '').strip()
                    exit_code = log_entry.get('ExitCode', 0)
                    print(f"     - Exit: {exit_code}, Output: {output[:100]}...")
            
            # Show current healthcheck config
            hc_config = container_info.get('Config', {}).get('Healthcheck', {})
            if hc_config:
                print(f"   • Current test: {hc_config.get('Test', [])}")
        
    except Exception as e:
        print(f"   • Diagnosis error: {e}")

def check_container_startup(container_name):
    """Check container startup logs"""
    print(f"\n📋 STARTUP LOGS for {container_name}:")
    
    try:
        # Get recent startup logs
        logs = subprocess.run([
            'docker', 'logs', '--tail', '20', container_name
        ], capture_output=True, text=True)
        
        if logs.returncode == 0:
            lines = logs.stdout.strip().split('\n')
            print("   • Recent logs:")
            for line in lines[-5:]:  # Last 5 lines
                print(f"     - {line}")
    except Exception as e:
        print(f"   • Failed to get logs: {e}")

def check_health_status(container_name):
    """Check actual container healthcheck status"""
    try:
        result = subprocess.run([
            'docker', 'inspect', '--format', '{{.State.Health.Status}}', container_name
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            status = result.stdout.strip()
            return status
    except subprocess.TimeoutExpired:
        return "timeout"
    except Exception:
        pass
    return "unknown"

def check_prometheus_config(container_name):
    """Check Prometheus configuration"""
    prometheus_config = Path("monitoring/prometheus.yml")
    
    if prometheus_config.exists():
        try:
            with open(prometheus_config, 'r') as f:
                config = yaml.safe_load(f)
            
            # Look for application configuration
            for job in config.get('scrape_configs', []):
                if job.get('job_name') == 'app':
                    targets = job.get('static_configs', [{}])[0].get('targets', [])
                    if targets and container_name in targets[0]:
                        print("   ✅ Prometheus configured correctly")
                    else:
                        print("   ❌ Prometheus configured INCORRECTLY")
                        print(f"   💡 Current setting: {targets}")
                        print(f"   💡 Should be: ['{container_name}:5000']")
        except Exception as e:
            print(f"   ⚠️  Error reading Prometheus config: {e}")
    else:
        print("   ⚠️  Prometheus config file not found")

def detect_apps():
    """Simple application detector with hints"""
    try:
        client = docker.from_env()
        print("🔍 Searching for applications...")
        
        for container in client.containers.list():
            # Look for applications by ports
            if container.ports and any('5000' in str(port) for port in container.ports):
                print(f"\n📱 Found application: {container.name}")
                print(f"   • Status: {container.status}")
                
                # Check metrics
                metrics_url = "http://localhost:5000/metrics"
                try:
                    response = requests.get(metrics_url, timeout=2)
                    if response.status_code == 200:
                        print("   ✅ Metrics available")
                    else:
                        print("   ❌ Metrics unavailable")
                except:
                    print("   ❌ Failed to connect to metrics")
                
                # Check health endpoints
                for endpoint in ["/", "/health", "/metrics"]:
                    health_url = f"http://localhost:5000{endpoint}"
                    try:
                        response = requests.get(health_url, timeout=2)
                        status_icon = "✅" if response.status_code == 200 else "⚠️"
                        
                        if endpoint == "/health" and response.status_code == 404:
                            print(f"   • {endpoint}: HTTP {response.status_code} {status_icon} (OK - endpoint not required)")
                        else:
                            print(f"   • {endpoint}: HTTP {response.status_code} {status_icon}")
                            
                    except Exception as e:
                        print(f"   • {endpoint}: ❌ {e}")
                
                # Check Docker health status
                health_status = check_health_status(container.name)
                print(f"   • Docker Health: {health_status.upper()}")
                
                # If container is unhealthy - do full diagnosis
                if "unhealthy" in container.status.lower():
                    diagnose_healthcheck(container.name)
                    check_container_startup(container.name)
                
                # Check Prometheus configuration
                check_prometheus_config(container.name)
                
    except docker.errors.DockerException as e:
        print(f"❌ Docker error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    detect_apps()
