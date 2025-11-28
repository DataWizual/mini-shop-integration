#!/usr/bin/env python3
"""
AI Insight Reporter - Enhanced version with detailed analysis
"""

import requests
from datetime import datetime, timedelta
import statistics
from typing import Dict, List, Any


class InsightGenerator:
    """AI report generator for monitoring system."""

    def __init__(self, use_ai: bool = True):
        """Initialize report generator."""
        self.prometheus_url = "http://localhost:9090/api/v1"
        self.loki_url = "http://localhost:3100"
        self.grafana_url = "http://localhost:3000"
        self.ollama_url = "http://localhost:11434"
        self.use_ai = use_ai

    def check_ollama_ready(self) -> Dict[str, Any]:
        """Check Ollama readiness with enhanced diagnostics"""
        status = {
            'available': False,
            'models': [],
            'error': None
        }

        try:
            print("🔍 Checking Ollama connection...")
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)

            if response.status_code == 200:
                data = response.json()
                status['available'] = True
                status['models'] = data.get('models', [])
                print(f"✅ Ollama available, models: {[m['name'] for m in status['models']]}")
            else:
                status['error'] = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Ollama response error: {status['error']}")

        except requests.exceptions.ConnectionError:
            status['error'] = "Cannot connect to Ollama server"
            print("❌ Ollama server not running or unavailable")
        except Exception as e:
            status['error'] = str(e)
            print(f"❌ Unexpected error: {e}")

        return status

    def ask_ollama(self, prompt: str) -> str:
        """Query Ollama for AI analysis."""
        ollama_status = self.check_ollama_ready()

        if not ollama_status['available']:
            return f"❌ Ollama unavailable: {ollama_status['error']}"

        if not ollama_status['models']:
            return "❌ No models available in Ollama."

        try:
            # FIX: use first available model name
            model_name = ollama_status['models'][0]['name']
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,  # ← Use actual model name
                    "prompt": (
                        "You are a monitoring system AI analyst. "
                        f"Analyze and provide recommendations in English. {prompt}"
                    ),
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=60  # Increased timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'No response from AI')
            else:
                return f"❌ AI error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ AI temporarily unavailable: {str(e)}"

    def get_prometheus_data(self, query: str) -> List[float]:
        """Fetch data from Prometheus."""
        try:
            end = datetime.now()
            start = end - timedelta(hours=24)

            params = {
                'query': query,
                'start': start.timestamp(),
                'end': end.timestamp(),
                'step': '1h'
            }

            response = requests.get(
                f"{self.prometheus_url}/query_range",
                params=params,
                timeout=10
            )
            data = response.json()

            if data['status'] == 'success' and data['data']['result']:
                values = [
                    float(point[1]) for result in data['data']['result']
                    for point in result.get('values', [])
                ]
                return values
            return []
        except Exception as e:
            print(f"⚠️ Prometheus error ({query}): {e}")
            return []

    def get_container_metrics(self) -> Dict[str, Any]:
        """Get container metrics with dynamic discovery"""
        print("📊 Collecting container metrics...")

        metrics = {}

        # Basic application metrics
        metrics['app_requests'] = self.get_prometheus_data(
            'rate(app_requests_total[1h])'
        ) or [0]  # Protection against empty values

        metrics['app_errors'] = self.get_prometheus_data(
            'rate(app_errors_total[1h])'
        ) or [0]

        # Dynamic container discovery
        metrics['app_memory'] = self.get_prometheus_data(
            'container_memory_usage_bytes{container_label_org_label_schema_group="app"}'
        ) or [0]

        metrics['app_cpu'] = self.get_prometheus_data(
            'rate(container_cpu_usage_seconds_total{container_label_org_label_schema_group="app"}[1h]) * 100'
        ) or [0]

        return metrics

    def analyze_trends(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze trends and anomalies."""
        trends = []

        requests = metrics.get('app_requests', [])
        if len(requests) >= 3:
            recent_avg = statistics.mean(requests[-3:])
            overall_avg = statistics.mean(requests)

            if recent_avg > overall_avg * 1.3:
                trends.append("📈 Growing load: +30% above average")
            elif recent_avg < overall_avg * 0.7:
                trends.append("📉 Load decrease: -30% below average")

        errors = metrics.get('app_errors', [])
        if any(errors) and max(errors) > 0.1:
            trends.append("🔴 Instability: high error rate")

        memory = metrics.get('app_memory', [])
        if memory:
            max_memory_gb = max(memory) / (1024**3)
            if max_memory_gb > 0.5:
                trends.append(
                    f"💾 High memory usage: up to {max_memory_gb:.1f}GB"
                )

        return trends

    def generate_detailed_health_report(
        self, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed system health report."""
        print("🔍 Detailed system analysis...")

        requests = metrics.get('app_requests', [])
        errors = metrics.get('app_errors', [])
        memory = metrics.get('app_memory', [])
        cpu = metrics.get('app_cpu', [])

        total_requests = sum(requests) * 3600 if requests else 0
        total_errors = sum(errors) * 3600 if errors else 0
        if total_requests:
            error_rate = (total_errors / total_requests * 100)
        else:
            error_rate = 0

        avg_rpm = statistics.mean(requests) * 60 if requests else 0
        peak_rpm = max(requests) * 60 if requests else 0

        avg_memory_mb = statistics.mean(memory) / (1024*1024) if memory else 0
        max_memory_mb = max(memory) / (1024*1024) if memory else 0

        avg_cpu_percent = statistics.mean(cpu) * 100 if cpu else 0

        if error_rate > 10:
            status = "🔴 CRITICAL"
        elif error_rate > 5:
            status = "🟡 WARNING"
        else:
            status = "🟢 NORMAL"

        availability = (
            "HIGH" if error_rate < 1
            else "MEDIUM" if error_rate < 5
            else "LOW"
        )

        return {
            'status': status,
            'uptime_percentage': 100 - min(error_rate, 100),
            'total_requests': int(total_requests),
            'total_errors': int(total_errors),
            'error_rate': round(error_rate, 2),
            'avg_rpm': round(avg_rpm, 1),
            'peak_rpm': round(peak_rpm, 1),
            'avg_memory_mb': round(avg_memory_mb, 1),
            'max_memory_mb': round(max_memory_mb, 1),
            'avg_cpu_percent': round(avg_cpu_percent, 1),
            'availability': availability
        }

    def generate_smart_recommendations(
        self, health_data: Dict, trends: List[str]
    ) -> List[str]:
        recommendations = []

        if health_data['max_memory_mb'] > 400:
            rec = "🚨 URGENT: Increase memory_limit to 1GB"
            recommendations.append(rec)
        elif health_data['max_memory_mb'] > 200:
            recommendations.append("💾 Recommended: Increase memory_limit")

        if health_data['peak_rpm'] > 100:
            recommendations.append("⚡ High load: Add replicas")
        elif health_data['peak_rpm'] > 50:
            recommendations.append("📈 Growing load: Monitor closely")

        if health_data['error_rate'] > 5:
            recommendations.append("🔧 Critical errors: Analyze logs")
        elif health_data['error_rate'] > 1:
            recommendations.append("⚠️ Errors detected: Check logs")

        if health_data['avg_cpu_percent'] > 80:
            recommendations.append("🔥 High CPU usage: Optimize code")

        if not recommendations:
            recommendations.append("🎯 System optimized")

        return recommendations

    def generate_report(self) -> str:
        """Generate full report."""
        print("🤖 Generating enhanced AI report...")

        metrics = self.get_container_metrics()
        health_data = self.generate_detailed_health_report(metrics)
        trends = self.analyze_trends(metrics)
        recommendations = self.generate_smart_recommendations(health_data, trends)

        # ENHANCED AI PROCESSING
        ai_analysis = ""
        if self.use_ai:
            ollama_status = self.check_ollama_ready()
            print(f"🔍 Ollama status: {ollama_status}")

            if ollama_status['available'] and ollama_status['models']:
                print("🧠 Running deep AI analysis...")
                
                # Create detailed prompt
                prompt = f"""
    Analyze system metrics and provide recommendations in English:

    STATUS: {health_data['status']}
    REQUESTS: {health_data['total_requests']:,} total
    ERRORS: {health_data['total_errors']} ({health_data['error_rate']}%)
    LOAD: {health_data['avg_rpm']} RPM average, {health_data['peak_rpm']} RPM peak
    MEMORY: {health_data['avg_memory_mb']}MB average, {health_data['max_memory_mb']}MB peak
    CPU: {health_data['avg_cpu_percent']}% average load
    TRENDS: {', '.join(trends) if trends else 'no significant trends'}

    Provide brief analysis and 2-3 main recommendations.
    """
                try:
                    ai_analysis = self.ask_ollama(prompt)
                    # Clean response from extra characters
                    if "❌" not in ai_analysis:
                        ai_analysis = "🤖 " + ai_analysis.strip()
                except Exception as e:
                    ai_analysis = f"❌ AI analysis error: {str(e)}"
            else:
                ai_analysis = f"🤖 AI unavailable: {ollama_status.get('error', 'Unknown error')}"

        report = f"""
🤖 DETAILED SYSTEM REPORT - {datetime.now().strftime('%d %B %Y %H:%M')}
{'='*60}

📊 CURRENT STATUS: {health_data['status']}
• System uptime: {health_data['uptime_percentage']:.1f}%
• Availability level: {health_data['availability']}

📈 PERFORMANCE:
• Total requests: {health_data['total_requests']:,}
• Load: {health_data['avg_rpm']} RPM (peak: {health_data['peak_rpm']} RPM)
• Errors: {health_data['total_errors']} ({health_data['error_rate']}%)

💻 RESOURCES:
• Memory: {health_data['avg_memory_mb']}MB average
• Peak memory: {health_data['max_memory_mb']}MB
• CPU: {health_data['avg_cpu_percent']}% average load
"""

        if trends:
            report += "📊 DETECTED TRENDS:\n"
            for trend in trends:
                report += f"• {trend}\n"
            report += "\n"

        if ai_analysis:
            report += f"🧠 AI ANALYSIS:\n{ai_analysis}\n\n"

        report += "🎯 RECOMMENDATIONS:\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"

        report += f"""
📋 DETAILED METRICS:
{self.grafana_url}/dashboards

💡 Report generated by: AI Insight Reporter v2.0
"""

        return report


def main():
    """Main function."""
    print("🚀 Starting enhanced AI Insight Reporter...")

    ollama_status = InsightGenerator().check_ollama_ready()
    use_ai = ollama_status['available'] and ollama_status['models']

    if use_ai:
        print("✅ AI mode activated")
    else:
        print("🔧 Basic mode (AI unavailable)")

    generator = InsightGenerator(use_ai=use_ai)
    report = generator.generate_report()

    print(report)

    with open('ai-report-detailed.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("\n💾 Detailed report saved to ai-report-detailed.txt")


if __name__ == "__main__":
    main()