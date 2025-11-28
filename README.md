# Universal AI Monitoring & Analytics Platform

A complete, self-adapting monitoring solution with AI-powered analytics. Successfully tested with MiniShop and ready for any application. Features automatic service discovery, intelligent dashboards, and unified script management.

## 🚀 Overview

This project provides a **universal monitoring platform** that automatically adapts to any application. Successfully tested with MiniShop integration, it features:

- **Self-discovery**: Automatically detects new applications and their metrics
- **AI-powered analytics**: Proactive issue detection and insights
- **Unified management**: Single control point for all scripts and components
- **Real-time monitoring**: Live metrics, logs, and intelligent dashboards
- **Self-healing**: Automatic problem detection and fixing
- **Universal compatibility**: Works with any application out of the box

## 📋 System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER 	   				      │
│ ┌─────────────────┐ ┌─────────────────┐     		      │
│ │ MiniShop 	    │ │ Any App		│ 		      │
│ │ (Tested)   	    │ │ (Universal)	│ 		      │
│ └─────────────────┘ └─────────────────┘ 		      │
└─────────────────┬─────────────────────┬─────────────────────┘
		  │ 			│
		  ▼ 			▼
┌─────────────────────────────────────────────────────────────┐
│ AUTODISCOVERY & MONITORING 		  		      │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  	      │
│ │ Prometheus 	│ │ Loki 	│ │ Auto-Detect │ 	      │
│ │ Metrics 	│ │ Logs 	│ │ Problems 	│ 	      │
│ └─────────────┘ └─────────────┘ └─────────────┘ 	      │
└───────────────────────────────┬─────────────────────────────┘
				│
				▼
		   ┌─────────────────────────┐
		   │ UNIFIED MANAGEMENT      │
		   │ script_manager.py       │
		   │ ⭐ CENTRAL HUB 	     │
		   └─────────────────────────┘
			        │
	    ┌───────────────────┼───────────────────┐
	    │ 	  	        │ 		    │
	    ▼ 		        ▼ 	            ▼
   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │ CONTROL & 	     │ │ AI ANALYTICS    │ │ SELF-HEALING    │
   │ DASHBOARDS      │ │ & INSIGHTS      │ │ & AUTOMATION    │
   ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
   │ • control_panel │ │ • master_       │ │ • auto_detector │
   │ .sh 	     │ │ analyzer.py     │ │ .py	     │
   │ • Grafana 	     │ │ • smart_        │ │ • fix_*.py      │
   │ Dashboards	     │ │ analyzer.py     │ │ • universal_    │
   │ • Real-time     │ │ • AI Insights   │ │ dashboard_      │
   │ Monitoring      │ │ • Email Reports │ │ fixer.py	     │
   └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### How It Works:

1. **Applications** → Any app (MiniShop tested, others work automatically)
   - Sends: Metrics + Logs

2. **Auto-Discovery** → System automatically finds and monitors apps
   - **Prometheus**: Collects application metrics
   - **Loki**: Collects application logs  
   - **Auto-Detect**: Finds problems automatically

3. **Unified Management** → `script_manager.py` controls everything
   - Single command for all operations
   - Central hub for all scripts and tools

4. **Three Output Channels**:
   - **Control & Dashboards**: Human interface (control panels, Grafana)
   - **AI Analytics**: Intelligent analysis and insights
   - **Self-Healing**: Automatic problem detection and fixing

**Key Innovation**: Instead of separate tools, everything connects through `script_manager.py` - one command to rule them all!

