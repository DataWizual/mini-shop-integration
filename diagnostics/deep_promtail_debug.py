#!/usr/bin/env python3
import subprocess
import time
import yaml
from pathlib import Path

def deep_promtail_debug():
    """Deep Promtail diagnostics"""
    print("🔍 Deep Promtail Debug...")
    
    # 1. Check if container is running
    print("\n📋 Container status:")
    result = subprocess.run([
        'docker', 'ps', '-a', '--filter', 'name=promtail', 
        '--format', '{{.Names}} | {{.Status}} | {{.State}} | {{.Ports}}'
    ], capture_output=True, text=True)
    print(f"   {result.stdout.strip()}")
    
    # 2. Check detailed container information
    print("\n📋 Container details:")
    inspect_result = subprocess.run([
        'docker', 'inspect', 'promtail'
    ], capture_output=True, text=True)
    
    if inspect_result.returncode == 0:
        import json
        container_info = json.loads(inspect_result.stdout)[0]
        
        # Status
        state = container_info['State']
        print(f"   • Status: {state['Status']}")
        print(f"   • Running: {state['Running']}")
        print(f"   • ExitCode: {state['ExitCode']}")
        print(f"   • Error: {state.get('Error', 'None')}")
        
        # Port mapping
        ports = container_info['NetworkSettings']['Ports']
        print(f"   • Ports: {ports}")
        
        # Healthcheck
        health = state.get('Health', {})
        if health:
            print(f"   • Health: {health.get('Status', 'Unknown')}")
    
    # 3. Check logs from the beginning
    print("\n📋 Full Promtail logs:")
    logs_result = subprocess.run([
        'docker', 'logs', 'promtail'
    ], capture_output=True, text=True)
    
    if logs_result.returncode == 0 and logs_result.stdout.strip():
        print("Recent logs:")
        for line in logs_result.stdout.strip().split('\n')[-20:]:
            print(f"   {line}")
    else:
        print("   ❌ No logs or cannot access")
    
    # 4. Check configuration file
    print("\n🔧 Checking Promtail configuration...")
    promtail_config = Path("logs/promtail.yml")
    if promtail_config.exists():
        with open(promtail_config, 'r') as f:
            config = yaml.safe_load(f)
        
        print("   ✅ Config file exists")
        
        # Check main sections
        if 'server' in config:
            print(f"   • Server port: {config['server'].get('http_listen_port')}")
        else:
            print("   ❌ Missing server section")
            
        if 'clients' in config:
            print(f"   • Loki URL: {config['clients'][0].get('url')}")
        else:
            print("   ❌ Missing clients section")
            
        if 'scrape_configs' in config:
            print(f"   • Scrape configs: {len(config['scrape_configs'])}")
        else:
            print("   ❌ Missing scrape_configs section")
    else:
        print("   ❌ Config file not found")
    
    # 5. Check mounted volumes
    print("\n📋 Volume mounts:")
    mounts_result = subprocess.run([
        'docker', 'inspect', '--format', '{{json .Mounts}}', 'promtail'
    ], capture_output=True, text=True)
    
    if mounts_result.returncode == 0:
        mounts = json.loads(mounts_result.stdout)
        for mount in mounts:
            print(f"   • {mount['Source']} → {mount['Destination']} ({mount['Type']})")

def check_promtail_config_file():
    """Check configuration file correctness"""
    print("\n🔍 Validating Promtail config...")
    
    promtail_config = Path("logs/promtail.yml")
    if promtail_config.exists():
        with open(promtail_config, 'r') as f:
            content = f.read()
            print("Config file content:")
            print("=" * 50)
            print(content)
            print("=" * 50)

def test_promtail_manually():
    """Test Promtail manual startup"""
    print("\n🚀 Testing Promtail manually...")
    
    # Stop current container
    subprocess.run(['docker', 'stop', 'promtail'], capture_output=True)
    subprocess.run(['docker', 'rm', 'promtail'], capture_output=True)
    
    # Start with logging
    print("Starting Promtail with debug...")
    manual_start = subprocess.run([
        'docker', 'run', '-d',
        '--name', 'promtail_debug',
        '--volume', f"{Path.cwd()}/logs/promtail.yml:/etc/promtail/promtail.yml:ro",
        '--volume', '/var/log:/var/log:ro',
        '--volume', '/var/run/docker.sock:/var/run/docker.sock',
        '--network', 'mini-shop-integration-test_monitoring',
        '--publish', '9080:9080',
        'grafana/promtail:latest',
        '-config.file=/etc/promtail/promtail.yml',
        '-log.level=debug'
    ], capture_output=True, text=True)
    
    if manual_start.returncode == 0:
        print("✅ Promtail started manually")
        
        # Wait and check logs
        time.sleep(5)
        print("\n📋 Manual startup logs:")
        logs = subprocess.run([
            'docker', 'logs', 'promtail_debug'
        ], capture_output=True, text=True)
        
        if logs.returncode == 0:
            for line in logs.stdout.strip().split('\n')[-15:]:
                print(f"   {line}")
    else:
        print(f"❌ Manual start failed: {manual_start.stderr}")

def fix_promtail_config():
    """Fix possible configuration problems"""
    print("\n🔧 Fixing Promtail configuration...")
    
    promtail_config = Path("logs/promtail.yml")
    if promtail_config.exists():
        with open(promtail_config, 'r') as f:
            config = yaml.safe_load(f)
        
        # Ensure server section is correct
        if 'server' not in config:
            config['server'] = {}
        
        config['server']['http_listen_port'] = 9080
        config['server']['grpc_listen_port'] = 0
        
        # Rewrite config
        with open(promtail_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Config updated")
        
        # Show updated config
        with open(promtail_config, 'r') as f:
            print("Updated config:")
            print("=" * 30)
            print(f.read())
            print("=" * 30)

if __name__ == "__main__":
    deep_promtail_debug()
    check_promtail_config_file()
    fix_promtail_config()
    test_promtail_manually()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check if manual Promtail works")
    print("2. If yes - update docker-compose.yml")
    print("3. Run: python3 check_panels.py")
