#!/bin/bash
# Comprehensive Agent Management System

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COORDINATION_FILE="AGENT_COORDINATION.md"
THEME_MANAGER="./development/agent_theme_manager.py"

# Function to show header
show_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                   AGENT MANAGEMENT SYSTEM                                      ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show help
show_help() {
    show_header
    echo -e "${CYAN}=== Agent Management System ===${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo -e "${YELLOW}Agent Control:${NC}"
    echo "  start <agent>     - Start a specific agent"
    echo "  auto              - Start all agents automatically"
    echo "  status            - Show current agent status"
    echo "  list              - List all available agents"
    echo ""
    echo -e "${YELLOW}Monitoring:${NC}"
    echo "  monitor           - Launch advanced monitoring dashboard"
    echo "  health            - Show agent health summary"
    echo "  processes         - Show running Claude processes"
    echo "  alerts            - Show system alerts"
    echo "  watch             - Monitor continuously"
    echo ""
    echo -e "${YELLOW}Notifications:${NC}"
    echo "  check             - Check agents and send notifications"
    echo "  notify <agent> <message> - Send custom notification"
    echo "  notifications     - Show recent notifications"
    echo ""
    echo -e "${YELLOW}Management:${NC}"
    echo "  snapshot          - Create status snapshot"
    echo "  log               - Show recent monitoring logs"
    echo "  cleanup           - Clean old logs and snapshots"
    echo "  help              - Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 auto                           - Start all agents"
    echo "  $0 monitor                        - Launch monitoring dashboard"
    echo "  $0 check                          - Check all agents for updates"
    echo "  $0 start alpha                    - Start Agent Alpha only"
    echo ""
    echo -e "${YELLOW}Files:${NC}"
    echo "  AGENT_COORDINATION.md             - Agent coordination file"
    echo "  AGENT_STATUS_UPDATE_GUIDE.md      - Status update guide"
    echo "  monitor_agents_advanced.sh        - Advanced monitoring system"
    echo "  notify_agents.sh                  - Notification system"
    echo "  manage_agents.sh                  - Basic agent management"
}

# Function to check if required files exist
check_requirements() {
    local missing_files=()
    
    if [[ ! -f "manage_agents.sh" ]]; then
        missing_files+=("manage_agents.sh")
    fi
    
    if [[ ! -f "monitor_agents_advanced.sh" ]]; then
        missing_files+=("monitor_agents_advanced.sh")
    fi
    
    if [[ ! -f "notify_agents.sh" ]]; then
        missing_files+=("notify_agents.sh")
    fi
    
    if [[ ! -f "$COORDINATION_FILE" ]]; then
        missing_files+=("$COORDINATION_FILE")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "${RED}Missing required files:${NC}"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        return 1
    fi
    
    return 0
}

# Function to get system overview
get_system_overview() {
    echo -e "${CYAN}=== System Overview ===${NC}"
    echo ""
    
    # Count Claude processes
    local claude_processes=$(ps aux | grep -E "claude\s" | grep -v grep | wc -l | tr -d ' ')
    echo "Claude Processes: $claude_processes"
    
    # Check coordination file age
    if [[ -f "$COORDINATION_FILE" ]]; then
        local file_age=$(( $(date +%s) - $(stat -f %m "$COORDINATION_FILE") ))
        echo "Coordination File Age: $(($file_age / 60)) minutes"
    fi
    
    # Check log files
    local log_files=$(ls -1 *.log 2>/dev/null | wc -l | tr -d ' ')
    echo "Log Files: $log_files"
    
    # Check snapshots
    local snapshots=$(ls -1 agent_status/snapshot_*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "Status Snapshots: $snapshots"
    
    echo ""
}

# Function to run agent control commands
run_agent_control() {
    local command=$1
    shift
    
    echo -e "${CYAN}Running agent control: $command${NC}"
    
    case "$command" in
        "start"|"auto"|"status"|"list")
            if [[ -f "manage_agents.sh" ]]; then
                ./manage_agents.sh "$command" "$@"
            else
                echo -e "${RED}manage_agents.sh not found${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown agent control command: $command${NC}"
            return 1
            ;;
    esac
}