## 🏗️ Project Structure
```
mini-shop-integration-test/
├── 📊 MONITORING INFRASTRUCTURE
│ ├── docker-compose.yml # Complete service stack
│ ├── monitoring/
│ │ ├── prometheus.yml # Metrics collection
│ │ ├── alert_rules.yml # Alert configuration
│ │ └── grafana/
│ │ ├── dashboards/ # 8+ adaptive dashboards
│ │ └── provisioning/ # Auto-configuration
│ └── logs/
│ ├── loki.yml # Log aggregation
│ └── promtail.yml # Log shipping
├── 🎯 APPLICATION (MiniShop)
│ ├── backend/
│ │ ├── app.py # Flask application
│ │ ├── Dockerfile # Container definition
│ │ └── requirements.txt # Python dependencies
│ └── db/
│ └── init.sql # Database initialization
├── 🤖 AI ANALYTICS CORE
│ ├── script_manager.py # ⭐ UNIFIED SCRIPT MANAGEMENT
│ ├── master_analyzer.py # Complete AI analysis
│ ├── monitoring_bridge.py # Universal data bridge
│ ├── ai-analysis/
│ │ └── smart_analyzer.py # Log analysis AI
│ └── ai-reporter/
│ └── insight_generator.py # Metrics analysis AI
├── 🔧 DIAGNOSTICS & AUTOMATION
│ ├── diagnostics/ # Complete diagnostics suite
│ │ ├── auto_detector.py # Auto problem detection
│ │ ├── check_.py # Health check scripts
│ │ ├── fix_.py # Auto-fix scripts
│ │ ├── control_panel.sh # Main control panel
│ │ └── universal_dashboard_fixer.py
│ └── scripts/
│ ├── metrics_system.sh # System metrics
│ └── metrics_containers.sh # Container metrics
├── ⚡ QUICK COMMANDS
│ ├── quick_check.sh # Fast health check (<3s)
│ └── quick_ai_check.sh # Fast AI analysis
├── ⚙️ CONFIGURATION
│ ├── .env # Environment variables
│ └── .gitignore
└── 🔄 CI/CD
└── .github/workflows/
└── ci-cd.yml # GitHub Actions
```

## 🔧 Core Components

### 1. 🎯 Unified Management System

**`script_manager.py` - ⭐ SINGLE COMMAND FOR EVERYTHING**
```bash
# One command to rule them all
python3 script_manager.py list          # 📋 List all available scripts
python3 script_manager.py check         # 🔍 Run all check scripts
python3 script_manager.py fix           # 🔧 Run all fix scripts  
python3 script_manager.py run <script>  # 🚀 Run any specific script

# Examples:
python3 script_manager.py run auto_detector.py
python3 script_manager.py run check_panels.py
python3 script_manager.py run control_panel.sh
```
### 2. 🎮 Control & Monitoring

`control_panel.sh` - Main dashboard with:

- Service health checks (HTTP)
- Docker container status
- Business metrics monitoring
- System resource tracking
- AI bridge integration
- Real-time status updates

`quick_check.sh` - Ultra-fast diagnostics (< 3 seconds)

- Critical services only
- Minimal resource usage
- Perfect for CI/CD pipelines

`quick_ai_check.sh` - Fast AI-powered status

- Bridge-based analysis
- Smart recommendations
- Color-coded output

### 3. 🤖 AI Analytics Engine

`master_analyzer.py` - Complete AI analysis system

- Combines metrics, logs, and system status
- Generates comprehensive health reports
- Provides intelligent recommendations
- Email reporting capabilities

`monitoring_bridge.py` - Universal data bridge
```
# Single API for all monitoring data
bridge.get_quick_status()      # ⚡ Fast system status (<100ms)
bridge.get_detailed_report()   # 📈 Full analysis with AI insights
```
`auto_detector.py` - Automatic problem detection
- Proactively identifies issues
- Suggests appropriate fix scripts
- Works with any application
### 4. 🔧 Diagnostics & Automation

#### Self-Healing System:

- `auto_detector.py` - Finds problems automatically
- `universal_dashboard_fixer.py` - Fixes dashboard queries
- `fix_*.py scripts` - Automated repairs
- `check_*.py scripts` - Comprehensive health checks

#### Network Analysis:

- `network_analyzer.py` - Complete network health monitoring
- Ping, HTTP, and DNS checks
- Performance recommendations

