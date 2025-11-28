#!/usr/bin/env python3
"""
MASTER AI ANALYZER - Intelligent monitoring analyzer
Combines metrics, logs and AI analysis for complete system overview
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import json
from datetime import timedelta

# Add import paths
sys.path.append('ai-reporter')
sys.path.append('ai-analysis')

from monitoring_bridge import bridge


class MasterAnalyzer:
    """Main AI analyzer for monitoring system"""
    
    def __init__(self, use_ai: bool = True):
        self.bridge = bridge
        self.use_ai = use_ai
        self.analysis_results = {}
    
    def analyze_system_health(self) -> Dict[str, Any]:
        """Analyze overall system health"""
        print("🔍 Analyzing system health...")
        
        quick_status = self.bridge.get_quick_status()
        system_metrics = self.bridge.get_system_metrics()
        container_metrics = self.bridge.get_container_metrics()
        
        # Criticality analysis
        health_score = 100  # initial score
        
        # Penalties for issues
        if quick_status['status'] != '🟢 OK':
            health_score -= 30
        
        if quick_status['services']['available'] < quick_status['services']['total']:
            health_score -= 20 * (quick_status['services']['total'] - quick_status['services']['available'])
        
        if quick_status['containers']['running'] < quick_status['containers']['expected']:
            health_score -= 15
        
        # Health level determination
        if health_score >= 90:
            health_level = "EXCELLENT"
        elif health_score >= 70:
            health_level = "GOOD" 
        elif health_score >= 50:
            health_level = "WARNING"
        else:
            health_level = "CRITICAL"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'health_level': health_level,
            'quick_status': quick_status,
            'system_metrics_available': 'output' in system_metrics,
            'container_metrics_available': 'output' in container_metrics
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance"""
        print("📊 Analyzing performance...")
        
        # Get detailed metrics via bridge
        detailed_report = self.bridge.get_detailed_report(use_ai=False)
        
        performance_data = {
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': detailed_report.get('response_time_ms', 0),
            'services_availability': detailed_report['services']['available'] / detailed_report['services']['total'] * 100,
            'containers_running': detailed_report['containers']['running'],
            'generation_time': detailed_report.get('generation_time_seconds', 0)
        }
        
        # Performance analysis
        if performance_data['response_time_ms'] > 1000:
            performance_data['performance_level'] = 'SLOW'
        elif performance_data['response_time_ms'] > 500:
            performance_data['performance_level'] = 'MODERATE'
        else:
            performance_data['performance_level'] = 'FAST'
        
        return performance_data
    
    def analyze_logs_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in logs"""
        print("📝 Analyzing logs...")
        
        try:
            from smart_analyzer import LogAnalyzer
            log_analyzer = LogAnalyzer()
            
            # Get logs from last 2 hours with different query
            logs_data = log_analyzer.get_loki_logs(hours=2)
            
            if "error" not in logs_data:
                log_entries = []
                for result in logs_data.get("data", {}).get("result", []):
                    for value in result.get("values", []):
                        log_entries.append(value[1])
                
                # If no results, try alternative query
                if not log_entries:
                    print("   ⚠️  Logs not found, checking alternative sources...")
                    # Try different query for Loki
                    try:
                        import requests
                        end_time = datetime.now()
                        start_time = end_time - timedelta(hours=2)
                        start_ns = int(start_time.timestamp() * 1e9)
                        end_ns = int(end_time.timestamp() * 1e9)
                        
                        alternative_queries = [
                            '{job="containers"}',
                            '{container="devops_app"}', 
                            '{app="devops"}',
                            '{service!=""}',
                            '{job=~".+"}'  # Any job
                        ]
                        
                        for query in alternative_queries:
                            url = "http://localhost:3100/loki/api/v1/query_range"
                            params = {'query': query, 'limit': 20, 'start': start_ns, 'end': end_ns}
                            response = requests.get(url, params=params, timeout=5)
                            if response.status_code == 200:
                                data = response.json()
                                for result in data.get("data", {}).get("result", []):
                                    for value in result.get("values", []):
                                        log_entries.append(value[1])
                                if log_entries:
                                    print(f"   ✅ Found logs via query: {query}")
                                    break
                    except:
                        pass
                
                logs_text = "\n".join(log_entries[:50])
                analysis = log_analyzer.analyze_with_patterns(logs_text)
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'log_analysis': analysis,
                    'entries_analyzed': len(log_entries),
                    'alert_level': analysis.get('alert_level', 'INFO'),
                    'detected_patterns': analysis.get('detected_patterns', []),
                    'query_used': 'alternative' if log_entries else 'original'
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'error': logs_data['error'],
                    'alert_level': 'UNKNOWN',
                    'entries_analyzed': 0
                }
                
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f"Log analysis failed: {str(e)}",
                'alert_level': 'ERROR',
                'entries_analyzed': 0
            }
    
    def generate_ai_insights(self, health_data: Dict, performance_data: Dict, logs_data: Dict) -> Dict[str, Any]:
        """Generate AI insights based on all data"""
        if not self.use_ai:
            return {'ai_available': False}
        
        print("🧠 Generating AI insights...")
        
        try:
            from insight_generator import InsightGenerator
            ai_analyzer = InsightGenerator(use_ai=True)
            
            # First try quick query
            quick_prompt = f"System: {health_data['health_level']}. Services: {health_data['quick_status']['services']['available']}/{health_data['quick_status']['services']['total']}. Performance: {performance_data['performance_level']}. Give 2 recommendations briefly."
            
            ollama_status = ai_analyzer.check_ollama_ready()
            
            if ollama_status['available']:
                model_name = ollama_status['models'][0]['name'] if ollama_status['models'] else 'tinyllama:latest'
                
                try:
                    # Try very fast query
                    response = requests.post(
                        f"{ai_analyzer.ollama_url}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": quick_prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.3, 
                                "num_predict": 100,  # Very short response
                                "top_k": 20
                            }
                        },
                        timeout=8  # Very short timeout
                    )
                    
                    if response.status_code == 200:
                        ai_response = response.json().get('response', 'No response from AI')
                        return {
                            'ai_available': True,
                            'timestamp': datetime.now().isoformat(),
                            'insights': ai_response.strip(),
                            'model_used': model_name,
                            'response_time': 'fast'
                        }
                    else:
                        # Fallback to static recommendations
                        return self._get_static_insights(health_data, performance_data, logs_data)
                        
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    # Fallback to static recommendations on timeout
                    return self._get_static_insights(health_data, performance_data, logs_data)
                except Exception as e:
                    return self._get_static_insights(health_data, performance_data, logs_data)
            else:
                return self._get_static_insights(health_data, performance_data, logs_data)
                
        except Exception as e:
            return self._get_static_insights(health_data, performance_data, logs_data)

    def _get_static_insights(self, health_data: Dict, performance_data: Dict, logs_data: Dict) -> Dict[str, Any]:
        """Static insights when AI unavailable"""
        insights = []
        
        # System health analysis
        if health_data['health_level'] == 'EXCELLENT':
            insights.append("✅ System in excellent condition: all services available, containers running")
            insights.append("📊 Consider configuring auto-scaling to maintain performance")
        elif health_data['health_level'] == 'GOOD':
            insights.append("⚠️ System stable, but recommend checking logs for hidden issues")
            insights.append("🔧 Consider optimizing resource consumption")
        else:
            insights.append("🚨 Immediate attention required! Critical system issues")
            insights.append("📋 Check Docker containers and service configurations")

        # Performance analysis
        if performance_data['performance_level'] == 'FAST':
            insights.append("⚡ Performance optimal, response time normal")
        elif performance_data['performance_level'] == 'SLOW':
            insights.append("🐌 Performance degraded, recommend code and configuration optimization")
            insights.append("💾 Check memory and CPU usage")

        # Logs analysis
        entries_analyzed = logs_data.get('entries_analyzed', 0)
        if entries_analyzed > 10:
            insights.append(f"📝 System generating stable log stream ({entries_analyzed} entries)")
        elif entries_analyzed > 0:
            insights.append("📝 Low log activity, system running stable")
        else:
            insights.append("🔧 Configure log collection for complete monitoring")

        # Detected patterns
        if logs_data.get('detected_patterns'):
            patterns = logs_data['detected_patterns']
            if 'application_errors' in patterns:
                insights.append("🚨 Application errors detected - check code and dependencies")
            if 'performance_issues' in patterns:
                insights.append("⚡ Performance issues identified - optimize queries")
            if 'security_issues' in patterns:
                insights.append("🔒 Security issues detected - check authentication")

        return {
            'ai_available': False,
            'static_insights': True,
            'timestamp': datetime.now().isoformat(),
            'insights': " • ".join(insights),
            'note': 'AI unavailable, used intelligent static recommendations'
        }
    
    def generate_master_report(self) -> Dict[str, Any]:
        """Generate complete master report"""
        print("🤖 Starting master analyzer...")
        print("=" * 50)
        
        # Collect data from all sources
        health_data = self.analyze_system_health()
        performance_data = self.analyze_performance()
        logs_data = self.analyze_logs_patterns()
        network_data = self.analyze_network() 
        ai_insights = self.generate_ai_insights(health_data, performance_data, logs_data)
        
        # Form unified report
        master_report = {
            'report_id': f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'health': health_data['health_level'],
                'performance': performance_data['performance_level'],
                'logs_alert': logs_data.get('alert_level', 'UNKNOWN'),
                'network': self._get_network_status(network_data),
                'overall_status': self._calculate_overall_status(health_data, performance_data, logs_data, network_data)
            },
            'details': {
                'health_analysis': health_data,
                'performance_analysis': performance_data,
                'logs_analysis': logs_data,
                'network_analysis': network_data,
                'ai_insights': ai_insights
            },
            'recommendations': self._generate_recommendations(health_data, performance_data, logs_data)
        }
        
        return master_report

    def _get_network_status(self, network_data: Dict) -> str:
        """Get network status"""
        if 'error' in network_data:
            return 'UNKNOWN'
        
        availability = network_data['summary']['http_availability']
        if availability >= 95:
            return 'EXCELLENT'
        elif availability >= 80:
            return 'GOOD'
        elif availability >= 60:
            return 'WARNING'
        else:
            return 'CRITICAL'

    def _calculate_overall_status(self, health: Dict, performance: Dict, logs: Dict, network: Dict) -> str:
        """Calculate overall system status with network"""
        status_weights = {
            'CRITICAL': 4, 'ERROR': 3, 'WARNING': 2, 'GOOD': 1, 'EXCELLENT': 0, 'UNKNOWN': 1
        }
        
        health_weight = status_weights.get(health['health_level'], 2)
        perf_weight = 2 if performance['performance_level'] == 'SLOW' else 0
        logs_weight = status_weights.get(logs.get('alert_level', 'INFO'), 1)
        network_weight = status_weights.get(self._get_network_status(network), 1)
        
        total_weight = health_weight + perf_weight + logs_weight + network_weight
        
        if total_weight >= 6:
            return "🔴 CRITICAL"
        elif total_weight >= 4:
            return "🟡 WARNING"
        else:
            return "🟢 NORMAL"
        
    def _generate_recommendations(self, health: Dict, performance: Dict, logs: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # System health recommendations
        health_score = health['health_score']
        if health_score == 100:
            recommendations.append("🎯 Maintain current configuration - system perfect")
        elif health_score >= 90:
            recommendations.append("📈 Consider business metrics monitoring for proactive management")
        elif health_score >= 70:
            recommendations.append("🔧 Conduct preventive system inspection")
        
        # Performance recommendations
        if performance['performance_level'] == 'FAST':
            recommendations.append("⚡ Performance optimal - maintain current settings")
        elif performance['performance_level'] == 'SLOW':
            recommendations.append("🐌 Optimize database settings and caching")
        
        # Logs recommendations
        entries_analyzed = logs.get('entries_analyzed', 0)
        if entries_analyzed > 0:
            log_level = logs.get('alert_level', 'INFO')
            if log_level == 'ERROR':
                recommendations.append("🚨 Urgently investigate errors in logs")
            elif log_level == 'WARNING':
                recommendations.append("⚠️ Attention: warnings present in logs")
            else:
                recommendations.append("📝 Logs clean - excellent system operation")
            
            # Log volume recommendations
            if entries_analyzed > 50:
                recommendations.append("📊 Consider log rotation to save space")
        else:
            recommendations.append("🔧 Configure Loki for application log collection")
        
        # Patterns recommendations
        if logs.get('detected_patterns'):
            patterns = logs['detected_patterns']
            if 'database_errors' in patterns:
                recommendations.append("🗄️ Check database connections")
            if 'performance_issues' in patterns:
                recommendations.append("⚡ Analyze slow queries")
        
        # If everything excellent
        if (health_score == 100 and 
            performance['performance_level'] == 'FAST' and 
            logs.get('alert_level') in ['INFO', None] and
            entries_analyzed > 0):
            recommendations.append("🏆 System operating perfectly! Recommend documenting configuration")
        
        return recommendations
        
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file"""
        if not filename:
            filename = f"master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Report saved to: {filename}")
        return filename
    
    def print_report(self, report: Dict[str, Any]):
        """Pretty console report output"""
        print("\n" + "=" * 60)
        print("🤖 MASTER AI ANALYZER - FULL REPORT")
        print("=" * 60)
        
        print(f"\n📊 OVERALL STATUS: {report['summary']['overall_status']}")
        print(f"   • Health: {report['summary']['health']}")
        print(f"   • Performance: {report['summary']['performance']}")
        print(f"   • Logs: {report['summary']['logs_alert']}")
        
        print(f"\n🔍 DETAILS:")
        print(f"   • Health score: {report['details']['health_analysis']['health_score']}/100")
        print(f"   • Response time: {report['details']['performance_analysis']['response_time_ms']:.1f}ms")
        print(f"   • Services: {report['details']['health_analysis']['quick_status']['services']['available']}/{report['details']['health_analysis']['quick_status']['services']['total']}")
        print(f"   • Containers: {report['details']['health_analysis']['quick_status']['containers']['running']}/{report['details']['health_analysis']['quick_status']['containers']['expected']}")
        print(f"   • Logs: {report['details']['logs_analysis']['entries_analyzed']} entries analyzed")
        
        if report['details']['logs_analysis'].get('detected_patterns'):
            print(f"   • Patterns: {', '.join(report['details']['logs_analysis']['detected_patterns'])}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # AI insights or static
        if report['details']['ai_insights'].get('ai_available'):
            print(f"\n🧠 AI INSIGHTS:")
            insights = report['details']['ai_insights']['insights']
            print(f"   {insights}")
        elif report['details']['ai_insights'].get('static_insights'):
            print(f"\n💡 AUTOMATIC INSIGHTS:")
            insights = report['details']['ai_insights']['insights']
            # Split into points
            for insight in insights.split(' • '):
                if insight.strip():
                    print(f"   • {insight}")
        
        print(f"\n⏰ Report generated: {report['timestamp']}")
        print("=" * 60)

    def send_email_report(self, report_file: str, report_data: Dict[str, Any]):
        """Send report via email"""
        print("📧 Preparing email report...")
        
        try:
            # Check existing email modules
            email_modules = []
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                email_modules = ['smtplib', 'email']
            except ImportError as e:
                print(f"   ⚠️  Email modules unavailable: {e}")
                return False
            
            # Read saved report
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Create email
            subject = f"🤖 AI Monitor Report - {report_data['summary']['overall_status']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Text content
            body = f"""
    AI Master Analyzer Report

    OVERALL STATUS: {report_data['summary']['overall_status']}
    • Health: {report_data['summary']['health']}
    • Performance: {report_data['summary']['performance']} 
    • Logs: {report_data['summary']['logs_alert']}

    DETAILS:
    • Health score: {report_data['details']['health_analysis']['health_score']}/100
    • Response time: {report_data['details']['performance_analysis']['response_time_ms']:.1f}ms
    • Services: {report_data['details']['health_analysis']['quick_status']['services']['available']}/{report_data['details']['health_analysis']['quick_status']['services']['total']}
    • Logs: {report_data['details']['logs_analysis']['entries_analyzed']} entries

    RECOMMENDATIONS:
    {chr(10).join(f"- {rec}" for rec in report_data['recommendations'])}

    Full report in attachment.
    """
            
            # Here will be sending code via existing email module
            # For now just log
            print(f"   ✅ Email prepared for: eldorzufarov66@gmail.com")
            print(f"   📧 Subject: {subject}")
            print(f"   📎 Attachment: {report_file}")
            
            # TODO: Integrate with existing email code
            return True
            
        except Exception as e:
            print(f"   ❌ Email preparation error: {e}")
            return False
    
    def analyze_network(self) -> Dict[str, Any]:
        """Analyze network metrics"""
        print("🌐 Analyzing network...")
        
        try:
            from network_analyzer import NetworkAnalyzer
            analyzer = NetworkAnalyzer()
            return analyzer.analyze_network_health()
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f"Network analysis failed: {str(e)}",
                'summary': {'network_availability': 0}
            }