# Function to run monitoring commands
run_monitoring() {
    local command=$1
    shift
    
    echo -e "${CYAN}Running monitoring: $command${NC}"
    
    case "$command" in
        "monitor"|"dashboard")
            if [[ -f "monitor_agents_advanced.sh" ]]; then
                ./monitor_agents_advanced.sh dashboard
            else
                echo -e "${RED}monitor_agents_advanced.sh not found${NC}"
                return 1
            fi
            ;;
        "health"|"processes"|"alerts"|"watch")
            if [[ -f "monitor_agents_advanced.sh" ]]; then
                ./monitor_agents_advanced.sh "$command" "$@"
            else
                echo -e "${RED}monitor_agents_advanced.sh not found${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown monitoring command: $command${NC}"
            return 1
            ;;
    esac
}

# Function to run notification commands
run_notifications() {
    local command=$1
    shift
    
    echo -e "${CYAN}Running notifications: $command${NC}"
    
    case "$command" in
        "check"|"notify"|"notifications")
            if [[ -f "notify_agents.sh" ]]; then
                if [[ "$command" == "notifications" ]]; then
                    ./notify_agents.sh show
                else
                    ./notify_agents.sh "$command" "$@"
                fi
            else
                echo -e "${RED}notify_agents.sh not found${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown notification command: $command${NC}"
            return 1
            ;;
    esac
}

# Function to create snapshot
create_snapshot() {
    echo -e "${CYAN}Creating status snapshot...${NC}"
    
    if [[ -f "monitor_agents_advanced.sh" ]]; then
        ./monitor_agents_advanced.sh snapshot
    else
        echo -e "${RED}monitor_agents_advanced.sh not found${NC}"
        return 1
    fi
}

# Function to show logs
show_logs() {
    echo -e "${CYAN}=== Recent Logs ===${NC}"
    echo ""
    
    if [[ -f "agent_monitoring.log" ]]; then
        echo -e "${YELLOW}Monitoring Log:${NC}"
        tail -10 agent_monitoring.log
        echo ""
    fi
    
    if [[ -f "agent_notifications.log" ]]; then
        echo -e "${YELLOW}Notifications Log:${NC}"
        tail -10 agent_notifications.log
        echo ""
    fi
}

# Function to cleanup old files
cleanup_old_files() {
    echo -e "${CYAN}Cleaning up old files...${NC}"
    
    # Clean old log files (keep last 1000 lines)
    for log_file in *.log; do
        if [[ -f "$log_file" ]]; then
            tail -1000 "$log_file" > "${log_file}.tmp"
            mv "${log_file}.tmp" "$log_file"
            echo "Cleaned $log_file"
        fi
    done
    
    # Clean old snapshots (keep last 50)
    if [[ -d "agent_status" ]]; then
        local snapshot_count=$(ls -1 agent_status/snapshot_*.json 2>/dev/null | wc -l | tr -d ' ')
        if [[ $snapshot_count -gt 50 ]]; then
            ls -1t agent_status/snapshot_*.json | tail -n +51 | xargs rm -f
            echo "Cleaned old snapshots"
        fi
    fi
    
    echo -e "${GREEN}Cleanup completed${NC}"
}

# Function to show quick status
show_quick_status() {
    show_header
    get_system_overview
    
    echo -e "${CYAN}=== Quick Agent Status ===${NC}"
    echo ""
    
    if [[ -f "monitor_agents_advanced.sh" ]]; then
        ./monitor_agents_advanced.sh status
    else
        echo -e "${RED}Advanced monitoring not available${NC}"
    fi
}

# Main function
main() {
    local command=${1:-help}
    
    # Check requirements
    if ! check_requirements; then
        echo -e "${RED}Missing required files. Please ensure all scripts are present.${NC}"
        exit 1
    fi
    
    case "$command" in
        # Agent control
        "start"|"auto"|"status"|"list")
            run_agent_control "$command" "${@:2}"
            ;;
        
        # Monitoring
        "monitor"|"dashboard"|"health"|"processes"|"alerts"|"watch")
            run_monitoring "$command" "${@:2}"
            ;;
        
        # Notifications
        "check"|"notify"|"notifications")
            run_notifications "$command" "${@:2}"
            ;;
        
        # Management
        "snapshot")
            create_snapshot
            ;;
        "log"|"logs")
            show_logs
            ;;
        "cleanup")
            cleanup_old_files
            ;;
        "overview")
            show_quick_status
            ;;
        
        # Help
        "help"|"-h"|"--help")
            show_help
            ;;
        
        # Default - show overview
        *)
            if [[ "$command" != "help" ]]; then
                echo -e "${RED}Unknown command: $command${NC}"
                echo ""
            fi
            show_quick_status
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${GREEN}Goodbye!${NC}"; exit 0' INT

# Run main function
main "$@"