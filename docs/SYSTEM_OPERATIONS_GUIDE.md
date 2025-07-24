# Multi-Agent Coordination System - Operations Guide

This comprehensive guide covers everything you need to know about starting up, running, monitoring, and maintaining the Multi-Agent Coordination System.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture Overview](#system-architecture-overview)
3. [Startup Procedures](#startup-procedures)
4. [Monitoring and Maintenance](#monitoring-and-maintenance)
5. [Shutdown Procedures](#shutdown-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tuning](#performance-tuning)
8. [Security Considerations](#security-considerations)

## Quick Start

### Prerequisites

```bash
# Ensure you have the required dependencies
pip install -r requirements.txt

# Verify system structure
ls -la | grep -E "(manage_agents.sh|coordination_manager.sh|lifecycle_daemon.sh|project_manager.sh)"

# Check Python scripts
ls coordination_system/ | grep -E "(project_manager.py|status_aggregator.py)"
```

### 5-Minute Setup

```bash
# 1. Initialize the coordination system
./coordination_manager.sh init

# 2. Start the system with automatic lifecycle management
./manage_agents.sh auto

# 3. Create your first project
./project_manager.sh create "My First Project" /path/to/your/code

# 4. Monitor the system
./coordination_manager.sh watch
```

## System Architecture Overview

### Core Components

```
Multi-Agent Coordination System
├── Project Management Layer
│   ├── project_manager.sh          # CLI interface
│   ├── coordination_system/
│   │   ├── project_manager.py      # Core project logic
│   │   └── project_lifecycle_manager.py
│   └── projects/                   # Project workspaces
│
├── Agent Management Layer
│   ├── manage_agents.sh            # Agent lifecycle control
│   ├── lifecycle_daemon.sh         # Automatic agent management
│   ├── agent_theme_manager.py      # Theme configuration
│   └── agent_status/               # Agent status tracking
│
├── Coordination Layer
│   ├── coordination_manager.sh     # System coordination
│   ├── coordination_system/
│   │   ├── status_aggregator.py    # Status aggregation
│   │   ├── task_assignment_manager.py
│   │   └── dynamic_authority_manager.py
│   └── agent_communication/        # Inter-agent messaging
│
└── Monitoring & Operations
    ├── logs/                       # System logs
    ├── metrics/                    # Performance metrics
    └── worktree_manager.sh         # Git worktree management
```

### Process Flow

1. **Initialization**: System checks requirements and sets up directories
2. **Project Creation**: Projects are created with isolated workspaces
3. **Agent Startup**: Agents are started based on project needs and dependencies
4. **Task Assignment**: Tasks are distributed among available agents
5. **Coordination**: Agents communicate and coordinate through status updates
6. **Monitoring**: System tracks performance, health, and progress
7. **Shutdown**: Graceful shutdown with cleanup

## Startup Procedures

### Method 1: Automatic Startup (Recommended)

```bash
# Complete automatic startup sequence
./manage_agents.sh auto
```

**What this does:**
- Checks if lifecycle daemon is already running
- Starts lifecycle daemon for automatic agent management
- Agents start automatically based on dependencies and blockers
- Monitors agent health through heartbeats
- Routes messages between agents

**Expected Output:**
```
Starting Lifecycle Daemon for automatic agent management...

The daemon will:
  ✓ Start agents when dependencies are met and no blockers exist
  ✓ Stop agents when they become blocked
  ✓ Route messages between agents
  ✓ Monitor agent health through heartbeats

✅ Lifecycle management activated!

Agents will be automatically started as their dependencies are met.
First agent(s) with no dependencies will start in ~10 seconds.

Monitor with:
  ./lifecycle_daemon.sh status   - Check daemon and agent status
  ./lifecycle_daemon.sh logs     - View detailed logs
  tail -f lifecycle_daemon.log   - Follow live activity
```

### Method 2: Manual Startup

```bash
# 1. Initialize coordination system
./coordination_manager.sh init

# 2. Configure theme and agent count
./manage_agents.sh set-theme marvel
./manage_agents.sh set-count 6

# 3. Generate agent files
./generate_agents.sh

# 4. Start individual agents
./manage_agents.sh start ironman
./manage_agents.sh start captainamerica
# ... continue for other agents

# 5. Start monitoring
./coordination_manager.sh watch &
```

### Method 3: Project-Specific Startup

```bash
# Create a new project and start agents for it
./project_manager.sh create "Web Application" ~/projects/webapp -a 8
./project_manager.sh start "Web Application"

# Or switch to existing project
./project_manager.sh switch "Existing Project"
./manage_agents.sh auto
```

### Startup Verification

After startup, verify the system is running correctly:

```bash
# Check daemon status
./lifecycle_daemon.sh status

# Check agent status
./manage_agents.sh status

# Check coordination system
./coordination_manager.sh show-all

# View recent logs
tail -f lifecycle_daemon.log
```

**Healthy System Indicators:**
- ✅ Lifecycle daemon is running (PID shown)
- ✅ At least one agent is active
- ✅ No error messages in logs
- ✅ Agent status files are being updated (recent timestamps)

## Monitoring and Maintenance

### Real-Time Monitoring Dashboard

```bash
# Start the main monitoring dashboard
./coordination_manager.sh watch

# Alternative: Project-specific monitoring
./project_manager.sh monitor "Project Name"
```

**Dashboard Features:**
- Real-time agent status updates
- Task progress tracking
- Authority assignments
- System health metrics
- Recent activity log

### Log Monitoring

```bash
# Follow live system activity
tail -f lifecycle_daemon.log

# View coordination logs
tail -f coordination_manager.log

# Check agent-specific logs
tail -f logs/agent_*.log

# View all recent logs
find logs/ -name "*.log" -mtime -1 -exec tail -5 {} +
```

### Health Checks

#### Daily Health Check Script

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Multi-Agent System Health Check $(date) ==="

# Check daemon status
echo "1. Lifecycle Daemon Status:"
./lifecycle_daemon.sh status

# Check disk space
echo -e "\n2. Disk Space:"
df -h . | tail -1

# Check log file sizes
echo -e "\n3. Log File Sizes:"
du -sh logs/*.log 2>/dev/null | head -10

# Check agent responsiveness
echo -e "\n4. Agent Responsiveness:"
./manage_agents.sh status | grep -E "(Active|Inactive|Blocked)"

# Check recent errors
echo -e "\n5. Recent Errors (last 24h):"
find logs/ -name "*.log" -mtime -1 -exec grep -l "ERROR\|CRITICAL" {} \;

# Check resource usage
echo -e "\n6. Resource Usage:"
ps aux | grep -E "(python.*coordination|lifecycle_daemon)" | grep -v grep

echo -e "\n=== Health Check Complete ==="
```

#### Weekly Maintenance Tasks

```bash
# Clean up old logs (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Rotate large log files
for log in lifecycle_daemon.log coordination_manager.log; do
    if [[ -f "$log" && $(stat -f%z "$log" 2>/dev/null || stat -c%s "$log") -gt 10485760 ]]; then
        mv "$log" "${log}.$(date +%Y%m%d)"
        touch "$log"
    fi
done

# Clean up stale agent communication files
find agent_communication/ -name "*.json" -mtime +7 -delete

# Verify git worktrees are healthy
./worktree_manager.sh health-check

# Update system status
./coordination_manager.sh show-all > system_status_$(date +%Y%m%d).txt
```

### Performance Monitoring

```bash
# Check system performance
./metrics_collector.py --report

# Monitor resource usage over time
watch -n 5 'ps aux | grep -E "(python.*coordination|lifecycle)" | grep -v grep'

# Check agent communication latency
./coordination_system/analyze_communication_patterns.py

# Generate performance report
./performance_profiler.py --generate-report
```

## Shutdown Procedures

### Graceful Shutdown (Recommended)

```bash
# Stop lifecycle daemon (stops all agents)
./lifecycle_daemon.sh stop

# Wait for agents to finish current tasks
sleep 10

# Stop coordination manager if running
pkill -f coordination_manager.sh

# Stop any remaining processes
./manage_agents.sh stop-all

# Verify shutdown
./lifecycle_daemon.sh status
```

### Emergency Shutdown

```bash
# Force stop everything immediately
pkill -f "python.*coordination"
pkill -f lifecycle_daemon.sh
pkill -f manage_agents.sh

# Clean up PID files
rm -f lifecycle_daemon.pid

# Verify no processes remain
ps aux | grep -E "(coordination|lifecycle|manage_agent)" | grep -v grep
```

### Maintenance Shutdown

```bash
# 1. Prevent new tasks from starting
./coordination_manager.sh pause-new-tasks

# 2. Wait for current tasks to complete
./manage_agents.sh wait-for-completion --timeout 300

# 3. Graceful shutdown
./lifecycle_daemon.sh stop

# 4. Backup current state
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz agent_status/ logs/ projects/

# 5. Perform maintenance
# ... your maintenance tasks ...

# 6. Restart system
./manage_agents.sh auto
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Lifecycle Daemon Won't Start

**Symptoms:**
```
❌ Failed to start lifecycle daemon
```

**Diagnosis:**
```bash
# Check for existing daemon
ps aux | grep lifecycle_daemon

# Check for PID file conflicts
ls -la lifecycle_daemon.pid

# Check permissions
ls -la lifecycle_daemon.sh
```

**Solutions:**
```bash
# Kill existing daemon and restart
pkill -f lifecycle_daemon.sh
rm -f lifecycle_daemon.pid
./lifecycle_daemon.sh start

# Fix permissions
chmod +x lifecycle_daemon.sh

# Check dependencies
python3 -c "import json, os, time, subprocess"
```

#### 2. Agents Not Starting

**Symptoms:**
```
No agents are currently active
```

**Diagnosis:**
```bash
# Check agent status files
ls -la agent_status/
cat agent_status/*.json

# Check for blockers
grep -r "blocked" agent_status/

# Check dependency resolution
./coordination_system/analyze_dependencies.py
```

**Solutions:**
```bash
# Clear stale status files
rm agent_status/*.json
./manage_agents.sh auto

# Reset agent communication
rm -rf agent_communication/*/
./coordination_manager.sh init

# Manual agent start
./manage_agents.sh start alpha
```

#### 3. High Resource Usage

**Symptoms:**
```
System is slow, high CPU/memory usage
```

**Diagnosis:**
```bash
# Check resource usage
top -p $(pgrep -f "python.*coordination")

# Check log file sizes
du -sh logs/*.log

# Check number of active processes
ps aux | grep coordination | wc -l
```

**Solutions:**
```bash
# Reduce agent count
./manage_agents.sh set-count 4

# Clean up logs
find logs/ -name "*.log" -mtime +7 -delete

# Restart with lower resource limits
ulimit -v 1048576  # Limit virtual memory
./manage_agents.sh auto
```

#### 4. Communication Issues

**Symptoms:**
```
Agents not communicating, stale status updates
```

**Diagnosis:**
```bash
# Check communication directories
find agent_communication/ -name "*.json" -mtime -1

# Check status update timestamps
stat agent_status/*.json | grep Modify

# Check for permission issues
ls -la agent_communication/
```

**Solutions:**
```bash
# Reset communication channels
./coordination_manager.sh reset-communication

# Fix permissions
chmod -R 755 agent_communication/

# Restart specific agents
./manage_agents.sh restart alpha beta
```

### Debug Mode Operations

```bash
# Enable debug logging
export DEBUG=1
./manage_agents.sh auto

# Run with verbose output
./lifecycle_daemon.sh start --verbose

# Enable trace mode for specific agent
TRACE_AGENT=alpha ./manage_agents.sh start alpha

# Generate debug report
./coordination_system/generate_debug_report.py
```

## Performance Tuning

### System Optimization

```bash
# Optimize agent count based on workload
./manage_agents.sh set-count $(nproc)

# Use faster theme (fewer string operations)
./manage_agents.sh set-theme greek_letters

# Enable performance mode
export PERFORMANCE_MODE=1
./manage_agents.sh auto

# Optimize log levels
export LOG_LEVEL=WARNING
```

### Resource Management

```bash
# Set resource limits
ulimit -n 1024      # File descriptors
ulimit -u 256       # Processes
ulimit -v 2097152   # Virtual memory (2GB)

# Use memory-mapped files for large datasets
export USE_MMAP=1

# Enable compression for logs
export COMPRESS_LOGS=1
```

### Scaling Considerations

#### Vertical Scaling (Single Machine)
```bash
# Increase agent count gradually
for count in 6 8 12 16; do
    ./manage_agents.sh set-count $count
    sleep 60  # Monitor performance
    echo "Testing with $count agents..."
done
```

#### Horizontal Scaling (Multiple Machines)
```bash
# Distribute agents across machines
# Machine 1: Agents 1-8
./manage_agents.sh set-theme marvel
./manage_agents.sh set-count 8

# Machine 2: Agents 9-16
./manage_agents.sh set-theme greek_mythology
./manage_agents.sh set-count 8

# Coordinate through shared filesystem or message queue
```

## Security Considerations

### Access Control

```bash
# Set proper file permissions
chmod 750 *.sh
chmod 640 *.json
chmod 755 coordination_system/

# Restrict log access
chmod 640 logs/*.log

# Secure communication directories
find agent_communication/ -type d -exec chmod 750 {} \;
find agent_communication/ -type f -exec chmod 640 {} \;
```

### Monitoring Security

```bash
# Check for unauthorized access
grep -r "UNAUTHORIZED\|DENIED" logs/

# Monitor file changes
find . -name "*.py" -newer last_security_check -ls

# Verify script integrity
shasum -c system_checksums.txt
```

### Secure Operations

```bash
# Run with restricted permissions
sudo -u coordination_user ./manage_agents.sh auto

# Use secure temporary directories
export TMPDIR=/secure/tmp

# Enable audit logging
export AUDIT_LOG=1
```

## Advanced Operations

### Backup and Recovery

```bash
# Create system backup
tar -czf system_backup_$(date +%Y%m%d).tar.gz \
    agent_status/ \
    agent_communication/ \
    coordination_system/ \
    projects/ \
    logs/ \
    *.json

# Recovery procedure
tar -xzf system_backup_YYYYMMDD.tar.gz
./coordination_manager.sh init
./manage_agents.sh auto
```

### Custom Configurations

```bash
# Create custom agent themes
./agent_theme_manager.py create-theme custom_theme \
    --agents "alice,bob,charlie,david" \
    --roles "lead,backend,frontend,devops"

# Configure specialized agent roles
./coordination_system/configure_agent_specialization.py \
    --agent alpha --specialization "database,backend" \
    --agent beta --specialization "frontend,ui"
```

### Integration with External Systems

```bash
# CI/CD Integration
./manage_agents.sh auto --mode ci
export CI_MODE=1

# Webhook notifications
export WEBHOOK_URL="https://your-system.com/hooks/coordination"
./coordination_manager.sh watch --webhook

# External monitoring integration
export PROMETHEUS_ENDPOINT="http://prometheus:9090"
./metrics_collector.py --export prometheus
```

## Summary

This operations guide provides comprehensive coverage of running the Multi-Agent Coordination System. The key points are:

1. **Start Simple**: Use `./manage_agents.sh auto` for most cases
2. **Monitor Actively**: Use the dashboard and log monitoring
3. **Maintain Regularly**: Clean logs, check health, backup state
4. **Troubleshoot Systematically**: Check daemon → agents → communication → resources
5. **Scale Thoughtfully**: Increase agents gradually while monitoring performance

For additional help:
- Check `./manage_agents.sh help` for agent management
- Check `./coordination_manager.sh help` for system coordination
- Check `./project_manager.sh help` for project operations
- Review logs in the `logs/` directory for detailed information

The system is designed to be self-managing once started, but understanding these operational procedures will help you run it effectively in production environments.