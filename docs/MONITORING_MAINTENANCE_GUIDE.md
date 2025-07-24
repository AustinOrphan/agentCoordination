# Multi-Agent System Monitoring & Maintenance Guide

This guide covers comprehensive monitoring strategies, maintenance procedures, and operational best practices for the Multi-Agent Coordination System.

## Table of Contents

1. [Real-Time Monitoring](#real-time-monitoring)
2. [Health Check Procedures](#health-check-procedures)
3. [Log Management](#log-management)
4. [Performance Monitoring](#performance-monitoring)
5. [Maintenance Schedules](#maintenance-schedules)
6. [Alert Systems](#alert-systems)
7. [Capacity Planning](#capacity-planning)

## Real-Time Monitoring

### Primary Monitoring Dashboard

```bash
# Start the main monitoring dashboard
./coordination_manager.sh watch
```

**Dashboard Components:**
- **Agent Status Panel**: Real-time agent health and activity
- **Task Progress Tracker**: Current task assignments and completion rates
- **Authority Matrix**: Dynamic authority assignments and conflicts
- **Communication Flow**: Inter-agent message routing and latency
- **System Metrics**: CPU, memory, disk usage
- **Recent Activity**: Last 50 system events

**Dashboard Commands:**
- `r` - Refresh display
- `f` - Toggle full-screen mode
- `l` - Switch to log view
- `s` - Save current state
- `q` - Quit dashboard

### Project-Specific Monitoring

```bash
# Monitor a specific project
./project_manager.sh monitor "Project Name"

# Multi-project overview
./project_manager.sh monitor --all

# Focus on specific metrics
./project_manager.sh monitor "Project Name" --focus tasks,communication
```

### Command-Line Monitoring Tools

```bash
# Quick status check
./manage_agents.sh status

# Detailed system status
./coordination_manager.sh show-all

# Agent-specific status
./manage_agents.sh status alpha

# Communication health
find agent_communication/ -name "*.json" -mtime -0.1 | wc -l

# Resource usage
ps aux | grep -E "(python.*coordination|lifecycle)" | grep -v grep
```

### Continuous Monitoring Scripts

#### System Health Monitor

```bash
#!/bin/bash
# continuous_monitor.sh - Run every 30 seconds

LOG_FILE="monitoring.log"
ALERT_THRESHOLD=80

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check daemon status
    if ! ./lifecycle_daemon.sh status | grep -q "is running"; then
        echo "[$TIMESTAMP] CRITICAL: Lifecycle daemon not running" | tee -a "$LOG_FILE"
        # Auto-restart daemon
        ./lifecycle_daemon.sh start
    fi
    
    # Check agent health
    ACTIVE_AGENTS=$(./manage_agents.sh status | grep -c "Active")
    if [[ $ACTIVE_AGENTS -eq 0 ]]; then
        echo "[$TIMESTAMP] WARNING: No active agents" | tee -a "$LOG_FILE"
    fi
    
    # Check resource usage
    CPU_USAGE=$(ps aux | grep "python.*coordination" | awk '{sum += $3} END {print int(sum)}')
    if [[ ${CPU_USAGE:-0} -gt $ALERT_THRESHOLD ]]; then
        echo "[$TIMESTAMP] WARNING: High CPU usage: ${CPU_USAGE}%" | tee -a "$LOG_FILE"
    fi
    
    # Check communication latency
    LATEST_COMM=$(find agent_communication/ -name "*.json" -mtime -0.01 | wc -l)
    if [[ $LATEST_COMM -eq 0 ]]; then
        echo "[$TIMESTAMP] WARNING: No recent communication activity" | tee -a "$LOG_FILE"
    fi
    
    sleep 30
done
```

#### Agent Heartbeat Monitor

```bash
#!/bin/bash
# heartbeat_monitor.sh

check_agent_heartbeat() {
    local agent=$1
    local heartbeat_file="agent_communication/$agent/status/heartbeat.json"
    
    if [[ -f "$heartbeat_file" ]]; then
        local last_beat=$(stat -f%m "$heartbeat_file" 2>/dev/null || stat -c%Y "$heartbeat_file")
        local current_time=$(date +%s)
        local age=$((current_time - last_beat))
        
        if [[ $age -gt 120 ]]; then  # 2 minutes
            echo "WARNING: $agent heartbeat is $age seconds old"
            return 1
        else
            echo "OK: $agent heartbeat is current ($age seconds)"
            return 0
        fi
    else
        echo "ERROR: $agent heartbeat file missing"
        return 1
    fi
}

# Check all agents
AGENTS=($(./agent_theme_manager.py get-agents))
for agent in "${AGENTS[@]}"; do
    check_agent_heartbeat "$agent"
done
```

## Health Check Procedures

### Daily Health Checks

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Multi-Agent System Health Check $(date) ==="

# 1. System Process Health
echo "1. Process Health:"
DAEMON_PID=$(pgrep -f lifecycle_daemon.sh)
if [[ -n "$DAEMON_PID" ]]; then
    echo "   ✅ Lifecycle daemon running (PID: $DAEMON_PID)"
else
    echo "   ❌ Lifecycle daemon not running"
fi

COORD_PROCESSES=$(pgrep -cf "python.*coordination")
echo "   ✅ $COORD_PROCESSES coordination processes active"

# 2. Agent Status
echo -e "\n2. Agent Status:"
ACTIVE_AGENTS=$(./manage_agents.sh status | grep -c "Active")
TOTAL_AGENTS=$(./manage_agents.sh list | wc -l)
echo "   ✅ $ACTIVE_AGENTS/$TOTAL_AGENTS agents active"

# Show inactive agents
INACTIVE_AGENTS=$(./manage_agents.sh status | grep "Inactive" | cut -d: -f1)
if [[ -n "$INACTIVE_AGENTS" ]]; then
    echo "   ⚠️  Inactive agents: $INACTIVE_AGENTS"
fi

# 3. Resource Usage
echo -e "\n3. Resource Usage:"
TOTAL_CPU=$(ps aux | grep "coordination\|lifecycle" | awk '{sum += $3} END {print int(sum)}')
TOTAL_MEMORY=$(ps aux | grep "coordination\|lifecycle" | awk '{sum += $4} END {print int(sum)}')
echo "   📊 CPU Usage: ${TOTAL_CPU:-0}%"
echo "   📊 Memory Usage: ${TOTAL_MEMORY:-0}%"

# 4. Disk Space
echo -e "\n4. Disk Space:"
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
echo "   📊 Disk Usage: $DISK_USAGE%"
if [[ $DISK_USAGE -gt 80 ]]; then
    echo "   ⚠️  High disk usage - consider cleanup"
fi

# 5. Log File Health
echo -e "\n5. Log File Health:"
LOG_SIZE=$(du -sh logs/ 2>/dev/null | cut -f1)
echo "   📊 Total log size: ${LOG_SIZE:-0B}"

# Check for recent errors
ERROR_COUNT=$(find logs/ -name "*.log" -mtime -1 -exec grep -c "ERROR\|CRITICAL" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
echo "   📊 Errors in last 24h: $ERROR_COUNT"

# 6. Communication Health
echo -e "\n6. Communication Health:"
RECENT_COMM=$(find agent_communication/ -name "*.json" -mtime -1 | wc -l)
echo "   📊 Communication files (24h): $RECENT_COMM"

STALE_COMM=$(find agent_communication/ -name "*.json" -mtime +7 | wc -l)
if [[ $STALE_COMM -gt 0 ]]; then
    echo "   ⚠️  $STALE_COMM stale communication files (>7 days)"
fi

# 7. System Performance
echo -e "\n7. Performance Metrics:"
if [[ -f "metrics/daily_metrics.json" ]]; then
    TASK_COMPLETION_RATE=$(grep "completion_rate" metrics/daily_metrics.json | tail -1 | cut -d: -f2 | tr -d ',')
    echo "   📊 Task completion rate: ${TASK_COMPLETION_RATE:-N/A}"
    
    AVG_RESPONSE_TIME=$(grep "avg_response_time" metrics/daily_metrics.json | tail -1 | cut -d: -f2 | tr -d ',')
    echo "   📊 Average response time: ${AVG_RESPONSE_TIME:-N/A}ms"
fi

# 8. Security Check
echo -e "\n8. Security Status:"
FAILED_AUTHS=$(grep -c "authentication failed\|unauthorized" logs/*.log 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
echo "   🔒 Failed authentications (24h): $FAILED_AUTHS"

# 9. Backup Status
echo -e "\n9. Backup Status:"
LATEST_BACKUP=$(ls -t backups/*.tar.gz 2>/dev/null | head -1)
if [[ -n "$LATEST_BACKUP" ]]; then
    BACKUP_AGE=$(stat -f%Sm -t%Y-%m-%d "$LATEST_BACKUP" 2>/dev/null || stat -c%y "$LATEST_BACKUP" | cut -d' ' -f1)
    echo "   💾 Latest backup: $BACKUP_AGE"
else
    echo "   ⚠️  No backups found"
fi

echo -e "\n=== Health Check Complete ==="

# Generate health score
HEALTH_SCORE=100
[[ $ACTIVE_AGENTS -eq 0 ]] && HEALTH_SCORE=$((HEALTH_SCORE - 30))
[[ $ERROR_COUNT -gt 10 ]] && HEALTH_SCORE=$((HEALTH_SCORE - 20))
[[ $DISK_USAGE -gt 90 ]] && HEALTH_SCORE=$((HEALTH_SCORE - 20))
[[ $TOTAL_CPU -gt 90 ]] && HEALTH_SCORE=$((HEALTH_SCORE - 15))
[[ $FAILED_AUTHS -gt 5 ]] && HEALTH_SCORE=$((HEALTH_SCORE - 15))

echo "📊 Overall Health Score: $HEALTH_SCORE/100"

if [[ $HEALTH_SCORE -lt 70 ]]; then
    echo "⚠️  System health is below optimal - review issues above"
fi
```

### Weekly Health Checks

```bash
#!/bin/bash
# weekly_health_check.sh

echo "=== Weekly Multi-Agent System Deep Health Check $(date) ==="

# 1. Performance Trend Analysis
echo "1. Performance Trends (7 days):"
./coordination_system/analyze_performance_trends.py --days 7

# 2. Resource Usage Patterns
echo -e "\n2. Resource Usage Patterns:"
./coordination_system/analyze_resource_patterns.py --output weekly_resource_report.json

# 3. Agent Reliability Analysis
echo -e "\n3. Agent Reliability Analysis:"
for agent in $(./agent_theme_manager.py get-agents); do
    UPTIME=$(./coordination_system/calculate_agent_uptime.py "$agent" --days 7)
    echo "   $agent: ${UPTIME}% uptime"
done

# 4. Communication Analysis
echo -e "\n4. Communication Analysis:"
./coordination_system/analyze_communication_patterns.py --output weekly_comm_report.json

# 5. Error Pattern Analysis
echo -e "\n5. Error Pattern Analysis:"
./coordination_system/analyze_error_patterns.py --days 7

# 6. Capacity Analysis
echo -e "\n6. Capacity Analysis:"
./coordination_system/analyze_capacity_trends.py --forecast 30

echo -e "\n=== Weekly Health Check Complete ==="
```

## Log Management

### Log Rotation Strategy

```bash
#!/bin/bash
# log_rotation.sh - Run daily

LOG_DIR="logs"
MAX_SIZE="10M"
MAX_AGE=30  # days
ARCHIVE_DIR="logs/archive"

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Rotate large files
find "$LOG_DIR" -name "*.log" -size +"$MAX_SIZE" | while read -r log_file; do
    if [[ "$log_file" != *"/archive/"* ]]; then
        echo "Rotating large log file: $log_file"
        mv "$log_file" "${log_file}.$(date +%Y%m%d_%H%M%S)"
        touch "$log_file"  # Create new empty log file
    fi
done

# Archive old files
find "$LOG_DIR" -name "*.log.*" -mtime +7 -exec mv {} "$ARCHIVE_DIR"/ \;

# Compress archived files
find "$ARCHIVE_DIR" -name "*.log.*" -not -name "*.gz" -exec gzip {} \;

# Remove very old archives
find "$ARCHIVE_DIR" -name "*.gz" -mtime +$MAX_AGE -delete

echo "Log rotation completed: $(date)"
```

### Log Analysis Scripts

```bash
#!/bin/bash
# analyze_logs.sh

# Error Analysis
echo "=== Error Analysis ==="
echo "Top 10 error types (last 24h):"
find logs/ -name "*.log" -mtime -1 -exec grep "ERROR\|CRITICAL" {} \; | \
    cut -d: -f3- | sort | uniq -c | sort -nr | head -10

# Performance Analysis
echo -e "\n=== Performance Analysis ==="
echo "Agent response times (last hour):"
grep "response_time" logs/*.log | tail -20 | \
    awk '{print $NF}' | sort -n | \
    awk '{sum+=$1; times[NR]=$1} END {
        print "Average:", sum/NR "ms"
        print "Median:", times[int(NR/2)] "ms"
    }'

# Communication Analysis
echo -e "\n=== Communication Analysis ==="
echo "Message volumes by agent (last 6 hours):"
find agent_communication/ -name "*.json" -mtime -0.25 | \
    cut -d/ -f2 | sort | uniq -c | sort -nr

# System Events
echo -e "\n=== System Events ==="
echo "Recent system events:"
grep -h "SYSTEM\|DAEMON\|STARTUP\|SHUTDOWN" logs/*.log | tail -10
```

### Log Monitoring Alerts

```bash
#!/bin/bash
# log_alerts.sh - Run every 5 minutes

ALERT_EMAIL="admin@company.com"
ALERT_WEBHOOK="https://hooks.slack.com/your-webhook"

# Check for critical errors
CRITICAL_ERRORS=$(find logs/ -name "*.log" -mtime -0.01 -exec grep -c "CRITICAL" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')

if [[ $CRITICAL_ERRORS -gt 0 ]]; then
    MESSAGE="ALERT: $CRITICAL_ERRORS critical errors detected in multi-agent system"
    echo "$MESSAGE" | mail -s "Multi-Agent System Alert" "$ALERT_EMAIL"
    
    # Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$MESSAGE\"}" \
        "$ALERT_WEBHOOK"
fi

# Check for system unresponsiveness
if ! timeout 10s ./manage_agents.sh list > /dev/null 2>&1; then
    MESSAGE="ALERT: Multi-agent system appears unresponsive"
    echo "$MESSAGE" | mail -s "Multi-Agent System Unresponsive" "$ALERT_EMAIL"
fi
```

## Performance Monitoring

### Real-Time Performance Metrics

```bash
#!/bin/bash
# performance_monitor.sh

# Function to get current metrics
get_metrics() {
    echo "=== Performance Metrics $(date) ==="
    
    # CPU Usage
    CPU_TOTAL=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $3} END {print sum}')
    echo "CPU Usage: ${CPU_TOTAL:-0}%"
    
    # Memory Usage
    MEM_TOTAL=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $4} END {print sum}')
    echo "Memory Usage: ${MEM_TOTAL:-0}%"
    
    # Active Connections
    CONNECTIONS=$(netstat -an | grep ESTABLISHED | wc -l)
    echo "Active Connections: $CONNECTIONS"
    
    # Agent Response Times
    if [[ -f "metrics/response_times.log" ]]; then
        AVG_RESPONSE=$(tail -100 metrics/response_times.log | awk '{sum += $1} END {print sum/NR}')
        echo "Average Response Time: ${AVG_RESPONSE:-0}ms"
    fi
    
    # Task Throughput
    TASKS_COMPLETED=$(find logs/ -name "*.log" -mtime -0.01 -exec grep -c "TASK_COMPLETED" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
    echo "Tasks Completed (last 15min): $TASKS_COMPLETED"
    
    # Error Rate
    ERROR_RATE=$(find logs/ -name "*.log" -mtime -0.01 -exec grep -c "ERROR" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
    echo "Error Rate (last 15min): $ERROR_RATE"
    
    echo "=========================="
}

# Run continuously
while true; do
    get_metrics
    sleep 300  # 5 minutes
done
```

### Performance Benchmarking

```bash
#!/bin/bash
# benchmark_performance.sh

echo "=== Multi-Agent System Performance Benchmark ==="

# Benchmark 1: Agent Startup Time
echo "1. Agent Startup Time:"
START_TIME=$(date +%s.%N)
./manage_agents.sh start alpha
END_TIME=$(date +%s.%N)
STARTUP_TIME=$(echo "$END_TIME - $START_TIME" | bc)
echo "   Agent startup time: ${STARTUP_TIME}s"

# Benchmark 2: Communication Latency
echo "2. Communication Latency:"
./coordination_system/benchmark_communication.py --iterations 10

# Benchmark 3: Task Processing Speed
echo "3. Task Processing Speed:"
./coordination_system/benchmark_task_processing.py --tasks 100

# Benchmark 4: System Responsiveness
echo "4. System Responsiveness:"
for i in {1..10}; do
    START_TIME=$(date +%s.%N)
    ./manage_agents.sh status > /dev/null
    END_TIME=$(date +%s.%N)
    RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    echo "   Response time $i: ${RESPONSE_TIME}s"
done

# Benchmark 5: Concurrent Load
echo "5. Concurrent Load Test:"
./coordination_system/load_test.py --concurrent-requests 50 --duration 60

echo "=== Benchmark Complete ==="
```

## Maintenance Schedules

### Daily Maintenance (Automated)

```bash
#!/bin/bash
# daily_maintenance.sh - Run via cron at 2 AM

echo "Starting daily maintenance: $(date)"

# 1. Log rotation
./log_rotation.sh

# 2. Cleanup temporary files
find /tmp -name "coordination_*" -mtime +1 -delete
find agent_communication/ -name "*.tmp" -delete

# 3. Update metrics
./coordination_system/collect_daily_metrics.py

# 4. Database maintenance (if applicable)
if [[ -f "coordination.db" ]]; then
    sqlite3 coordination.db "VACUUM; ANALYZE;"
fi

# 5. Check for system updates
./coordination_system/check_system_updates.py

# 6. Generate daily report
./generate_daily_report.sh

echo "Daily maintenance completed: $(date)"
```

### Weekly Maintenance (Semi-Automated)

```bash
#!/bin/bash
# weekly_maintenance.sh - Run via cron on Sunday 3 AM

echo "Starting weekly maintenance: $(date)"

# 1. Deep system cleanup
find logs/ -name "*.log.*" -mtime +7 -delete
find agent_communication/ -name "*.json" -mtime +7 -delete
find metrics/ -name "*_daily.json" -mtime +30 -delete

# 2. Performance optimization
./coordination_system/optimize_performance.py

# 3. Security audit
./coordination_system/security_audit.py

# 4. Capacity planning analysis
./coordination_system/analyze_capacity_needs.py

# 5. System backup
./backup_system.sh

# 6. Update documentation
./coordination_system/update_system_docs.py

# 7. Generate weekly report
./generate_weekly_report.sh

echo "Weekly maintenance completed: $(date)"
```

### Monthly Maintenance (Manual)

```bash
#!/bin/bash
# monthly_maintenance.sh - Run manually on first Saturday of month

echo "Starting monthly maintenance: $(date)"

# 1. Full system health audit
./comprehensive_health_audit.sh

# 2. Performance trend analysis
./coordination_system/analyze_monthly_trends.py

# 3. Configuration review
./coordination_system/review_configurations.py

# 4. Update system dependencies
pip install -r requirements.txt --upgrade

# 5. Archive old data
./archive_old_data.sh

# 6. Plan capacity upgrades
./coordination_system/plan_capacity_upgrades.py

# 7. Generate monthly report
./generate_monthly_report.sh

echo "Monthly maintenance completed: $(date)"
echo "Please review monthly report and plan any necessary system upgrades."
```

## Alert Systems

### Alert Configuration

```bash
# Configure alert thresholds
cat > alert_config.json << EOF
{
    "thresholds": {
        "cpu_usage": 80,
        "memory_usage": 85,
        "disk_usage": 90,
        "error_rate": 10,
        "response_time": 5000,
        "agent_downtime": 300
    },
    "notifications": {
        "email": "admin@company.com",
        "slack_webhook": "https://hooks.slack.com/your-webhook",
        "pagerduty_key": "your-pagerduty-key"
    },
    "escalation": {
        "level1_delay": 300,
        "level2_delay": 900,
        "level3_delay": 1800
    }
}
EOF
```

### Alert Scripts

```bash
#!/bin/bash
# alert_system.sh

source alert_config.json

send_alert() {
    local severity=$1
    local message=$2
    local component=$3
    
    # Email notification
    echo "$message" | mail -s "[$severity] Multi-Agent System Alert: $component" "$EMAIL"
    
    # Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"[$severity] $message\"}" \
        "$SLACK_WEBHOOK"
    
    # Log alert
    echo "[$(date)] [$severity] $message" >> alerts.log
}

# Check thresholds and send alerts
check_cpu_usage() {
    local cpu_usage=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $3} END {print int(sum)}')
    if [[ ${cpu_usage:-0} -gt 80 ]]; then
        send_alert "WARNING" "High CPU usage: ${cpu_usage}%" "Performance"
    fi
}

check_memory_usage() {
    local mem_usage=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $4} END {print int(sum)}')
    if [[ ${mem_usage:-0} -gt 85 ]]; then
        send_alert "WARNING" "High memory usage: ${mem_usage}%" "Performance"
    fi
}

check_agent_health() {
    local inactive_agents=$(./manage_agents.sh status | grep -c "Inactive")
    if [[ $inactive_agents -gt 0 ]]; then
        send_alert "WARNING" "$inactive_agents agents are inactive" "Agents"
    fi
}

# Run all checks
check_cpu_usage
check_memory_usage  
check_agent_health
```

## Capacity Planning

### Capacity Monitoring

```bash
#!/bin/bash
# capacity_monitor.sh

# Collect capacity metrics
collect_capacity_metrics() {
    local timestamp=$(date +%s)
    
    # System resources
    local cpu_cores=$(nproc)
    local cpu_usage=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $3} END {print sum}')
    local mem_total=$(free -m | awk '/^Mem:/{print $2}')
    local mem_used=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $6} END {print sum/1024}')
    local disk_total=$(df -BG . | tail -1 | awk '{print $2}' | sed 's/G//')
    local disk_used=$(du -BG . | tail -1 | awk '{print $1}' | sed 's/G//')
    
    # Agent metrics
    local total_agents=$(./manage_agents.sh list | wc -l)
    local active_agents=$(./manage_agents.sh status | grep -c "Active")
    local tasks_per_hour=$(find logs/ -name "*.log" -mtime -0.04 -exec grep -c "TASK_COMPLETED" {} \; 2>/dev/null | awk '{sum += $1} END {print sum*24}')
    
    # Write to metrics file
    cat >> capacity_metrics.json << EOF
{
    "timestamp": $timestamp,
    "system": {
        "cpu_cores": $cpu_cores,
        "cpu_usage_percent": ${cpu_usage:-0},
        "memory_total_mb": $mem_total,
        "memory_used_mb": ${mem_used:-0},
        "disk_total_gb": $disk_total,
        "disk_used_gb": $disk_used
    },
    "agents": {
        "total_configured": $total_agents,
        "currently_active": $active_agents,
        "tasks_per_hour": ${tasks_per_hour:-0}
    }
}
EOF
}

# Analyze capacity trends
analyze_capacity_trends() {
    python3 << EOF
import json
import numpy as np
from datetime import datetime, timedelta

# Load recent metrics
with open('capacity_metrics.json', 'r') as f:
    metrics = [json.loads(line) for line in f.readlines()[-168:]]  # Last week

if len(metrics) < 24:
    print("Insufficient data for trend analysis")
    exit()

# Calculate trends
cpu_trend = np.polyfit(range(len(metrics)), [m['system']['cpu_usage_percent'] for m in metrics], 1)[0]
mem_trend = np.polyfit(range(len(metrics)), [m['system']['memory_used_mb'] for m in metrics], 1)[0]
task_trend = np.polyfit(range(len(metrics)), [m['agents']['tasks_per_hour'] for m in metrics], 1)[0]

print(f"Capacity Trend Analysis:")
print(f"CPU Usage Trend: {cpu_trend:+.2f}% per hour")
print(f"Memory Usage Trend: {mem_trend:+.2f} MB per hour")
print(f"Task Volume Trend: {task_trend:+.2f} tasks/hour per hour")

# Predict capacity needs
hours_to_forecast = 720  # 30 days
current_cpu = metrics[-1]['system']['cpu_usage_percent']
predicted_cpu = current_cpu + (cpu_trend * hours_to_forecast)

if predicted_cpu > 80:
    print(f"WARNING: CPU usage predicted to reach {predicted_cpu:.1f}% in 30 days")

current_mem = metrics[-1]['system']['memory_used_mb']
predicted_mem = current_mem + (mem_trend * hours_to_forecast)
total_mem = metrics[-1]['system']['memory_total_mb']

if predicted_mem > total_mem * 0.85:
    print(f"WARNING: Memory usage predicted to reach {predicted_mem:.1f}MB in 30 days")
EOF
}

# Generate capacity report
generate_capacity_report() {
    cat > capacity_report.md << EOF
# Multi-Agent System Capacity Report

Generated: $(date)

## Current Utilization

$(collect_capacity_metrics && tail -1 capacity_metrics.json | python3 -m json.tool)

## Trend Analysis

$(analyze_capacity_trends)

## Recommendations

Based on current trends:

1. **CPU**: $(if [[ $(analyze_capacity_trends | grep "CPU.*+" | wc -l) -gt 0 ]]; then echo "Consider CPU upgrade"; else echo "CPU capacity sufficient"; fi)
2. **Memory**: $(if [[ $(analyze_capacity_trends | grep "Memory.*+" | wc -l) -gt 0 ]]; then echo "Consider memory upgrade"; else echo "Memory capacity sufficient"; fi)
3. **Agents**: Current agent count appears $(if [[ $(./manage_agents.sh status | grep -c "Active") -eq $(./manage_agents.sh list | wc -l) ]]; then echo "optimal"; else echo "sub-optimal - consider adjusting"; fi)

EOF
}

# Run capacity monitoring
collect_capacity_metrics
analyze_capacity_trends
generate_capacity_report
```

## Summary

Effective monitoring and maintenance are crucial for reliable operation of the Multi-Agent Coordination System. Key practices include:

1. **Continuous Monitoring**: Use real-time dashboards and automated checks
2. **Proactive Maintenance**: Regular cleanup, optimization, and updates
3. **Alert Systems**: Immediate notification of critical issues
4. **Capacity Planning**: Trend analysis and resource forecasting
5. **Documentation**: Keep detailed logs and reports for analysis

Regular execution of these procedures ensures optimal system performance and prevents issues before they impact operations.

For more specific troubleshooting guidance, refer to the [System Operations Guide](SYSTEM_OPERATIONS_GUIDE.md) and [Startup Procedures](STARTUP_PROCEDURES.md).