## 🚀 Quick Start
### 1. Start the System
```
# Start all services
docker compose up -d

# Check status
./control_panel.sh

# Or use quick check
./quick_check.sh
```
### 2. Unified Management
```
# 📋 See all available scripts
python3 script_manager.py list

# 🔍 Run all health checks
python3 script_manager.py check

# 🔧 Run all fix scripts
python3 script_manager.py fix

# 🚀 Run specific script
python3 script_manager.py run auto_detector.py
```

### 3. AI Analysis
```
# Fast AI status
./quick_ai_check.sh

# Complete AI report
python3 master_analyzer.py

# Report with email
python3 master_analyzer.py --email
```
### 4. Access Dashboards
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Application: http://localhost:5000
- Loki: http://localhost:3100

## 🎯 Key Features
### 🧠 AI-Powered Analytics
- **Smart Detection**: Automatic problem identification
- **Intelligent Insights**: AI-generated recommendations
- **Pattern Recognition**: Log and metric pattern analysis
- **Predictive Analysis**: Proactive issue prevention

### 🔧 Self-Healing Capabilities
- **Auto-Discovery**: Detects new applications automatically
- **Adaptive Dashboards**: Self-configuring Grafana panels
- **Problem Resolution**: Suggests and runs fix scripts
- **Universal Compatibility**: Works with any application

### ⚡ Performance Optimized
- **Quick Checks**: < 3 second health verification
- **Lazy Loading**: AI components load only when needed
- **Real-time Updates**: Live data streaming
- **Resource Efficient**: Minimal system footprint

### 🎮 Unified Management
- **Single Interface**: One command for all operations
- **Script Centralization**: All tools in one place
- **Automated Workflows**: Pre-defined check/fix sequences
- **Extensible Architecture**: Easy to add new components

## 📊 Application Monitoring
### Universal Application Support

The system automatically adapts to any application with zero configuration:
```
# Works with any application exposing metrics
# Auto-detects: Flask, Django, Node.js, Java, etc.
# Supports: Prometheus metrics, health endpoints, custom business metrics
```

### MiniShop Integration Example

Successfully tested with MiniShop application:
```
# Metrics automatically discovered:
minishop_requests_total
minishop_errors_total
minishop_products_total  
minishop_request_latency_seconds
minishop_business_orders_total
```
### Health Check Integration
```
# Application health endpoints monitored:
http://localhost:5000/health
http://localhost:5000/metrics
http://localhost:5000/          # Main endpoint
```

### Business Metrics Tracking

```
# Real-time business intelligence:
- Total requests and error rates
- Product inventory and sales
- User activity and orders
- Performance latency metrics
- Custom business KPIs
```
## 📈 Adaptive Dashboards
### Self-Configuring Grafana Dashboards
The system includes 8+ intelligent dashboards that automatically adapt:

#### Core Dashboards:

- `App Metrics` - Application performance metrics
- `MiniShop Metrics` - Business-specific monitoring
- `Application Logs` - Real-time log analysis
- `Infrastructure Metrics` - System resource monitoring
- `AI Analysis` - AI-powered insights and patterns
- `System Health` - Human - Simple, understandable status
- `Business Simple` - Business KPIs and metrics
- `Universal Container Logs` - Auto-detected container logs

### Smart Dashboard Features
```
# Automatic adaptation:
- Detects new metric prefixes (app_*, minishop_*, etc.)
- Updates queries automatically
- Creates universal dashboards for new applications
- Fixes broken panels in real-time
```

### Universal Dashboard Fixer
```
# Automatically repairs dashboard issues:
python3 universal_dashboard_fixer.py

# Features:
- Auto-detects running containers
- Finds working Loki log queries
- Updates outdated metric references
- Creates universal log dashboards
```

## 💡 Examples & Use Cases
### 1. Quick System Check
```
# ⚡ Fast health verification (<3 seconds)
./quick_check.sh

# Output:
# Services: 4/4 ✅
# Containers: 7/7 🐳
# Status: 🟢 OK
```

