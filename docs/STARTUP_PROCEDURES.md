# Multi-Agent System Startup Procedures

This document provides detailed startup procedures for the Multi-Agent Coordination System, covering initialization, configuration, and verification steps.

## Table of Contents

1. [Pre-Startup Checklist](#pre-startup-checklist)
2. [System Initialization](#system-initialization)
3. [Configuration Setup](#configuration-setup)
4. [Startup Methods](#startup-methods)
5. [Verification Procedures](#verification-procedures)
6. [Common Startup Issues](#common-startup-issues)

## Pre-Startup Checklist

### System Requirements

```bash
# Check Python version (3.8+ required)
python3 --version

# Check required dependencies
pip install -r requirements.txt

# Verify shell script permissions
ls -la *.sh | grep -E "rwxr"

# Check disk space (minimum 1GB recommended)
df -h . | tail -1
```

### Directory Structure Verification

```bash
# Check core directories exist
for dir in agent_status agent_communication coordination_system logs projects; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing - creating..."
        mkdir -p "$dir"
    fi
done

# Check script files exist
for script in manage_agents.sh coordination_manager.sh lifecycle_daemon.sh project_manager.sh; do
    if [[ -f "$script" ]]; then
        echo "✅ $script exists"
    else
        echo "❌ $script missing"
    fi
done
```

### Initial Configuration

```bash
# Set default theme if not configured
if [[ ! -f "agent_config.json" ]]; then
    echo "Setting up default configuration..."
    ./development/agent_theme_manager.py set-theme greek_letters
    ./development/agent_theme_manager.py set-count 6
fi

# Initialize coordination system
./coordination_manager.sh init
```

## System Initialization

### Step 1: Coordination System Setup

```bash
# Initialize the coordination infrastructure
./coordination_manager.sh init
```

**What this does:**
- Creates necessary directories
- Initializes status tracking files
- Sets up communication channels
- Prepares logging infrastructure
- Validates system requirements

**Expected Output:**
```
🔧 Initializing Coordination System...

✅ Created agent_status directory
✅ Created agent_communication directory  
✅ Created coordination_system directory
✅ Initialized status tracking
✅ Set up communication channels
✅ Prepared logging infrastructure

🎉 Coordination system initialized successfully!
```

### Step 2: Agent Configuration

```bash
# Check current theme configuration
./development/agent_theme_manager.py show

# Set theme if needed (optional)
./development/agent_theme_manager.py set-theme marvel

# Set agent count if needed (optional)  
./development/agent_theme_manager.py set-count 8

# Generate agent files
./generate_agents.sh
```

### Step 3: Project Setup (If Using Projects)

```bash
# Create initial project
./project_manager.sh create "Development Project" /path/to/code \
    --description "Main development project" \
    --agents 6

# Or import existing project
./project_manager.sh import existing_project_config.json
```

## Configuration Setup

### Agent Theme Configuration

```bash
# List available themes
./manage_agents.sh themes

# Available themes:
# - greek_letters: Alpha, Beta, Gamma, Delta, Epsilon, Zeta
# - marvel: Iron Man, Captain America, Thor, Hulk, Black Widow, Hawkeye  
# - greek_mythology: Zeus, Hera, Poseidon, Athena, Apollo, Artemis
# - vegetables: Carrot, Broccoli, Spinach, Tomato, Cucumber, Pepper
# ... and more

# Set theme
./manage_agents.sh set-theme marvel

# Set number of agents (1-24 depending on theme)
./manage_agents.sh set-count 8

# Generate agent configuration files
./generate_agents.sh
```

### Advanced Configuration

```bash
# Configure custom agent specializations
./coordination_system/configure_specializations.py \
    --agent ironman --specialization "backend,database" \
    --agent captainamerica --specialization "frontend,ui"

# Set resource limits
./manage_agents.sh config --max-memory 2048 --max-cpu 80

# Configure communication preferences
./coordination_manager.sh config --heartbeat-interval 30 --timeout 120
```

## Startup Methods

### Method 1: Automatic Startup (Recommended)

**Use Case**: Production environments, continuous operation

```bash
# Single command startup
./manage_agents.sh auto
```

**Detailed Steps:**
```bash
# 1. Check if already running
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    echo "System already running"
    exit 0
fi

# 2. Start lifecycle daemon
./lifecycle_daemon.sh start

# 3. Verify startup
sleep 5
./lifecycle_daemon.sh status

# 4. Monitor initial agent startup
tail -f lifecycle_daemon.log &
TAIL_PID=$!

# 5. Wait for first agents to start
sleep 15

# 6. Stop log monitoring
kill $TAIL_PID 2>/dev/null

# 7. Show status
./manage_agents.sh status
```

**Timeline:**
- T+0s: Lifecycle daemon starts
- T+10s: First agents begin startup sequence
- T+30s: Primary agents active
- T+60s: All agents operational

### Method 2: Manual Sequential Startup

**Use Case**: Development, debugging, controlled startup

```bash
# 1. Start coordination manager
./coordination_manager.sh start

# 2. Start agents one by one
AGENTS=($(./development/agent_theme_manager.py get-agents))
for agent in "${AGENTS[@]}"; do
    echo "Starting $agent..."
    ./manage_agents.sh start "$agent"
    sleep 10  # Wait between starts
done

# 3. Verify all agents started
./manage_agents.sh status
```

### Method 3: Project-Based Startup

**Use Case**: Project-specific work, isolated development

```bash
# 1. Create or switch to project
./project_manager.sh create "Feature Development" ~/projects/feature-x -a 4
# OR
./project_manager.sh switch "Existing Project"

# 2. Start project-specific agents
./project_manager.sh start "Feature Development"

# 3. Monitor project status
./project_manager.sh monitor "Feature Development"
```

### Method 4: Selective Agent Startup

**Use Case**: Resource constraints, testing specific agents

```bash
# Start specific agents only
./manage_agents.sh start ironman
./manage_agents.sh start captainamerica
./manage_agents.sh start thor

# Verify selected agents are running
./manage_agents.sh status | grep -E "ironman|captainamerica|thor"
```

### Method 5: Development Mode Startup

**Use Case**: Development, testing, frequent restarts

```bash
# Enable debug mode
export DEBUG=1
export LOG_LEVEL=DEBUG

# Start with reduced agent count
./manage_agents.sh set-count 3
./generate_agents.sh

# Start with verbose logging
./manage_agents.sh auto --verbose

# Monitor debug output
tail -f logs/debug.log
```

## Verification Procedures

### Immediate Verification (0-2 minutes)

```bash
# Check daemon is running
./lifecycle_daemon.sh status
# Expected: "Lifecycle daemon is running (PID: XXXX)"

# Check for critical errors
grep -i error logs/*.log | tail -5
# Expected: No recent critical errors

# Check agent status directory
ls -la agent_status/
# Expected: At least one .json file with recent timestamp
```

### Short-term Verification (2-5 minutes)

```bash
# Check agent startup
./manage_agents.sh status
# Expected: At least one agent showing "Active"

# Check communication channels
find agent_communication/ -name "*.json" -mtime -1 | wc -l
# Expected: > 0 (recent communication files)

# Check coordination system
./coordination_manager.sh show-all
# Expected: System status showing active agents
```

### Full System Verification (5-10 minutes)

```bash
# Run verification script
#!/bin/bash
# verify_startup.sh

echo "=== Multi-Agent System Startup Verification ==="

# 1. Daemon Status
echo "1. Lifecycle Daemon Status:"
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    echo "   ✅ Daemon is running"
else
    echo "   ❌ Daemon not running"
    exit 1
fi

# 2. Agent Count
echo "2. Active Agents:"
ACTIVE_COUNT=$(./manage_agents.sh status | grep -c "Active")
echo "   ✅ $ACTIVE_COUNT agents active"

# 3. Communication Health
echo "3. Communication Health:"
COMM_FILES=$(find agent_communication/ -name "*.json" -mtime -0.1 | wc -l)
if [[ $COMM_FILES -gt 0 ]]; then
    echo "   ✅ $COMM_FILES recent communication files"
else
    echo "   ⚠️  No recent communication activity"
fi

# 4. Log Health
echo "4. Log Health:"
ERROR_COUNT=$(grep -c "ERROR\|CRITICAL" logs/*.log 2>/dev/null | awk -F: '{sum += $2} END {print sum}')
if [[ ${ERROR_COUNT:-0} -eq 0 ]]; then
    echo "   ✅ No critical errors in logs"
else
    echo "   ⚠️  $ERROR_COUNT errors found in logs"
fi

# 5. Resource Usage
echo "5. Resource Usage:"
PROCESS_COUNT=$(ps aux | grep -c "python.*coordination")
echo "   ✅ $PROCESS_COUNT coordination processes running"

# 6. System Responsiveness
echo "6. System Responsiveness:"
timeout 10s ./manage_agents.sh list > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "   ✅ System responding normally"
else
    echo "   ❌ System unresponsive"
fi

echo ""
echo "=== Verification Complete ==="
```

### Health Check Commands

```bash
# Quick health check
./manage_agents.sh status | head -10

# Detailed health check  
./coordination_manager.sh health-check

# Performance check
ps aux | grep -E "(python.*coordination|lifecycle)" | grep -v grep

# Communication check
./coordination_system/check_communication_health.py

# Log analysis
./coordination_system/analyze_startup_logs.py
```

## Common Startup Issues

### Issue 1: Daemon Fails to Start

**Symptoms:**
```
❌ Failed to start lifecycle daemon
Error: Address already in use
```

**Diagnosis:**
```bash
# Check for existing processes
ps aux | grep lifecycle_daemon

# Check for stale PID file
ls -la lifecycle_daemon.pid

# Check port conflicts
netstat -an | grep LISTEN
```

**Solutions:**
```bash
# Kill existing processes
pkill -f lifecycle_daemon.sh
rm -f lifecycle_daemon.pid

# Clear port conflicts
lsof -ti:8080 | xargs kill -9  # Adjust port as needed

# Restart daemon
./lifecycle_daemon.sh start
```

### Issue 2: No Agents Starting

**Symptoms:**
```
No agents are currently active
All agents show status: Inactive
```

**Diagnosis:**
```bash
# Check agent configuration
cat agent_config.json

# Check dependencies
grep -r "dependencies" agent_status/

# Check blockers
grep -r "blocked" agent_status/
```

**Solutions:**
```bash
# Reset agent status
rm -f agent_status/*.json

# Regenerate agent files
./generate_agents.sh

# Manual agent start
./manage_agents.sh start alpha

# Check startup logs
tail -20 logs/agent_startup.log
```

### Issue 3: Slow Startup

**Symptoms:**
```
Agents taking >2 minutes to start
System appears hung during startup
```

**Diagnosis:**
```bash
# Check resource usage
top -n 1 | head -20

# Check disk I/O
iostat 1 5

# Check agent startup order
grep "Starting agent" logs/*.log | tail -10
```

**Solutions:**
```bash
# Reduce agent count
./manage_agents.sh set-count 3

# Increase startup timeouts
export AGENT_STARTUP_TIMEOUT=60

# Clear cache/temp files
rm -rf /tmp/coordination_*

# Restart with debug mode
DEBUG=1 ./manage_agents.sh auto
```

### Issue 4: Permission Errors

**Symptoms:**
```
Permission denied: cannot create file
mkdir: cannot create directory
```

**Diagnosis:**
```bash
# Check file permissions
ls -la *.sh

# Check directory permissions
ls -la agent_status/ agent_communication/

# Check ownership
ls -la | grep "$(whoami)"
```

**Solutions:**
```bash
# Fix script permissions
chmod +x *.sh

# Fix directory permissions
chmod 755 agent_status/ agent_communication/ logs/

# Fix ownership if needed
chown -R $(whoami):$(whoami) .

# Create missing directories
mkdir -p agent_status agent_communication logs
```

### Issue 5: Configuration Errors

**Symptoms:**
```
Invalid theme configuration
Agent count out of range
Missing configuration file
```

**Diagnosis:**
```bash
# Check configuration
./development/agent_theme_manager.py show

# Validate configuration
./development/agent_theme_manager.py validate

# Check for config file
ls -la agent_config.json
```

**Solutions:**
```bash
# Reset to defaults
./development/agent_theme_manager.py reset

# Set valid configuration
./development/agent_theme_manager.py set-theme greek_letters
./development/agent_theme_manager.py set-count 6

# Regenerate files
./generate_agents.sh
```

## Startup Performance Optimization

### Fast Startup Configuration

```bash
# Use lightweight theme
./manage_agents.sh set-theme greek_letters

# Reduce agent count
./manage_agents.sh set-count 4

# Enable performance mode
export PERFORMANCE_MODE=1

# Use minimal logging during startup
export STARTUP_LOG_LEVEL=ERROR

# Pre-warm system
./manage_agents.sh pre-warm
```

### Startup Timing Benchmarks

```bash
# Benchmark startup time
time ./manage_agents.sh auto

# Measure component startup times
./coordination_system/benchmark_startup.py

# Profile startup performance
./coordination_system/profile_startup.py --output startup_profile.json
```

## Conclusion

Proper startup procedures are critical for reliable operation of the Multi-Agent Coordination System. Key takeaways:

1. **Always run pre-startup checks** to catch issues early
2. **Use automatic startup** for production environments
3. **Verify system health** after startup
4. **Monitor logs** during the startup process  
5. **Have fallback procedures** for common issues

For ongoing operation, refer to the [System Operations Guide](SYSTEM_OPERATIONS_GUIDE.md) for monitoring and maintenance procedures.