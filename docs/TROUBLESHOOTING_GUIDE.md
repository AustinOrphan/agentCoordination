# Multi-Agent System Troubleshooting Guide

This guide provides systematic troubleshooting procedures for common operational issues in the Multi-Agent Coordination System.

## Table of Contents

1. [Diagnostic Framework](#diagnostic-framework)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [System Recovery Procedures](#system-recovery-procedures)
4. [Performance Issues](#performance-issues)
5. [Communication Problems](#communication-problems)
6. [Emergency Procedures](#emergency-procedures)
7. [Debug Tools](#debug-tools)

## Diagnostic Framework

### Initial Assessment Protocol

```bash
#!/bin/bash
# quick_diagnosis.sh - Run this first for any issue

echo "🔍 Multi-Agent System Quick Diagnosis"
echo "===================================="

# 1. System Health Check
echo "1. System Health:"
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    echo "   ✅ Lifecycle daemon: Running"
else
    echo "   ❌ Lifecycle daemon: Not running"
fi

ACTIVE_AGENTS=$(./manage_agents.sh status 2>/dev/null | grep -c "Active" || echo "0")
TOTAL_AGENTS=$(./manage_agents.sh list 2>/dev/null | wc -l || echo "0")
echo "   📊 Active agents: $ACTIVE_AGENTS/$TOTAL_AGENTS"

# 2. Resource Check
CPU_USAGE=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $3} END {print int(sum)}' || echo "0")
MEM_USAGE=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $4} END {print int(sum)}' || echo "0")
echo "   📊 CPU usage: ${CPU_USAGE}%"
echo "   📊 Memory usage: ${MEM_USAGE}%"

# 3. Recent Errors
ERROR_COUNT=$(find logs/ -name "*.log" -mtime -0.1 -exec grep -c "ERROR\|CRITICAL" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
echo "   📊 Recent errors (last 2.4h): $ERROR_COUNT"

# 4. Communication Health
COMM_FILES=$(find agent_communication/ -name "*.json" -mtime -0.1 2>/dev/null | wc -l)
echo "   📊 Recent communication: $COMM_FILES files"

# 5. Disk Space
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' || echo "N/A")
echo "   📊 Disk usage: $DISK_USAGE"

echo ""
echo "Quick diagnosis completed. See specific sections below for detailed troubleshooting."
```

### Systematic Troubleshooting Steps

1. **Identify Symptoms** - What exactly is not working?
2. **Check System Health** - Run quick diagnosis
3. **Review Recent Logs** - Look for error patterns
4. **Isolate Components** - Test individual components
5. **Apply Solutions** - Implement fixes systematically
6. **Verify Resolution** - Confirm issue is resolved
7. **Document** - Record solution for future reference

## Common Issues and Solutions

### Issue 1: System Won't Start

#### Symptoms
- `./manage_agents.sh auto` fails
- "Failed to start lifecycle daemon" error
- No agents become active

#### Diagnosis
```bash
# Check for existing processes
ps aux | grep -E "(lifecycle|coordination)" | grep -v grep

# Check for port conflicts
netstat -tuln | grep :8080  # Adjust port as needed

# Check file permissions
ls -la *.sh | grep -v "rwx"

# Check disk space
df -h .

# Check dependencies
python3 -c "import json, os, subprocess, time"
```

#### Solutions

**Solution 1A: Clean Start**
```bash
# Kill any existing processes
pkill -f "lifecycle_daemon\|coordination_manager"
rm -f *.pid

# Reset system state
rm -rf agent_status/*.json
rm -rf agent_communication/*/input/*.json
rm -rf agent_communication/*/output/*.json

# Restart
./coordination_manager.sh init
./manage_agents.sh auto
```

**Solution 1B: Fix Permissions**
```bash
# Fix script permissions
chmod +x *.sh
chmod 755 coordination_system/

# Fix directory permissions
chmod 755 agent_status agent_communication logs
```

**Solution 1C: Port Conflict Resolution**
```bash
# Find and kill process using port
lsof -ti:8080 | xargs kill -9

# Or change port in configuration
export COORDINATION_PORT=8081
./manage_agents.sh auto
```

### Issue 2: Agents Not Starting

#### Symptoms
- Lifecycle daemon running but no active agents
- Agents show "Inactive" status
- "No agents started after timeout" message

#### Diagnosis
```bash
# Check agent configuration
cat agent_config.json

# Check for blockers
find agent_status/ -name "*.json" -exec grep -l "blocked" {} \;

# Check dependency resolution
./coordination_system/check_dependencies.py

# Check agent-specific logs
tail -20 logs/agent_*.log
```

#### Solutions

**Solution 2A: Reset Agent Status**
```bash
# Clear all agent status files
rm -f agent_status/*.json

# Regenerate agent configuration
./generate_agents.sh

# Restart lifecycle daemon
./lifecycle_daemon.sh restart
```

**Solution 2B: Manual Agent Start**
```bash
# Try starting individual agents
./manage_agents.sh start alpha
sleep 10

# Check if manual start works
./manage_agents.sh status alpha

# If successful, check what's blocking automatic start
grep -r "dependency\|blocked" agent_status/
```

**Solution 2C: Reduce Agent Count**
```bash
# Start with fewer agents
./manage_agents.sh set-count 2
./generate_agents.sh
./manage_agents.sh auto

# Gradually increase once stable
./manage_agents.sh set-count 4
```

### Issue 3: High Resource Usage

#### Symptoms
- System becomes slow or unresponsive
- High CPU or memory usage
- "Resource exhausted" errors

#### Diagnosis
```bash
# Check resource usage by process
ps aux | grep -E "(coordination|lifecycle)" | head -10

# Check for runaway processes
top -n 1 | grep -E "(coordination|python)"

# Check for memory leaks
free -h

# Check for excessive logging
du -sh logs/
find logs/ -name "*.log" -size +100M
```

#### Solutions

**Solution 3A: Reduce Load**
```bash
# Reduce number of agents
./manage_agents.sh set-count 3

# Enable performance mode
export PERFORMANCE_MODE=1
./lifecycle_daemon.sh restart

# Increase resource limits
ulimit -n 2048  # file descriptors
ulimit -u 512   # processes
```

**Solution 3B: Clean Up Resources**
```bash
# Clean up log files
find logs/ -name "*.log" -size +50M -exec truncate -s 25M {} \;

# Clean up temporary files
find /tmp -name "coordination_*" -delete
find . -name "*.tmp" -delete

# Clean up old communication files
find agent_communication/ -name "*.json" -mtime +1 -delete
```

**Solution 3C: Restart Services**
```bash
# Rolling restart to free resources
./rolling_restart.sh

# Full restart if necessary
./graceful_shutdown.sh
sleep 30
./manage_agents.sh auto
```

### Issue 4: Communication Problems

#### Symptoms
- Agents not communicating with each other
- Stale status updates
- "Communication timeout" errors

#### Diagnosis
```bash
# Check communication directories
find agent_communication/ -name "*.json" -mtime -0.1

# Check file permissions
ls -la agent_communication/*/

# Check for stale files
find agent_communication/ -name "*.json" -mtime +0.1 | wc -l

# Check network connectivity (if distributed)
ping other_host  # if applicable
```

#### Solutions

**Solution 4A: Reset Communication Channels**
```bash
# Clear all communication files
find agent_communication/ -name "*.json" -delete

# Recreate directory structure
./coordination_manager.sh init-communication

# Restart agents
./manage_agents.sh restart-all
```

**Solution 4B: Fix Permissions**
```bash
# Fix directory permissions
chmod -R 755 agent_communication/

# Ensure proper ownership
chown -R $(whoami):$(whoami) agent_communication/

# Restart coordination manager
./coordination_manager.sh restart
```

**Solution 4C: Increase Timeouts**
```bash
# Increase communication timeouts
export COMM_TIMEOUT=60
export HEARTBEAT_INTERVAL=30

# Restart with new settings
./lifecycle_daemon.sh restart
```

### Issue 5: Database/State Corruption

#### Symptoms
- "Invalid JSON" errors
- Corrupted status files
- Inconsistent system state

#### Diagnosis
```bash
# Check for corrupted JSON files
find . -name "*.json" -exec python3 -m json.tool {} \; 2>&1 | grep -B1 "Expecting"

# Check file integrity
find agent_status/ -name "*.json" -size 0

# Check for partial writes
lsof | grep -E "coordination.*json"
```

#### Solutions

**Solution 5A: Restore from Backup**
```bash
# Stop system
./emergency_shutdown.sh

# Restore from latest backup
LATEST_BACKUP=$(ls -t backup_*.tar.gz | head -1)
if [[ -n "$LATEST_BACKUP" ]]; then
    tar -xzf "$LATEST_BACKUP"
    cp -r backup_*/agent_status . 2>/dev/null
    cp -r backup_*/projects . 2>/dev/null
    rm -rf backup_*/
    echo "Restored from $LATEST_BACKUP"
fi

# Restart system
./manage_agents.sh auto
```

**Solution 5B: Regenerate State**
```bash
# Remove corrupted files
find . -name "*.json" -size 0 -delete
find . -name "*.json" -exec python3 -m json.tool {} \; 2>&1 | grep -B1 "Expecting" | grep "\.json" | xargs rm -f

# Regenerate system files
./generate_agents.sh
./coordination_manager.sh init

# Restart system
./manage_agents.sh auto
```

### Issue 6: Project-Specific Problems

#### Symptoms
- Specific project won't start
- Project tasks not completing
- Project agent conflicts

#### Diagnosis
```bash
# Check project status
./project_manager.sh info "Project Name"

# Check project agents
./project_manager.sh status "Project Name"

# Check project logs
tail -20 projects/proj_*/logs/*.log

# Check project configuration
cat projects/proj_*/config.json
```

#### Solutions

**Solution 6A: Reset Project**
```bash
# For test projects
./project_manager.sh reset "Project Name"

# For production projects (with caution)
./project_manager.sh reset "Project Name" --confirm
```

**Solution 6B: Project-Specific Restart**
```bash
# Stop project agents
./project_manager.sh stop "Project Name"

# Clean project state
./project_cleanup.sh "Project Name" standard

# Restart project
./project_manager.sh start "Project Name"
```

## System Recovery Procedures

### Recovery from System Crash

```bash
#!/bin/bash
# crash_recovery.sh

echo "🚨 Starting crash recovery procedure..."

# 1. Emergency assessment
echo "1. Assessing system state..."
DAEMON_RUNNING=$(pgrep -f lifecycle_daemon.sh | wc -l)
COORD_PROCESSES=$(pgrep -f coordination | wc -l)
echo "   Daemon processes: $DAEMON_RUNNING"
echo "   Coordination processes: $COORD_PROCESSES"

# 2. Clean up crashed processes
echo "2. Cleaning up crashed processes..."
pkill -f "lifecycle_daemon.*<defunct>"
pkill -f "python.*coordination.*<defunct>"
rm -f *.pid

# 3. Check for data corruption
echo "3. Checking for data corruption..."
CORRUPTED_FILES=0
for file in agent_config.json projects/*/config.json; do
    if [[ -f "$file" ]] && ! python3 -m json.tool "$file" > /dev/null 2>&1; then
        echo "   ⚠️  Corrupted: $file"
        CORRUPTED_FILES=$((CORRUPTED_FILES + 1))
    fi
done

if [[ $CORRUPTED_FILES -gt 0 ]]; then
    echo "   🔧 Attempting data recovery..."
    ./data_recovery.sh backup
fi

# 4. Gradual restart
echo "4. Starting gradual system recovery..."
./manage_agents.sh set-count 2
./coordination_manager.sh init
./lifecycle_daemon.sh start

# 5. Verify recovery
sleep 60
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    ACTIVE_AGENTS=$(./manage_agents.sh status | grep -c "Active")
    if [[ $ACTIVE_AGENTS -gt 0 ]]; then
        echo "   ✅ Recovery successful ($ACTIVE_AGENTS agents active)"
        # Gradually restore full capacity
        ./manage_agents.sh set-count 6
    else
        echo "   ⚠️  Partial recovery - agents not starting"
    fi
else
    echo "   ❌ Recovery failed - manual intervention required"
fi

echo "🚨 Crash recovery procedure completed"
```

### Recovery from Configuration Corruption

```bash
#!/bin/bash
# config_recovery.sh

echo "🔧 Starting configuration recovery..."

# Backup current state
cp agent_config.json agent_config.json.backup 2>/dev/null

# Create minimal working configuration
cat > agent_config.json << EOF
{
    "theme": "greek_letters",
    "agent_count": 3,
    "agents": ["alpha", "beta", "gamma"],
    "roles": {
        "alpha": "Critical Path Lead",
        "beta": "Migration Specialist", 
        "gamma": "Dashboard Developer"
    },
    "created": "$(date -Iseconds)",
    "recovery_mode": true
}
EOF

# Regenerate system files
./generate_agents.sh

# Test configuration
if ./manage_agents.sh list > /dev/null 2>&1; then
    echo "✅ Configuration recovery successful"
    echo "ℹ️  System running in recovery mode with 3 agents"
    echo "ℹ️  Reconfigure as needed: ./manage_agents.sh set-theme <theme>"
else
    echo "❌ Configuration recovery failed"
    exit 1
fi
```

## Performance Issues

### Slow System Response

```bash
#!/bin/bash
# diagnose_performance.sh

echo "📊 Performance Diagnosis"
echo "======================="

# 1. System load
echo "1. System Load:"
uptime
echo ""

# 2. Process analysis
echo "2. Top resource consumers:"
ps aux | grep -E "(coordination|lifecycle)" | head -5
echo ""

# 3. I/O analysis
echo "3. Disk I/O:"
iostat 1 3 2>/dev/null || echo "iostat not available"
echo ""

# 4. Memory analysis
echo "4. Memory usage:"
free -h
echo ""

# 5. Agent response times
echo "5. Agent response times:"
for agent in alpha beta gamma; do
    if ./manage_agents.sh status "$agent" | grep -q "Active"; then
        START_TIME=$(date +%s.%N)
        ./manage_agents.sh ping "$agent" > /dev/null 2>&1
        END_TIME=$(date +%s.%N)
        RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc 2>/dev/null || echo "N/A")
        echo "   $agent: ${RESPONSE_TIME}s"
    fi
done
```

### Memory Leak Detection

```bash
#!/bin/bash
# memory_leak_check.sh

echo "🔍 Memory Leak Detection"

# Monitor memory usage over time
for i in {1..10}; do
    MEM_USAGE=$(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $6} END {print sum/1024}')
    echo "$(date '+%H:%M:%S'): ${MEM_USAGE}MB"
    sleep 30
done | tee memory_usage.log

# Analyze trend
echo "Memory usage trend:"
python3 << EOF
import re
with open('memory_usage.log', 'r') as f:
    data = []
    for line in f:
        if 'MB' in line:
            mem = float(re.search(r'(\d+\.?\d*)MB', line).group(1))
            data.append(mem)
    
if len(data) > 5:
    trend = (data[-1] - data[0]) / len(data)
    print(f"Memory trend: {trend:+.2f}MB per measurement")
    if trend > 10:
        print("⚠️  Potential memory leak detected")
    else:
        print("✅ Memory usage appears stable")
EOF
```

## Communication Problems

### Message Queue Diagnosis

```bash
#!/bin/bash
# diagnose_communication.sh

echo "📡 Communication System Diagnosis"
echo "================================"

# 1. Message queue status
echo "1. Message queue status:"
for agent in $(./agent_theme_manager.py get-agents); do
    INBOX_COUNT=$(find "agent_communication/$agent/input" -name "*.json" 2>/dev/null | wc -l)
    OUTBOX_COUNT=$(find "agent_communication/$agent/output" -name "*.json" 2>/dev/null | wc -l)
    echo "   $agent: $INBOX_COUNT inbox, $OUTBOX_COUNT outbox"
done
echo ""

# 2. Recent communication activity
echo "2. Recent communication activity:"
RECENT_COUNT=$(find agent_communication/ -name "*.json" -mtime -0.1 2>/dev/null | wc -l)
echo "   Messages in last 2.4 hours: $RECENT_COUNT"
echo ""

# 3. Stale messages
echo "3. Stale messages:"
STALE_COUNT=$(find agent_communication/ -name "*.json" -mtime +0.5 2>/dev/null | wc -l)
echo "   Messages older than 12 hours: $STALE_COUNT"
if [[ $STALE_COUNT -gt 0 ]]; then
    echo "   ⚠️  Consider cleanup: find agent_communication/ -name '*.json' -mtime +0.5 -delete"
fi
echo ""

# 4. Communication errors
echo "4. Communication errors:"
COMM_ERRORS=$(grep -r "communication.*error\|timeout.*communication" logs/ 2>/dev/null | wc -l)
echo "   Communication errors in logs: $COMM_ERRORS"
```

### Network Connectivity Issues

```bash
#!/bin/bash
# network_diagnosis.sh

echo "🌐 Network Connectivity Diagnosis"
echo "================================="

# 1. Local connectivity
echo "1. Local connectivity:"
if nc -z localhost 8080 2>/dev/null; then
    echo "   ✅ Local port 8080 accessible"
else
    echo "   ❌ Local port 8080 not accessible"
fi

# 2. File system permissions
echo "2. File system permissions:"
if [[ -w agent_communication/ ]]; then
    echo "   ✅ Communication directory writable"
else
    echo "   ❌ Communication directory not writable"
fi

# 3. Inter-process communication
echo "3. Inter-process communication:"
if [[ -p /tmp/coordination_pipe ]]; then
    echo "   ✅ Named pipe exists"
else
    echo "   ℹ️  Named pipe not found (may use different IPC method)"
fi
```

## Emergency Procedures

### System Unresponsive

```bash
#!/bin/bash
# emergency_unresponsive.sh

echo "🚨 EMERGENCY: System Unresponsive Recovery"

# 1. Force kill all processes
echo "1. Force terminating all coordination processes..."
pkill -KILL -f "coordination\|lifecycle\|manage_agent"
sleep 5

# 2. Clean up resources
echo "2. Cleaning up system resources..."
rm -f *.pid
rm -f /tmp/coordination_*
ipcs -s | grep $(whoami) | awk '{print $2}' | xargs -r ipcrm -s  # Clean semaphores

# 3. Check system resources
echo "3. Checking system resources..."
df -h .
free -h

# 4. Emergency restart
echo "4. Attempting emergency restart..."
export EMERGENCY_MODE=1
./coordination_manager.sh init
./manage_agents.sh set-count 2
./lifecycle_daemon.sh start --emergency

# 5. Verify minimal operation
sleep 30
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    echo "✅ Emergency restart successful"
else
    echo "❌ Emergency restart failed - system may need manual intervention"
    echo "Suggestions:"
    echo "1. Reboot the machine"
    echo "2. Check system logs: journalctl -xe"
    echo "3. Check disk space and permissions"
fi
```

### Data Corruption Emergency

```bash
#!/bin/bash
# emergency_data_corruption.sh

echo "🚨 EMERGENCY: Data Corruption Recovery"

# 1. Stop all processes immediately
./emergency_shutdown.sh

# 2. Assess corruption extent
echo "Assessing corruption extent..."
CORRUPTED_COUNT=0
for file in $(find . -name "*.json"); do
    if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
        echo "Corrupted: $file"
        CORRUPTED_COUNT=$((CORRUPTED_COUNT + 1))
    fi
done

echo "Total corrupted files: $CORRUPTED_COUNT"

# 3. Emergency backup of current state
echo "Creating emergency backup..."
tar -czf "emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
    --exclude="*.log" \
    --exclude="*.tmp" \
    .

# 4. Restore from backup or regenerate
if [[ $CORRUPTED_COUNT -gt 10 ]]; then
    echo "Extensive corruption detected - attempting full restore..."
    ./data_recovery.sh backup
else
    echo "Limited corruption - attempting selective recovery..."
    # Remove only corrupted files
    find . -name "*.json" -exec python3 -m json.tool {} \; 2>&1 | grep -B1 "Expecting" | grep "\.json" | xargs rm -f
    ./generate_agents.sh
    ./coordination_manager.sh init
fi

# 5. Verify recovery
echo "Verifying recovery..."
if ./manage_agents.sh list > /dev/null 2>&1; then
    echo "✅ Data corruption recovery successful"
    ./manage_agents.sh auto
else
    echo "❌ Recovery failed - manual intervention required"
fi
```

## Debug Tools

### Comprehensive Debug Information

```bash
#!/bin/bash
# generate_debug_info.sh

DEBUG_DIR="debug_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_DIR"

echo "🔍 Generating comprehensive debug information..."

# 1. System information
cat > "$DEBUG_DIR/system_info.txt" << EOF
System Debug Information
Generated: $(date)
Hostname: $(hostname)
Uptime: $(uptime)
Kernel: $(uname -a)
Python Version: $(python3 --version)
Disk Usage: $(df -h .)
Memory: $(free -h)
Load Average: $(uptime | awk -F'load average:' '{print $2}')
EOF

# 2. Process information
ps aux | grep -E "(coordination|lifecycle|manage)" > "$DEBUG_DIR/processes.txt"

# 3. Configuration files
cp *.json "$DEBUG_DIR/" 2>/dev/null
cp coordination_system/*.py "$DEBUG_DIR/" 2>/dev/null

# 4. Recent logs
mkdir -p "$DEBUG_DIR/logs"
find logs/ -name "*.log" -mtime -1 -exec cp {} "$DEBUG_DIR/logs/" \;

# 5. Agent status
mkdir -p "$DEBUG_DIR/agent_status"
cp agent_status/* "$DEBUG_DIR/agent_status/" 2>/dev/null

# 6. Communication snapshot
mkdir -p "$DEBUG_DIR/communication"
find agent_communication/ -name "*.json" -mtime -0.1 -exec cp --parents {} "$DEBUG_DIR/" \; 2>/dev/null

# 7. Network information
netstat -tuln > "$DEBUG_DIR/network.txt" 2>/dev/null
lsof -i > "$DEBUG_DIR/open_files.txt" 2>/dev/null

# 8. Performance snapshot
top -b -n 1 > "$DEBUG_DIR/performance.txt"

# 9. Error analysis
grep -r "ERROR\|CRITICAL\|FATAL" logs/ > "$DEBUG_DIR/errors.txt" 2>/dev/null

# 10. Compress debug package
tar -czf "$DEBUG_DIR.tar.gz" "$DEBUG_DIR"
rm -rf "$DEBUG_DIR"

echo "✅ Debug information generated: $DEBUG_DIR.tar.gz"
echo "📎 Include this file when reporting issues"
```

### Interactive Debug Shell

```bash
#!/bin/bash
# debug_shell.sh

echo "🔧 Multi-Agent System Debug Shell"
echo "================================="
echo "Available commands:"
echo "  status    - Show system status"
echo "  logs      - Show recent logs"
echo "  agents    - Show agent details"
echo "  comm      - Show communication status"
echo "  perf      - Show performance metrics"
echo "  test      - Run connectivity tests"
echo "  restart   - Restart specific component"
echo "  help      - Show this help"
echo "  quit      - Exit debug shell"
echo ""

while true; do
    read -p "debug> " cmd args
    
    case "$cmd" in
        "status")
            ./quick_diagnosis.sh
            ;;
        "logs")
            tail -20 logs/*.log | grep -E "ERROR|WARN|INFO"
            ;;
        "agents")
            ./manage_agents.sh status
            ;;
        "comm")
            ./diagnose_communication.sh
            ;;
        "perf")
            ./diagnose_performance.sh
            ;;
        "test")
            echo "Testing system connectivity..."
            timeout 10s ./manage_agents.sh list > /dev/null && echo "✅ System responsive" || echo "❌ System unresponsive"
            ;;
        "restart")
            if [[ -n "$args" ]]; then
                case "$args" in
                    "daemon")
                        ./lifecycle_daemon.sh restart
                        ;;
                    "agents")
                        ./manage_agents.sh restart-all
                        ;;
                    *)
                        echo "Usage: restart {daemon|agents}"
                        ;;
                esac
            else
                echo "Usage: restart {daemon|agents}"
            fi
            ;;
        "help")
            echo "Debug commands available - see list above"
            ;;
        "quit"|"exit"|"q")
            echo "Exiting debug shell"
            break
            ;;
        "")
            continue
            ;;
        *)
            echo "Unknown command: $cmd"
            echo "Type 'help' for available commands"
            ;;
    esac
    echo ""
done
```

## Summary

This troubleshooting guide provides systematic approaches to diagnosing and resolving common issues in the Multi-Agent Coordination System. Key troubleshooting principles:

1. **Start with quick diagnosis** to assess overall system health
2. **Use systematic approach** - identify, diagnose, fix, verify
3. **Check logs first** for error patterns and clues
4. **Test components individually** to isolate problems
5. **Keep backups** before making major changes
6. **Document solutions** for future reference

### Quick Reference Commands

**Emergency Stop**: `./emergency_shutdown.sh`
**Quick Diagnosis**: `./quick_diagnosis.sh`
**System Recovery**: `./crash_recovery.sh`
**Debug Information**: `./generate_debug_info.sh`
**Performance Check**: `./diagnose_performance.sh`

### Escalation Path

1. **Level 1**: Use automated diagnosis and common solutions
2. **Level 2**: Manual investigation using debug tools
3. **Level 3**: Emergency procedures and data recovery
4. **Level 4**: System rebuild or external assistance

For persistent issues not covered in this guide, generate debug information with `./generate_debug_info.sh` and consult the system logs for additional clues.