### 2. Complete AI Analysis
```
# 🤖 Full system analysis with AI insights
python3 master_analyzer.py

# Output includes:
# - Health score (0-100)
# - Performance analysis
# - Log pattern detection
# - AI recommendations
# - Network health status
```
### 3. Automated Problem Solving
```
# 🔧 Let the system diagnose and fix issues
python3 script_manager.py check
python3 script_manager.py fix

# Or use auto-detector directly:
python3 auto_detector.py
```

### 4. Real-time Business Monitoring
```
# 📊 Monitor business metrics in real-time
./control_panel.sh

# Shows:
# - Business request volumes
# - Error rates and patterns
# - Product inventory changes
# - User activity trends
```
### 5. Network Health Analysis
```
# 🌐 Comprehensive network diagnostics
python3 network_analyzer.py

# Monitors:
# - Service response times
# - DNS resolution performance
# - Internal service connectivity
# - External service availability
```
## ⚙️ Configuration
### Environment Variables
Create `.env` file:
```
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
# Add application-specific variables as needed
```

### Resource Allocation
Optimized Docker resource limits:
```
| Service       | Memory Limit | CPU Cores |
|---------------|--------------|-----------|
| Application   | 256MB        | 0.5       |
| Prometheus    | 512MB        | 1.0       |
| Grafana       | 256MB        | 0.5       |
| Loki          | 192MB        | 0.3       |
| Promtail      | 128MB        | 0.2       |
```

### Customizing for New Applications
```
# The system automatically detects:
# - Any application exposing /metrics endpoint
# - Any container with business metrics
# - Any service with health check endpoints

# Manual configuration (if needed):
# 1. Update prometheus.yml scrape configs
# 2. Add custom dashboards to grafana/provisioning
# 3. Define alert rules in monitoring/alert_rules.yml
```

## 🛠️ Troubleshooting
### Quick Diagnostics
```
# 1. Check all services quickly
./quick_check.sh

# 2. Run comprehensive diagnostics
python3 script_manager.py check

# 3. Auto-detect and fix issues
python3 script_manager.py fix
```

### Common Issues & Solutions
#### Issue: No metrics in Grafana
```
# Solution: Check Prometheus configuration
python3 check_prometheus.py
python3 fix_dashboards.py
```

### Issue: Logs not showing in Loki
```
# Solution: Debug log collection
python3 check_promtail_port.py
python3 fix_loki_logs.py
python3 deep_promtail_debug.py
```
### Issue: Dashboard panels broken
```
# Solution: Auto-fix dashboard queries
python3 universal_dashboard_fixer.py
python3 fix_grafana_datasource.py
```

### Issue: Application not monitored
```
# Solution: Auto-detect and configure
python3 auto_detector.py
python3 script_manager.py run fix_prometheus.py
```

### Manual Debugging Commands
```
# Check individual components:
python3 check_grafana.py
python3 check_dashboards.py
python3 check_panels.py

### # Deep diagnostics:
python3 deep_promtail_debug.py
python3 final_fixes.py
```
## 🔌 API Reference
### Monitoring Bridge API
```
from monitoring_bridge import bridge

# ⚡ Quick system status (<100ms)
status = bridge.get_quick_status()
# Returns: services, containers, response time, overall status

# 📊 System metrics
metrics = bridge.get_system_metrics()
# Returns: CPU, memory, disk, network metrics

# 🐳 Container metrics
containers = bridge.get_container_metrics()
# Returns: Docker container status and resources

# 📈 Detailed AI report
report = bridge.get_detailed_report(use_ai=True)
# Returns: Complete analysis with AI insights
```
### Master Analyzer API
```
from master_analyzer import MasterAnalyzer

analyzer = MasterAnalyzer(use_ai=True)

# Generate complete report
report = analyzer.generate_master_report()
# Includes: health, performance, logs, network, AI insights

# Save and email report
filename = analyzer.save_report(report)
analyzer.send_email_report(filename, report)
```

