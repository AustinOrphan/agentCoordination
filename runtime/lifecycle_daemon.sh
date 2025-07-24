#!/bin/bash
# Agent Lifecycle Daemon - Manages automatic agent start/stop based on blockers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DAEMON_NAME="agent_lifecycle_daemon"
PID_FILE="lifecycle_daemon.pid"
LOG_FILE="lifecycle_daemon.log"

# Detect if we're in multi-project mode
if [[ -f "coordination_system/global_pool_config.json" ]]; then
    PYTHON_SCRIPT="coordination_system/project_lifecycle_manager.py"
    MULTI_PROJECT_MODE=true
else
    PYTHON_SCRIPT="coordination_system/agent_lifecycle_manager.py"
    MULTI_PROJECT_MODE=false
fi

# Function to check if daemon is running
is_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to start the daemon
start_daemon() {
    if is_running; then
        echo -e "${YELLOW}Lifecycle daemon is already running${NC}"
        return 1
    fi
    
    if [[ "$MULTI_PROJECT_MODE" == "true" ]]; then
        echo -e "${CYAN}Starting Project-Aware Lifecycle Daemon with Global Task Pool...${NC}"
        
        # Get pool mode
        POOL_MODE=$(python3 -c "
import json
with open('coordination_system/global_pool_config.json', 'r') as f:
    config = json.load(f)
print(config.get('pool_mode', 'global_priority'))
" 2>/dev/null || echo "global_priority")
        
        echo -e "${BLUE}Pool mode: $POOL_MODE${NC}"
        
        # Start the project-aware lifecycle manager
        nohup python3 "$PYTHON_SCRIPT" \
            --pool-mode "$POOL_MODE" \
            >> "$LOG_FILE" 2>&1 &
    else
        echo -e "${CYAN}Starting Enhanced Agent Lifecycle Daemon with Task Assignment...${NC}"
        
        # Start the legacy lifecycle manager
        nohup python3 "$PYTHON_SCRIPT" \
            --check-interval 10 \
            --heartbeat-timeout 60 \
            >> "$LOG_FILE" 2>&1 &
    fi
    
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Give it a moment to start
    sleep 2
    
    if is_running; then
        if [[ "$MULTI_PROJECT_MODE" == "true" ]]; then
            echo -e "${GREEN}✓ Project-aware Lifecycle daemon started (PID: $pid)${NC}"
            echo -e "${GREEN}✓ Global task pool mode: $POOL_MODE${NC}"
            echo -e "${GREEN}✓ Tasks from all projects will be prioritized globally${NC}"
            echo -e "${GREEN}✓ Agents will be assigned to highest priority tasks across all projects${NC}"
        else
            echo -e "${GREEN}✓ Enhanced Lifecycle daemon started (PID: $pid)${NC}"
            echo -e "${GREEN}✓ Agents will be automatically started/stopped based on task assignments and blockers${NC}"
            echo -e "${GREEN}✓ Task assignments are processed every 30 seconds${NC}"
        fi
        echo -e "${CYAN}Monitor with: tail -f $LOG_FILE${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to start lifecycle daemon${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the daemon
stop_daemon() {
    if ! is_running; then
        echo -e "${YELLOW}Lifecycle daemon is not running${NC}"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    echo -e "${CYAN}Stopping Agent Lifecycle Daemon (PID: $pid)...${NC}"
    
    # Send SIGTERM for graceful shutdown
    kill "$pid"
    
    # Wait for process to stop
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [[ $count -lt 10 ]]; do
        sleep 1
        ((count++))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${YELLOW}Force stopping daemon...${NC}"
        kill -9 "$pid"
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ Lifecycle daemon stopped${NC}"
    return 0
}

# Function to show daemon status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}✓ Lifecycle daemon is running (PID: $pid)${NC}"
        
        # Show recent log entries
        echo ""
        echo -e "${CYAN}Recent activity:${NC}"
        tail -10 "$LOG_FILE" | grep -E "(Starting|Stopping|Blocked|unblocked)" || echo "No recent agent activity"
        
        # Show agent communication status
        echo ""
        echo -e "${CYAN}Agent Communication Directories:${NC}"
        if [[ -d "agent_communication" ]]; then
            for agent_dir in agent_communication/*/; do
                if [[ -d "$agent_dir" ]]; then
                    agent_name=$(basename "$agent_dir")
                    inbox_count=0
                    outbox_count=0
                    
                    # Count messages
                    if [[ -f "$agent_dir/input/inbox.json" ]]; then
                        inbox_count=$(python3 -c "import json; print(len(json.load(open('$agent_dir/input/inbox.json')).get('messages', [])))" 2>/dev/null || echo "0")
                    fi
                    if [[ -f "$agent_dir/output/outbox.json" ]]; then
                        outbox_count=$(python3 -c "import json; print(len(json.load(open('$agent_dir/output/outbox.json')).get('messages', [])))" 2>/dev/null || echo "0")
                    fi
                    
                    echo "  $agent_name: $inbox_count inbox, $outbox_count outbox messages"
                fi
            done
        else
            echo "  No agent communication directories found"
        fi
    else
        echo -e "${RED}✗ Lifecycle daemon is not running${NC}"
    fi
}

# Function to restart the daemon
restart_daemon() {
    echo -e "${CYAN}Restarting Agent Lifecycle Daemon...${NC}"
    stop_daemon
    sleep 2
    start_daemon
}

# Function to show logs
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${CYAN}=== Lifecycle Daemon Logs ===${NC}"
        tail -50 "$LOG_FILE"
    else
        echo -e "${YELLOW}No log file found${NC}"
    fi
}

# Function to show help
show_help() {
    echo "Agent Lifecycle Daemon Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the lifecycle daemon"
    echo "  stop     - Stop the lifecycle daemon"
    echo "  restart  - Restart the lifecycle daemon"
    echo "  status   - Show daemon status"
    echo "  logs     - Show daemon logs"
    echo "  help     - Show this help message"
    echo ""
    echo "The enhanced lifecycle daemon automatically:"
    echo "  - Assigns tasks to agents based on their roles and capabilities"
    echo "  - Monitors agent blockers and dependencies"
    echo "  - Starts agents when they have tasks assigned"
    echo "  - Stops agents when they become blocked"
    echo "  - Routes messages between agents"
    echo "  - Monitors agent heartbeats"
    echo "  - Processes task status updates from agents"
}

# Main script logic
case "${1:-help}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        restart_daemon
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac