# network_analyzer.py
#!/usr/bin/env python3
"""
Network metrics analyzer for monitoring
"""

import subprocess
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
import statistics


class NetworkAnalyzer:
    """Network metrics analyzer"""
    
    def __init__(self):
        self.target_services = [
            'http://localhost:5000',      # Application
            'http://localhost:9090',      # Prometheus
            'http://localhost:3100',      # Loki
            'http://localhost:3000',      # Grafana
            '8.8.8.8',                    # DNS Google
            '1.1.1.1'                     # DNS Cloudflare
        ]
    
    def ping_service(self, target: str) -> Dict[str, Any]:
        """Ping service with response time measurement"""
        try:
            # Remove protocol for ping command
            host = target.replace('http://', '').replace('https://', '').split('/')[0]
            
            # Execute ping
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '2', host],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Parse response time
                lines = result.stdout.split('\n')
                times = []
                for line in lines:
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split(' ')[0]
                        times.append(float(time_str))
                
                if times:
                    return {
                        'target': target,
                        'available': True,
                        'response_times': times,
                        'avg_time': statistics.mean(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'packet_loss': 0
                    }
            
            return {
                'target': target,
                'available': False,
                'error': 'Ping failed',
                'response_times': [],
                'avg_time': 0,
                'packet_loss': 100
            }
            
        except subprocess.TimeoutExpired:
            return {
                'target': target,
                'available': False,
                'error': 'Timeout',
                'response_times': [],
                'avg_time': 0,
                'packet_loss': 100
            }
        except Exception as e:
            return {
                'target': target,
                'available': False,
                'error': str(e),
                'response_times': [],
                'avg_time': 0,
                'packet_loss': 100
            }
    
    def http_response_time(self, url: str) -> Dict[str, Any]:
        """HTTP response time measurement"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            
            return {
                'url': url,
                'available': True,
                'response_time_ms': (end_time - start_time) * 1000,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
        except Exception as e:
            return {
                'url': url,
                'available': False,
                'error': str(e),
                'response_time_ms': 0
            }
    
    def check_dns_resolution(self, hostname: str) -> Dict[str, Any]:
        """DNS resolution check"""
        try:
            import socket
            start_time = time.time()
            socket.gethostbyname(hostname)
            end_time = time.time()
            
            return {
                'hostname': hostname,
                'resolved': True,
                'resolution_time_ms': (end_time - start_time) * 1000
            }
        except Exception as e:
            return {
                'hostname': hostname,
                'resolved': False,
                'error': str(e),
                'resolution_time_ms': 0
            }
    
    def analyze_network_health(self) -> Dict[str, Any]:
        """Complete network health analysis"""
        print("🌐 Analyzing network metrics...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'ping_results': [],
            'http_results': [],
            'dns_results': [],
            'summary': {}
        }
        
        # Ping analysis
        ping_times = []
        available_pings = 0
        
        for target in self.target_services:
            if not target.startswith('http'):
                ping_result = self.ping_service(target)
                results['ping_results'].append(ping_result)
                
                if ping_result['available']:
                    available_pings += 1
                    ping_times.append(ping_result['avg_time'])
        
        # HTTP analysis
        http_times = []
        available_http = 0
        
        for target in self.target_services:
            if target.startswith('http'):
                http_result = self.http_response_time(target)
                results['http_results'].append(http_result)
                
                if http_result['available']:
                    available_http += 1
                    http_times.append(http_result['response_time_ms'])
        
        # DNS analysis
        dns_hosts = ['google.com', 'github.com', 'docker.com']
        dns_times = []
        resolved_dns = 0
        
        for host in dns_hosts:
            dns_result = self.check_dns_resolution(host)
            results['dns_results'].append(dns_result)
            
            if dns_result['resolved']:
                resolved_dns += 1
                dns_times.append(dns_result['resolution_time_ms'])
        
        # Summary
        results['summary'] = {
            'ping_availability': available_pings / len([t for t in self.target_services if not t.startswith('http')]) * 100,
            'http_availability': available_http / len([t for t in self.target_services if t.startswith('http')]) * 100,
            'dns_availability': resolved_dns / len(dns_hosts) * 100,
            'avg_ping_time': statistics.mean(ping_times) if ping_times else 0,
            'avg_http_time': statistics.mean(http_times) if http_times else 0,
            'avg_dns_time': statistics.mean(dns_times) if dns_times else 0,
            'total_checks': len(self.target_services) + len(dns_hosts)
        }
        
        return results
    
    def generate_network_report(self) -> str:
        """Generate text report"""
        analysis = self.analyze_network_health()
        
        report = f"""
🌐 NETWORK REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

📊 SUMMARY:
• Ping Availability: {analysis['summary']['ping_availability']:.1f}%
• HTTP Availability: {analysis['summary']['http_availability']:.1f}%  
• DNS Availability: {analysis['summary']['dns_availability']:.1f}%
• Average Ping Time: {analysis['summary']['avg_ping_time']:.1f}ms
• Average HTTP Time: {analysis['summary']['avg_http_time']:.1f}ms
• Average DNS Time: {analysis['summary']['avg_dns_time']:.1f}ms

🎯 RECOMMENDATIONS:
"""
        
        # Recommendations based on metrics
        recommendations = []
        
        if analysis['summary']['ping_availability'] < 80:
            recommendations.append("🔧 Check network connection and firewall")
        
        if analysis['summary']['http_availability'] < 100:
            recommendations.append("🌐 Check internal services availability")
        
        if analysis['summary']['avg_http_time'] > 1000:
            recommendations.append("⚡ Optimize application performance")
        
        if analysis['summary']['dns_availability'] < 100:
            recommendations.append("🔍 Check DNS settings")
        
        if not recommendations:
            recommendations.append("✅ Network infrastructure running stable")
        
        report += "\n".join([f"• {rec}" for rec in recommendations])
        report += f"\n\n⏰ Services checked: {analysis['summary']['total_checks']}"
        
        return report


# Bridge integration
def add_network_to_bridge():
    """Add network analysis to bridge"""
    try:
        from monitoring_bridge import bridge
        
        # Add method to bridge (dynamically)
        if not hasattr(bridge, 'network_analyzer'):
            bridge.network_analyzer = NetworkAnalyzer()
        
        def get_network_metrics(self):
            return self.network_analyzer.analyze_network_health()
        
        # Add method to bridge
        import types
        bridge.get_network_metrics = types.MethodType(get_network_metrics, bridge)
        
        print("✅ Network analyzer integrated with bridge")
        
    except Exception as e:
        print(f"❌ Network integration failed: {e}")


if __name__ == "__main__":
    analyzer = NetworkAnalyzer()
    print(analyzer.generate_network_report())
    
    # Bridge integration
    add_network_to_bridge()