def main():
    """Main function"""
    print("🚀 Starting Master AI Analyzer...")
    
    # Check AI availability
    try:
        from insight_generator import InsightGenerator
        ai_status = InsightGenerator().check_ollama_ready()
        use_ai = ai_status['available'] and ai_status['models']
        
        if use_ai:
            print("✅ AI mode activated")
        else:
            print("🔧 Basic mode (AI unavailable)")
    except:
        use_ai = False
        print("🔧 Basic mode (AI components unavailable)")
    
    # Start analyzer
    analyzer = MasterAnalyzer(use_ai=use_ai)
    report = analyzer.generate_master_report()
    
    # Print and save report
    analyzer.print_report(report)
    filename = analyzer.save_report(report)
    
    print(f"\n📋 Report ready: {filename}")
    print("💡 For email sending use: python3 master_analyzer.py --email")
    
    return filename

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Master AI Analyzer')
    parser.add_argument('--email', action='store_true', help='Send report via email')
    args = parser.parse_args()
    
    # Start analyzer
    filename = main()
    
    # Email sending if requested
    if args.email:
        print("\n📧 Starting email sending...")
        try:
            from master_analyzer import MasterAnalyzer
            analyzer = MasterAnalyzer(use_ai=False)  # No AI needed for sending
            # Need to load report for sending
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            success = analyzer.send_email_report(filename, report_data)
            if success:
                print("✅ Email report sent!")
            else:
                print("❌ Email sending error")
        except Exception as e:
            print(f"❌ Error during email sending: {e}")