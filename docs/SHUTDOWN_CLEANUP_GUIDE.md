# Multi-Agent System Shutdown & Cleanup Guide

This guide covers safe shutdown procedures, cleanup operations, and system recovery for the Multi-Agent Coordination System.

## Table of Contents

1. [Shutdown Types](#shutdown-types)
2. [Graceful Shutdown Procedures](#graceful-shutdown-procedures)
3. [Emergency Shutdown](#emergency-shutdown)
4. [Cleanup Operations](#cleanup-operations)
5. [Data Preservation](#data-preservation)
6. [Recovery Procedures](#recovery-procedures)
7. [Maintenance Shutdowns](#maintenance-shutdowns)

## Shutdown Types

### 1. Graceful Shutdown (Recommended)
- Allows current tasks to complete
- Preserves data integrity
- Proper cleanup of resources
- Takes 30-120 seconds

### 2. Quick Shutdown
- Stops agents after current task iteration
- Minimal data loss risk
- Takes 10-30 seconds

### 3. Emergency Shutdown
- Immediate termination
- Potential data loss
- Used for critical issues
- Takes 5-10 seconds

### 4. Maintenance Shutdown
- Planned downtime for updates
- Full backup before shutdown
- Extensive cleanup operations
- Takes 2-10 minutes

## Graceful Shutdown Procedures

### Standard Graceful Shutdown

```bash
#!/bin/bash
# graceful_shutdown.sh

echo "🛑 Starting graceful shutdown of Multi-Agent Coordination System..."
echo "Timestamp: $(date)"

# Step 1: Stop accepting new tasks
echo "1. Stopping new task acceptance..."
./coordination_manager.sh pause-new-tasks
sleep 5

# Step 2: Wait for current tasks to complete
echo "2. Waiting for current tasks to complete..."
TIMEOUT=120  # 2 minutes
ELAPSED=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
    ACTIVE_TASKS=$(./coordination_manager.sh show-active-tasks | wc -l)
    if [[ $ACTIVE_TASKS -eq 0 ]]; then
        echo "   ✅ All tasks completed"
        break
    fi
    
    echo "   ⏳ $ACTIVE_TASKS tasks still active (${ELAPSED}s elapsed)"
    sleep 10
    ELAPSED=$((ELAPSED + 10))
done

if [[ $ELAPSED -ge $TIMEOUT ]]; then
    echo "   ⚠️  Timeout reached - proceeding with shutdown"
fi

# Step 3: Stop lifecycle daemon
echo "3. Stopping lifecycle daemon..."
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    ./lifecycle_daemon.sh stop
    echo "   ✅ Lifecycle daemon stopped"
else
    echo "   ℹ️  Lifecycle daemon was not running"
fi

# Step 4: Stop individual agents gracefully
echo "4. Stopping individual agents..."
AGENTS=($(./agent_theme_manager.py get-agents))
for agent in "${AGENTS[@]}"; do
    if ./manage_agents.sh status "$agent" | grep -q "Active"; then
        echo "   Stopping $agent..."
        ./manage_agents.sh stop "$agent"
        sleep 2
    fi
done

# Step 5: Stop coordination manager
echo "5. Stopping coordination manager..."
COORD_PID=$(pgrep -f coordination_manager.sh)
if [[ -n "$COORD_PID" ]]; then
    kill -TERM "$COORD_PID"
    sleep 5
    if kill -0 "$COORD_PID" 2>/dev/null; then
        kill -KILL "$COORD_PID"
    fi
    echo "   ✅ Coordination manager stopped"
fi

# Step 6: Clean up temporary files
echo "6. Cleaning up temporary files..."
find /tmp -name "coordination_*" -delete 2>/dev/null
find agent_communication/ -name "*.tmp" -delete 2>/dev/null
echo "   ✅ Temporary files cleaned"

# Step 7: Save final state
echo "7. Saving final system state..."
./coordination_manager.sh save-state "shutdown_$(date +%Y%m%d_%H%M%S).json"
echo "   ✅ System state saved"

# Step 8: Verify shutdown
echo "8. Verifying shutdown..."
REMAINING_PROCESSES=$(ps aux | grep -E "(coordination|lifecycle|manage_agent)" | grep -v grep | wc -l)
if [[ $REMAINING_PROCESSES -eq 0 ]]; then
    echo "   ✅ All processes stopped successfully"
else
    echo "   ⚠️  $REMAINING_PROCESSES processes still running"
    ps aux | grep -E "(coordination|lifecycle|manage_agent)" | grep -v grep
fi

echo ""
echo "🏁 Graceful shutdown completed: $(date)"
echo "System is now safely stopped."
```

### Agent-by-Agent Graceful Shutdown

```bash
#!/bin/bash
# graceful_agent_shutdown.sh

stop_agent_gracefully() {
    local agent=$1
    local timeout=${2:-60}
    
    echo "Gracefully stopping $agent..."
    
    # Send stop signal to agent
    ./manage_agents.sh send-signal "$agent" STOP
    
    # Wait for agent to finish current task
    local elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if ! ./manage_agents.sh status "$agent" | grep -q "Active"; then
            echo "  ✅ $agent stopped gracefully"
            return 0
        fi
        
        echo "  ⏳ Waiting for $agent to complete current task (${elapsed}s)"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    # Force stop if timeout reached
    echo "  ⚠️  Timeout reached - force stopping $agent"
    ./manage_agents.sh stop "$agent" --force
    return 1
}

# Stop all agents gracefully
AGENTS=($(./agent_theme_manager.py get-agents))
for agent in "${AGENTS[@]}"; do
    if ./manage_agents.sh status "$agent" | grep -q "Active"; then
        stop_agent_gracefully "$agent" 60
    fi
done
```

### Project-Specific Graceful Shutdown

```bash
#!/bin/bash
# graceful_project_shutdown.sh

PROJECT_NAME="$1"

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

echo "🛑 Gracefully shutting down project: $PROJECT_NAME"

# 1. Pause project tasks
./project_manager.sh pause "$PROJECT_NAME"

# 2. Wait for project tasks to complete
echo "Waiting for project tasks to complete..."
TIMEOUT=180  # 3 minutes for projects
ELAPSED=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
    ACTIVE_TASKS=$(./project_manager.sh status "$PROJECT_NAME" | grep -c "Active")
    if [[ $ACTIVE_TASKS -eq 0 ]]; then
        echo "✅ All project tasks completed"
        break
    fi
    
    echo "⏳ $ACTIVE_TASKS tasks still active (${ELAPSED}s elapsed)"
    sleep 15
    ELAPSED=$((ELAPSED + 15))
done

# 3. Stop project agents
echo "Stopping project agents..."
./project_manager.sh stop "$PROJECT_NAME"

# 4. Archive project state
echo "Archiving project state..."
./project_manager.sh archive "$PROJECT_NAME"

echo "🏁 Project $PROJECT_NAME shutdown completed"
```

## Emergency Shutdown

### Immediate Emergency Shutdown

```bash
#!/bin/bash
# emergency_shutdown.sh

echo "🚨 EMERGENCY SHUTDOWN - IMMEDIATE TERMINATION"
echo "Timestamp: $(date)"

# 1. Kill all coordination processes immediately
echo "1. Terminating all coordination processes..."
pkill -KILL -f "python.*coordination"
pkill -KILL -f "lifecycle_daemon"
pkill -KILL -f "manage_agents"
pkill -KILL -f "coordination_manager"

# 2. Remove PID files
echo "2. Cleaning up PID files..."
rm -f lifecycle_daemon.pid
rm -f coordination_manager.pid
rm -f agent_*.pid

# 3. Mark emergency shutdown in logs
echo "3. Logging emergency shutdown..."
echo "[$(date)] EMERGENCY SHUTDOWN EXECUTED" >> logs/emergency.log

# 4. Save crash state if possible
echo "4. Attempting to save crash state..."
if [[ -d "agent_status" ]]; then
    cp -r agent_status/ "crash_state_$(date +%Y%m%d_%H%M%S)/"
fi

# 5. Verify all processes stopped
echo "5. Verifying process termination..."
REMAINING=$(ps aux | grep -E "(coordination|lifecycle|manage_agent)" | grep -v grep | wc -l)
if [[ $REMAINING -eq 0 ]]; then
    echo "✅ All processes terminated"
else
    echo "⚠️  $REMAINING processes may still be running"
    ps aux | grep -E "(coordination|lifecycle|manage_agent)" | grep -v grep
fi

echo ""
echo "🚨 EMERGENCY SHUTDOWN COMPLETED: $(date)"
echo "⚠️  SYSTEM MAY NEED RECOVERY - CHECK LOGS AND DATA INTEGRITY"
```

### Selective Emergency Stop

```bash
#!/bin/bash
# emergency_stop_component.sh

COMPONENT="$1"

case "$COMPONENT" in
    "daemon")
        echo "🚨 Emergency stop: Lifecycle Daemon"
        pkill -KILL -f lifecycle_daemon
        rm -f lifecycle_daemon.pid
        ;;
    "agents")
        echo "🚨 Emergency stop: All Agents"
        pkill -KILL -f "python.*agent"
        rm -f agent_*.pid
        ;;
    "coordination")
        echo "🚨 Emergency stop: Coordination Manager"
        pkill -KILL -f coordination_manager
        rm -f coordination_manager.pid
        ;;
    "project")
        PROJECT="$2"
        echo "🚨 Emergency stop: Project $PROJECT"
        ./project_manager.sh emergency-stop "$PROJECT"
        ;;
    *)
        echo "Usage: $0 {daemon|agents|coordination|project} [project_name]"
        exit 1
        ;;
esac

echo "Emergency stop of $COMPONENT completed"
```

## Cleanup Operations

### Standard Cleanup

```bash
#!/bin/bash
# standard_cleanup.sh

echo "🧹 Starting standard system cleanup..."

# 1. Clean temporary files
echo "1. Cleaning temporary files..."
find /tmp -name "coordination_*" -mtime +1 -delete
find . -name "*.tmp" -delete
find . -name ".DS_Store" -delete
echo "   ✅ Temporary files cleaned"

# 2. Clean old log files
echo "2. Cleaning old log files..."
find logs/ -name "*.log.*" -mtime +30 -delete
find logs/ -name "*.log" -size +100M -exec truncate -s 50M {} \;
echo "   ✅ Old log files cleaned"

# 3. Clean stale communication files
echo "3. Cleaning stale communication files..."
find agent_communication/ -name "*.json" -mtime +7 -delete
find agent_communication/ -name "archive/*.json" -mtime +30 -delete
echo "   ✅ Stale communication files cleaned"

# 4. Clean old metrics
echo "4. Cleaning old metrics..."
find metrics/ -name "*_daily.json" -mtime +90 -delete
find metrics/ -name "*_hourly.json" -mtime +7 -delete
echo "   ✅ Old metrics cleaned"

# 5. Clean orphaned worktrees
echo "5. Cleaning orphaned worktrees..."
./worktree_manager.sh prune
echo "   ✅ Orphaned worktrees cleaned"

# 6. Clean agent status files
echo "6. Cleaning stale agent status files..."
find agent_status/ -name "*.json" -mtime +1 -delete
echo "   ✅ Stale status files cleaned"

echo "🧹 Standard cleanup completed"
```

### Deep Cleanup

```bash
#!/bin/bash
# deep_cleanup.sh

echo "🧹 Starting deep system cleanup..."

# 1. Archive old data
echo "1. Archiving old data..."
ARCHIVE_DIR="archive_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

# Archive old logs
find logs/ -name "*.log.*" -mtime +7 -exec mv {} "$ARCHIVE_DIR"/ \;

# Archive old metrics
find metrics/ -name "*.json" -mtime +30 -exec mv {} "$ARCHIVE_DIR"/ \;

# Archive old projects
find projects/ -maxdepth 1 -type d -mtime +90 -exec mv {} "$ARCHIVE_DIR"/ \;

# Compress archive
tar -czf "${ARCHIVE_DIR}.tar.gz" "$ARCHIVE_DIR"
rm -rf "$ARCHIVE_DIR"
echo "   ✅ Old data archived to ${ARCHIVE_DIR}.tar.gz"

# 2. Database cleanup (if applicable)
echo "2. Database cleanup..."
if [[ -f "coordination.db" ]]; then
    sqlite3 coordination.db "DELETE FROM logs WHERE timestamp < datetime('now', '-30 days');"
    sqlite3 coordination.db "DELETE FROM metrics WHERE timestamp < datetime('now', '-90 days');"
    sqlite3 coordination.db "VACUUM; ANALYZE;"
    echo "   ✅ Database cleaned and optimized"
fi

# 3. Reset system state
echo "3. Resetting system state..."
rm -rf agent_communication/*/input/*.json
rm -rf agent_communication/*/output/*.json
mkdir -p agent_communication/{input,output,status}
echo "   ✅ Communication channels reset"

# 4. Clear caches
echo "4. Clearing caches..."
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
echo "   ✅ Caches cleared"

# 5. Regenerate system files
echo "5. Regenerating system files..."
./generate_agents.sh
./coordination_manager.sh init
echo "   ✅ System files regenerated"

echo "🧹 Deep cleanup completed"
```

### Project-Specific Cleanup

```bash
#!/bin/bash
# project_cleanup.sh

PROJECT_NAME="$1"
CLEANUP_TYPE="${2:-standard}"  # standard, deep, or archive

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Usage: $0 <project_name> [standard|deep|archive]"
    exit 1
fi

echo "🧹 Cleaning up project: $PROJECT_NAME (type: $CLEANUP_TYPE)"

PROJECT_DIR="projects/$(./project_manager.sh get-project-id "$PROJECT_NAME")"

if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

case "$CLEANUP_TYPE" in
    "standard")
        # Clean temporary files
        find "$PROJECT_DIR" -name "*.tmp" -delete
        find "$PROJECT_DIR/logs" -name "*.log.*" -mtime +7 -delete
        
        # Clean old task assignments
        find "$PROJECT_DIR/task_assignments" -name "*.json" -mtime +1 -delete
        
        echo "✅ Standard project cleanup completed"
        ;;
        
    "deep")
        # Reset project state
        rm -rf "$PROJECT_DIR/agent_status"/*
        rm -rf "$PROJECT_DIR/agent_communication"/*
        rm -rf "$PROJECT_DIR/task_assignments"/*
        rm -rf "$PROJECT_DIR/logs"/*
        
        # Recreate directory structure
        ./project_manager.sh init-project-structure "$PROJECT_NAME"
        
        echo "✅ Deep project cleanup completed"
        ;;
        
    "archive")
        # Archive entire project
        ARCHIVE_NAME="archived_${PROJECT_NAME}_$(date +%Y%m%d_%H%M%S)"
        mv "$PROJECT_DIR" "projects/$ARCHIVE_NAME"
        tar -czf "projects/$ARCHIVE_NAME.tar.gz" "projects/$ARCHIVE_NAME"
        rm -rf "projects/$ARCHIVE_NAME"
        
        echo "✅ Project archived to projects/$ARCHIVE_NAME.tar.gz"
        ;;
        
    *)
        echo "❌ Invalid cleanup type: $CLEANUP_TYPE"
        echo "Valid types: standard, deep, archive"
        exit 1
        ;;
esac
```

## Data Preservation

### Pre-Shutdown Backup

```bash
#!/bin/bash
# pre_shutdown_backup.sh

BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating pre-shutdown backup: $BACKUP_DIR"

# 1. Create backup directory
mkdir -p "$BACKUP_DIR"

# 2. Backup critical data
echo "Backing up critical data..."

# System configuration
cp -r agent_config.json "$BACKUP_DIR"/ 2>/dev/null
cp -r coordination_system/ "$BACKUP_DIR"/ 2>/dev/null

# Agent status and communication
cp -r agent_status/ "$BACKUP_DIR"/ 2>/dev/null
cp -r agent_communication/ "$BACKUP_DIR"/ 2>/dev/null

# Projects
cp -r projects/ "$BACKUP_DIR"/ 2>/dev/null

# Recent logs (last 24 hours)
mkdir -p "$BACKUP_DIR/logs"
find logs/ -name "*.log" -mtime -1 -exec cp {} "$BACKUP_DIR/logs/" \;

# Metrics (last 7 days)
mkdir -p "$BACKUP_DIR/metrics"
find metrics/ -name "*.json" -mtime -7 -exec cp {} "$BACKUP_DIR/metrics/" \;

# Database (if exists)
if [[ -f "coordination.db" ]]; then
    cp coordination.db "$BACKUP_DIR"/
fi

# 3. Create backup manifest
cat > "$BACKUP_DIR/BACKUP_MANIFEST.txt" << EOF
Multi-Agent System Backup
Created: $(date)
Backup Type: Pre-shutdown
System State: $(./manage_agents.sh status | grep -c "Active") active agents

Contents:
- System configuration files
- Agent status and communication history
- All project data
- Recent logs (24 hours)
- Recent metrics (7 days)
- Database snapshot (if applicable)

To restore:
1. Stop system: ./emergency_shutdown.sh
2. Extract backup: tar -xzf $BACKUP_DIR.tar.gz
3. Copy files to original locations
4. Restart system: ./manage_agents.sh auto
EOF

# 4. Compress backup
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup created: $BACKUP_DIR.tar.gz"
echo "   Size: $(du -h "$BACKUP_DIR.tar.gz" | cut -f1)"
```

### State Preservation

```bash
#!/bin/bash
# preserve_system_state.sh

STATE_FILE="system_state_$(date +%Y%m%d_%H%M%S).json"
echo "💾 Preserving system state to: $STATE_FILE"

# Collect comprehensive system state
cat > "$STATE_FILE" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "system_info": {
        "hostname": "$(hostname)",
        "uptime": "$(uptime)",
        "load_average": "$(uptime | awk -F'load average:' '{print $2}')",
        "disk_usage": "$(df -h . | tail -1)"
    },
    "daemon_status": {
        "lifecycle_daemon": "$(./lifecycle_daemon.sh status 2>/dev/null || echo 'stopped')",
        "coordination_manager": "$(pgrep -f coordination_manager >/dev/null && echo 'running' || echo 'stopped')"
    },
    "agent_status": {
EOF

# Add agent status
AGENTS=($(./agent_theme_manager.py get-agents))
for i in "${!AGENTS[@]}"; do
    agent="${AGENTS[$i]}"
    status=$(./manage_agents.sh status "$agent" 2>/dev/null || echo "unknown")
    echo "        \"$agent\": \"$status\"$([ $i -lt $((${#AGENTS[@]}-1)) ] && echo ",")" >> "$STATE_FILE"
done

cat >> "$STATE_FILE" << EOF
    },
    "project_status": {
EOF

# Add project status
PROJECTS=($(./project_manager.sh list 2>/dev/null | cut -d: -f1))
for i in "${!PROJECTS[@]}"; do
    project="${PROJECTS[$i]}"
    status=$(./project_manager.sh info "$project" 2>/dev/null | grep "Status:" | cut -d: -f2 | tr -d ' ')
    echo "        \"$project\": \"$status\"$([ $i -lt $((${#PROJECTS[@]}-1)) ] && echo ",")" >> "$STATE_FILE"
done

cat >> "$STATE_FILE" << EOF
    },
    "resource_usage": {
        "processes": $(ps aux | grep -E "(coordination|lifecycle)" | grep -v grep | wc -l),
        "cpu_usage": $(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $3} END {print sum+0}'),
        "memory_usage": $(ps aux | grep -E "(coordination|lifecycle)" | awk '{sum += $4} END {print sum+0}')
    },
    "communication_stats": {
        "recent_messages": $(find agent_communication/ -name "*.json" -mtime -0.1 | wc -l),
        "total_channels": $(find agent_communication/ -type d -name "input" | wc -l)
    }
}
EOF

echo "✅ System state preserved: $STATE_FILE"
```

## Recovery Procedures

### Post-Emergency Recovery

```bash
#!/bin/bash
# post_emergency_recovery.sh

echo "🔧 Starting post-emergency recovery procedures..."

# 1. Check for data corruption
echo "1. Checking for data corruption..."
CHECK_FAILED=false

# Check critical files
for file in agent_config.json; do
    if [[ -f "$file" ]]; then
        if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
            echo "   ❌ Corrupted file detected: $file"
            CHECK_FAILED=true
        fi
    fi
done

# Check directories
for dir in agent_status agent_communication coordination_system; do
    if [[ ! -d "$dir" ]]; then
        echo "   ❌ Missing directory: $dir"
        CHECK_FAILED=true
    fi
done

if [[ "$CHECK_FAILED" == "true" ]]; then
    echo "   ⚠️  Data corruption detected - attempting recovery..."
    
    # Restore from backup if available
    LATEST_BACKUP=$(ls -t backup_*.tar.gz 2>/dev/null | head -1)
    if [[ -n "$LATEST_BACKUP" ]]; then
        echo "   🔄 Restoring from backup: $LATEST_BACKUP"
        tar -xzf "$LATEST_BACKUP"
        # Copy critical files
        cp -r backup_*/agent_config.json . 2>/dev/null
        cp -r backup_*/coordination_system . 2>/dev/null
        rm -rf backup_*/
    else
        echo "   ⚠️  No backup available - regenerating system files..."
        ./coordination_manager.sh init
        ./generate_agents.sh
    fi
fi

# 2. Clean up crash artifacts
echo "2. Cleaning up crash artifacts..."
rm -f *.pid
rm -f /tmp/coordination_*
find . -name "core.*" -delete
echo "   ✅ Crash artifacts cleaned"

# 3. Verify system integrity
echo "3. Verifying system integrity..."
if ! ./coordination_manager.sh check-integrity; then
    echo "   ❌ System integrity check failed"
    echo "   🔄 Attempting automatic repair..."
    ./coordination_manager.sh repair
fi

# 4. Gradual restart
echo "4. Starting gradual system restart..."
./manage_agents.sh set-count 2  # Start with fewer agents
./coordination_manager.sh init
./lifecycle_daemon.sh start

# Wait and verify
sleep 30
if ./lifecycle_daemon.sh status | grep -q "is running"; then
    echo "   ✅ Basic system restart successful"
    
    # Gradually increase agent count
    ./manage_agents.sh set-count 4
    sleep 60
    
    ACTIVE_AGENTS=$(./manage_agents.sh status | grep -c "Active")
    if [[ $ACTIVE_AGENTS -gt 0 ]]; then
        echo "   ✅ Agent recovery successful ($ACTIVE_AGENTS agents active)"
        
        # Return to normal agent count
        ./manage_agents.sh set-count 6
    else
        echo "   ⚠️  Agent recovery incomplete - manual intervention required"
    fi
else
    echo "   ❌ System restart failed - manual intervention required"
fi

echo "🔧 Post-emergency recovery completed"
```

### Data Recovery

```bash
#!/bin/bash
# data_recovery.sh

RECOVERY_TYPE="$1"  # backup, state, or manual

echo "💾 Starting data recovery (type: $RECOVERY_TYPE)..."

case "$RECOVERY_TYPE" in
    "backup")
        # Restore from latest backup
        LATEST_BACKUP=$(ls -t backup_*.tar.gz 2>/dev/null | head -1)
        if [[ -n "$LATEST_BACKUP" ]]; then
            echo "Restoring from backup: $LATEST_BACKUP"
            
            # Create recovery directory
            RECOVERY_DIR="recovery_$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$RECOVERY_DIR"
            
            # Extract backup
            tar -xzf "$LATEST_BACKUP" -C "$RECOVERY_DIR"
            
            # Restore files selectively
            cp -r "$RECOVERY_DIR"/*/agent_config.json . 2>/dev/null
            cp -r "$RECOVERY_DIR"/*/projects . 2>/dev/null
            cp -r "$RECOVERY_DIR"/*/coordination_system . 2>/dev/null
            
            rm -rf "$RECOVERY_DIR"
            echo "✅ Backup restoration completed"
        else
            echo "❌ No backup files found"
            exit 1
        fi
        ;;
        
    "state")
        # Restore from saved state
        LATEST_STATE=$(ls -t system_state_*.json 2>/dev/null | head -1)
        if [[ -n "$LATEST_STATE" ]]; then
            echo "Restoring from state: $LATEST_STATE"
            
            # Extract configuration from state
            python3 << EOF
import json
with open('$LATEST_STATE', 'r') as f:
    state = json.load(f)

# Restore agent configuration
import os
if not os.path.exists('agent_config.json'):
    config = {
        'theme': 'greek_letters',
        'agent_count': len(state.get('agent_status', {})),
        'last_updated': state['timestamp']
    }
    with open('agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)

print("State-based recovery configuration created")
EOF
            
            # Regenerate system files
            ./generate_agents.sh
            ./coordination_manager.sh init
            
            echo "✅ State-based restoration completed"
        else
            echo "❌ No state files found"
            exit 1
        fi
        ;;
        
    "manual")
        echo "Manual recovery mode - creating minimal working system..."
        
        # Create basic configuration
        cat > agent_config.json << EOF
{
    "theme": "greek_letters",
    "agent_count": 3,
    "agents": ["alpha", "beta", "gamma"],
    "created": "$(date -Iseconds)",
    "recovery_mode": true
}
EOF
        
        # Create minimal directory structure
        mkdir -p agent_status agent_communication logs metrics projects
        
        # Generate basic system files
        ./generate_agents.sh
        ./coordination_manager.sh init
        
        echo "✅ Manual recovery system created"
        echo "ℹ️  System is in minimal state - reconfigure as needed"
        ;;
        
    *)
        echo "Usage: $0 {backup|state|manual}"
        exit 1
        ;;
esac

echo "💾 Data recovery completed"
```

## Maintenance Shutdowns

### Planned Maintenance Shutdown

```bash
#!/bin/bash
# maintenance_shutdown.sh

MAINTENANCE_TYPE="$1"  # update, cleanup, or backup
ESTIMATED_DURATION="$2"  # in minutes

echo "🔧 Starting planned maintenance shutdown"
echo "Type: $MAINTENANCE_TYPE"
echo "Estimated Duration: ${ESTIMATED_DURATION:-Unknown} minutes"
echo "Start Time: $(date)"

# 1. Create maintenance notification
cat > MAINTENANCE_NOTICE.txt << EOF
MAINTENANCE IN PROGRESS

Start Time: $(date)
Type: $MAINTENANCE_TYPE
Estimated Duration: ${ESTIMATED_DURATION:-Unknown} minutes
Status: In Progress

System is temporarily offline for scheduled maintenance.
EOF

# 2. Create comprehensive backup
echo "Creating pre-maintenance backup..."
./pre_shutdown_backup.sh

# 3. Graceful shutdown with extended timeout
echo "Performing graceful shutdown..."
ORIGINAL_TIMEOUT=300  # 5 minutes for maintenance
export AGENT_SHUTDOWN_TIMEOUT=$ORIGINAL_TIMEOUT
./graceful_shutdown.sh

# 4. Perform maintenance tasks
echo "Performing maintenance tasks..."
case "$MAINTENANCE_TYPE" in
    "update")
        echo "Updating system components..."
        git pull origin main
        pip install -r requirements.txt --upgrade
        ./coordination_system/migrate_data.py
        ;;
    "cleanup")
        echo "Performing deep cleanup..."
        ./deep_cleanup.sh
        ;;
    "backup")
        echo "Creating full system backup..."
        ./create_full_backup.sh
        ;;
esac

# 5. Update maintenance notice
cat > MAINTENANCE_NOTICE.txt << EOF
MAINTENANCE COMPLETED

Start Time: $(date)
Type: $MAINTENANCE_TYPE
Duration: $((SECONDS/60)) minutes
Status: Completed

System maintenance completed successfully.
Restart with: ./manage_agents.sh auto
EOF

echo "🔧 Maintenance shutdown completed"
echo "Duration: $((SECONDS/60)) minutes"
echo "To restart system: ./manage_agents.sh auto"
```

### Rolling Restart (Zero-Downtime)

```bash
#!/bin/bash
# rolling_restart.sh

echo "🔄 Starting rolling restart (zero-downtime maintenance)..."

AGENTS=($(./agent_theme_manager.py get-agents))
BATCH_SIZE=2  # Restart 2 agents at a time

# Restart agents in batches
for ((i=0; i<${#AGENTS[@]}; i+=BATCH_SIZE)); do
    BATCH_AGENTS=("${AGENTS[@]:i:BATCH_SIZE}")
    
    echo "Restarting batch: ${BATCH_AGENTS[*]}"
    
    # Stop batch
    for agent in "${BATCH_AGENTS[@]}"; do
        ./manage_agents.sh stop "$agent"
    done
    
    # Wait for graceful stop
    sleep 30
    
    # Start batch
    for agent in "${BATCH_AGENTS[@]}"; do
        ./manage_agents.sh start "$agent"
    done
    
    # Wait for startup and verification
    sleep 60
    
    # Verify batch is healthy
    for agent in "${BATCH_AGENTS[@]}"; do
        if ! ./manage_agents.sh status "$agent" | grep -q "Active"; then
            echo "⚠️  Warning: $agent failed to restart properly"
        fi
    done
    
    echo "Batch restart completed: ${BATCH_AGENTS[*]}"
done

echo "🔄 Rolling restart completed"
./manage_agents.sh status
```

## Summary

Proper shutdown and cleanup procedures are essential for maintaining system integrity and enabling reliable recovery. Key principles:

1. **Always prefer graceful shutdown** when possible
2. **Create backups before major operations**
3. **Use emergency shutdown only when necessary**
4. **Perform regular cleanup to prevent resource exhaustion**
5. **Test recovery procedures regularly**
6. **Document any emergency situations for analysis**

For normal operations, use:
- `./graceful_shutdown.sh` for planned shutdowns
- `./standard_cleanup.sh` for regular maintenance
- `./pre_shutdown_backup.sh` before any major changes

For emergency situations:
- `./emergency_shutdown.sh` for immediate termination
- `./post_emergency_recovery.sh` for system recovery
- `./data_recovery.sh backup` to restore from backups

These procedures ensure reliable system operation and minimize data loss in all shutdown scenarios.