### Network Analyzer API
```
from network_analyzer import NetworkAnalyzer

analyzer = NetworkAnalyzer()
network_health = analyzer.analyze_network_health()
# Returns: ping, HTTP, DNS metrics and availability
```
## 🚀 Deployment
### Local Development
```
# 1. Clone and setup
git clone <repository>
cd mini-shop-integration-test

# 2. Start services
docker compose up -d

# 3. Verify deployment
./deploy-local.sh
./control_panel.sh
```

### Production Deployment
```
# docker-compose.yml is production-ready with:
- Health checks for all services
- Resource limits and reservations
- Proper service dependencies
- Persistent data volumes
- Security best practices
```

### CI/CD Integration
```
# GitHub Actions workflow included:
# - Automated testing
# - Docker image building
# - Deployment validation
# - Health check verification
```

### Monitoring in Production
```
# Use quick checks for health monitoring
./quick_check.sh
# Returns exit code 0 for healthy, 1 for issues

# Integrate with monitoring systems:
python3 master_analyzer.py --email
# Send automated reports to operations team
```
## 📈 Performance Characteristics
### Response Times
- **Quick Check**: < 3 seconds
- **AI Quick Check**: < 5 seconds
- **Full AI Analysis**: 10-30 seconds
- **Real-time Metrics**: < 100ms updates

### Resource Usage
- **Memory**: < 1GB total for all services
- **CPU: Minimal overhead (< 5% typical)
- **Storage**: Efficient log and metric retention
- **Network**: Optimized data collection

## 🎯 Use Cases
### Development Teams
- Real-time application debugging
- Performance optimization
- Automated testing integration
- Local development monitoring

### Operations Teams
- Production health monitoring
- Incident detection and response
- Capacity planning
- Business metrics tracking

### Business Teams
- Real-time KPI monitoring
- Customer activity insights
- Sales and inventory tracking
- Performance trend analysis

## 🔮 Future Enhancements
### Planned Features
- **Predictive Analytics**: ML-based anomaly detection
- **Auto-scaling**: Resource-based scaling recommendations
- **Multi-tenant Support**: Multiple application instances
- **Advanced AI**: Natural language query interface
- **Mobile Dashboard**: Real-time mobile monitoring

### Integration Points
- **Slack/Teams**: Real-time alerts and notifications
- **PagerDuty**: Incident management integration
- **Data Warehouses**: Long-term metric storage
- **Custom Applications**: API-based integration

## 👨‍💻 Created by Eldor Zufarov - Senior DevOps & AI Engineer
### 🏆 Project Highlights
- **Enterprise-Grade**: Production-ready monitoring platform
- **AI-Powered**: Intelligent analytics and automation
- **Universal**: Works with any application out of the box
- **Self-Healing**: Automatic problem detection and resolution
- **Performance Optimized**: Minimal footprint, maximum insight

## 🚀 Why This Project Stands Out
```
🎯 ZERO-CONFIG SETUP → Detects applications automatically
🧠 AI-NATIVE ARCHITECTURE → Built with intelligence at core  
⚡ PERFORMANCE FOCUSED → Lightning-fast checks and analysis
🔧 SELF-HEALING → Fixes issues before they become problems
🌐 UNIVERSAL COMPATIBILITY → Works with any tech stack
```
🎉 GETTING STARTED IS EASY!
```
# 1. Clone and run
git clone <repository>
docker compose up -d

# 2. Check status  
./control_panel.sh

# 3. Let AI do the rest!
python3 script_manager.py check
```
Your applications will be monitored automatically - no configuration needed!

"*Monitoring should be intelligent, automatic, and universal - that's the future we're building.*" - **Eldor Zufarov**

## 🤝 Contributing
We welcome contributions! Please see our contributing guidelines for:

- Code standards and style guide
- Testing requirements
- Documentation updates
- Feature proposal process

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- **Grafana, Prometheus, Loki** - Monitoring infrastructure
- **Docker** - Containerization platform
- **Python AI Ecosystem** - Machine learning components
- **Open Source Community** - Continuous improvement and upport

<div align="center">
⭐ If this project helps you, please give it a star! ⭐
</div> ```




