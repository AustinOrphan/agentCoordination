#!/bin/bash
# Comprehensive Coordination Manager for Distributed Agent Status System

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
AGENT_STATUS_DIR="agent_status"
COORDINATION_DIR="coordination_system"
LOG_FILE="coordination_manager.log"
THEME_MANAGER="./development/agent_theme_manager.py"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to show header
show_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                           DISTRIBUTED AGENT COORDINATION SYSTEM                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check system requirements
check_requirements() {
    local missing_items=()
    
    # Check directories
    if [[ ! -d "$AGENT_STATUS_DIR" ]]; then
        missing_items+=("$AGENT_STATUS_DIR directory")
    fi
    
    if [[ ! -d "$COORDINATION_DIR" ]]; then
        missing_items+=("$COORDINATION_DIR directory")
    fi
    
    # Check Python scripts
    if [[ ! -f "$COORDINATION_DIR/status_aggregator.py" ]]; then
        missing_items+=("status_aggregator.py")
    fi
    
    if [[ ! -f "$COORDINATION_DIR/update_agent_status.py" ]]; then
        missing_items+=("update_agent_status.py")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_items+=("python3")
    fi
    
    if [[ ${#missing_items[@]} -gt 0 ]]; then
        echo -e "${RED}Missing required components:${NC}"
        for item in "${missing_items[@]}"; do
            echo "  - $item"
        done
        return 1
    fi
    
    return 0
}

# Function to initialize the system
initialize_system() {
    echo -e "${CYAN}Initializing distributed agent coordination system...${NC}"
    
    # Create directories
    mkdir -p "$AGENT_STATUS_DIR" "$COORDINATION_DIR"
    
    # Make Python scripts executable
    if [[ -f "$COORDINATION_DIR/status_aggregator.py" ]]; then
        chmod +x "$COORDINATION_DIR/status_aggregator.py"
    fi
    
    if [[ -f "$COORDINATION_DIR/update_agent_status.py" ]]; then
        chmod +x "$COORDINATION_DIR/update_agent_status.py"
    fi
    
    # Get current agents from theme manager
    local agents=()
    if [[ -f "$THEME_MANAGER" ]]; then
        # Use portable method instead of mapfile
        while IFS= read -r line; do
            [[ -n "$line" ]] && agents+=("$line")
        done < <("$THEME_MANAGER" get-agents)
    fi
    
    # Fallback to default agents if none found
    if [[ ${#agents[@]} -eq 0 ]]; then
        agents=("alpha" "beta" "gamma" "delta" "epsilon" "zeta")
    fi
    local missing_agents=()
    
    for agent in "${agents[@]}"; do
        if [[ ! -f "$AGENT_STATUS_DIR/${agent}_status.json" ]]; then
            missing_agents+=("$agent")
        fi
    done
    
    if [[ ${#missing_agents[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Missing agent status files:${NC}"
        for agent in "${missing_agents[@]}"; do
            echo "  - ${agent}_status.json"
        done
        echo -e "${YELLOW}You may need to create these files manually or migrate from existing coordination data.${NC}"
    fi
    
    echo -e "${GREEN}System initialized successfully!${NC}"
}

# Function to aggregate agent statuses
aggregate_statuses() {
    echo -e "${CYAN}Aggregating agent statuses...${NC}"
    
    # Try enhanced aggregator first
    if [[ -f "$COORDINATION_DIR/enhanced_status_aggregator.py" ]]; then
        cd "$COORDINATION_DIR"
        if python3 enhanced_status_aggregator.py --once --agent-dir "../$AGENT_STATUS_DIR" --output-dir ".." --config-file "../runtime/agent_config.json"; then
            echo -e "${GREEN}Status aggregation completed successfully (enhanced)${NC}"
            log "Status aggregation completed (enhanced)"
            return 0
        fi
    fi
    
    # Fall back to basic aggregator
    if [[ -f "$COORDINATION_DIR/status_aggregator.py" ]]; then
        cd "$COORDINATION_DIR"
        if python3 status_aggregator.py --agent-dir "../$AGENT_STATUS_DIR" --output-dir ".."; then
            echo -e "${GREEN}Status aggregation completed successfully${NC}"
            log "Status aggregation completed"
            return 0
        else
            echo -e "${RED}Status aggregation failed${NC}"
            log "Status aggregation failed"
            return 1
        fi
    else
        echo -e "${RED}No aggregator found${NC}"
        return 1
    fi
}

# Function to start status watcher
start_watcher() {
    local mode=${1:-enhanced}
    echo -e "${CYAN}Starting status watcher...${NC}"
    echo "Press Ctrl+C to stop"
    
    # Check which aggregator to use
    if [[ "$mode" == "enhanced" ]] && [[ -f "$COORDINATION_DIR/enhanced_status_aggregator.py" ]]; then
        echo -e "${GREEN}Using enhanced real-time aggregator with change queue${NC}"
        cd "$COORDINATION_DIR"
        log "Starting enhanced status watcher with real-time display"
        python3 enhanced_status_aggregator.py --watch --agent-dir "../$AGENT_STATUS_DIR" --output-dir ".." --config-file "../runtime/agent_config.json"
    elif [[ -f "$COORDINATION_DIR/status_aggregator.py" ]]; then
        echo -e "${YELLOW}Using basic aggregator (enhanced version not found)${NC}"
        cd "$COORDINATION_DIR"
        log "Starting basic status watcher"
        python3 status_aggregator.py --watch --interval 30 --agent-dir "../$AGENT_STATUS_DIR" --output-dir ".."
    else
        echo -e "${RED}No aggregator found${NC}"
        return 1
    fi
}

# Function to update agent status
update_agent_status() {
    local agent_id=$1
    shift
    
    if [[ -z "$agent_id" ]]; then
        echo -e "${RED}Agent ID required${NC}"
        return 1
    fi
    
    echo -e "${CYAN}Updating status for agent $agent_id...${NC}"
    
    if [[ ! -f "$COORDINATION_DIR/update_agent_status.py" ]]; then
        echo -e "${RED}update_agent_status.py not found${NC}"
        return 1
    fi
    
    cd "$COORDINATION_DIR"
    if python3 update_agent_status.py "$agent_id" --agent-dir "../$AGENT_STATUS_DIR" "$@"; then
        echo -e "${GREEN}Status updated successfully${NC}"
        log "Status updated for agent $agent_id"
        
        # Trigger aggregation
        echo -e "${CYAN}Triggering status aggregation...${NC}"
        python3 status_aggregator.py --agent-dir "../$AGENT_STATUS_DIR" --output-dir ".."
        
        return 0
    else
        echo -e "${RED}Status update failed${NC}"
        log "Status update failed for agent $agent_id"
        return 1
    fi
}

# Function to show agent status
show_agent_status() {
    local agent_id=$1
    
    if [[ -z "$agent_id" ]]; then
        echo -e "${RED}Agent ID required${NC}"
        return 1
    fi
    
    if [[ ! -f "$COORDINATION_DIR/update_agent_status.py" ]]; then
        echo -e "${RED}update_agent_status.py not found${NC}"
        return 1
    fi
    
    cd "$COORDINATION_DIR"
    python3 update_agent_status.py "$agent_id" --show --agent-dir "../$AGENT_STATUS_DIR"
}

# Function to show all agent statuses
show_all_statuses() {
    echo -e "${CYAN}=== All Agent Statuses ===${NC}"
    echo ""
    
    # Use enhanced status aggregator for better output
    if [[ -f "$COORDINATION_DIR/enhanced_status_aggregator.py" ]]; then
        cd "$COORDINATION_DIR"
        python3 enhanced_status_aggregator.py --once --agent-dir "../$AGENT_STATUS_DIR" --config-file "../runtime/agent_config.json"
    else
        # Fallback to individual status display
        # Get current agents from theme manager
        local agents=()
        if [[ -f "$THEME_MANAGER" ]]; then
            # Use portable method instead of mapfile
            while IFS= read -r line; do
                [[ -n "$line" ]] && agents+=("$line")
            done < <("$THEME_MANAGER" get-agents)
        fi
        
        # Fallback to default agents if none found
        if [[ ${#agents[@]} -eq 0 ]]; then
            agents=("alpha" "beta" "gamma" "delta" "epsilon" "zeta")
        fi
        
        for agent in "${agents[@]}"; do
            if [[ -f "$AGENT_STATUS_DIR/${agent}_status.json" ]]; then
                echo -e "${GREEN}Agent $agent: Active${NC}"
            else
                echo -e "${YELLOW}Agent $agent: Status file not found${NC}"
            fi
        done
    fi
}

# Function to show system status
show_system_status() {
    echo -e "${CYAN}=== System Status ===${NC}"
    echo ""
    
    # Get current agents from theme manager
    local agents=()
    if [[ -f "$THEME_MANAGER" ]]; then
        # Use portable method instead of mapfile
        while IFS= read -r line; do
            [[ -n "$line" ]] && agents+=("$line")
        done < <("$THEME_MANAGER" get-agents)
    fi
    
    # Fallback to default agents if none found
    if [[ ${#agents[@]} -eq 0 ]]; then
        agents=("alpha" "beta" "gamma" "delta" "epsilon" "zeta")
    fi
    local active_agents=0
    local total_agents=${#agents[@]}
    
    for agent in "${agents[@]}"; do
        if [[ -f "$AGENT_STATUS_DIR/${agent}_status.json" ]]; then
            ((active_agents++))
        fi
    done
    
    echo "Active Agent Files: $active_agents/$total_agents"
    
    # Check generated files
    if [[ -f "AGENT_COORDINATION_MASTER.json" ]]; then
        local master_age=$(( $(date +%s) - $(stat -f %m "AGENT_COORDINATION_MASTER.json") ))
        echo "Master Coordination JSON: $(($master_age / 60)) minutes old"
    else
        echo "Master Coordination JSON: Not found"
    fi
    
    if [[ -f "AGENT_COORDINATION_GENERATED.md" ]]; then
        local generated_age=$(( $(date +%s) - $(stat -f %m "AGENT_COORDINATION_GENERATED.md") ))
        echo "Generated Coordination MD: $(($generated_age / 60)) minutes old"
    else
        echo "Generated Coordination MD: Not found"
    fi
    
    # Check for running watchers
    local watcher_count=$(ps aux | grep "status_aggregator.py.*--watch" | grep -v grep | wc -l | tr -d ' ')
    echo "Active Watchers: $watcher_count"
    
    echo ""
}

# Function to migrate from old coordination file
migrate_from_old_system() {
    echo -e "${CYAN}Migrating from old coordination system...${NC}"
    
    if [[ ! -f "AGENT_COORDINATION.md" ]]; then
        echo -e "${RED}AGENT_COORDINATION.md not found${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Migration feature not yet implemented${NC}"
    echo "Please create individual agent status files manually using the JSON format"
    echo "Reference: AGENT_STATUS_ARCHITECTURE.md"
    
    return 1
}

# Function to create agent status template
create_agent_template() {
    local agent_id=$1
    
    if [[ -z "$agent_id" ]]; then
        echo -e "${RED}Agent ID required${NC}"
        return 1
    fi
    
    # Get current agents from theme manager
    local agents=()
    if [[ -f "$THEME_MANAGER" ]]; then
        # Use portable method instead of mapfile
        while IFS= read -r line; do
            [[ -n "$line" ]] && agents+=("$line")
        done < <("$THEME_MANAGER" get-agents)
    fi
    
    # Fallback to default agents if none found
    if [[ ${#agents[@]} -eq 0 ]]; then
        agents=("alpha" "beta" "gamma" "delta" "epsilon" "zeta")
    fi
    
    if [[ ! " ${agents[@]} " =~ " ${agent_id} " ]]; then
        echo -e "${RED}Invalid agent ID: $agent_id${NC}"
        echo "Valid agents: ${agents[*]}"
        return 1
    fi
    
    local status_file="$AGENT_STATUS_DIR/${agent_id}_status.json"
    
    if [[ -f "$status_file" ]]; then
        echo -e "${YELLOW}Status file already exists: $status_file${NC}"
        return 1
    fi
    
    # Get agent info from theme manager if available
    local agent_name agent_role agent_color agent_index
    
    if [[ -f "$THEME_MANAGER" ]]; then
        # Find agent index
        agent_index=-1
        for i in "${!agents[@]}"; do
            if [[ "${agents[$i]}" == "$agent_id" ]]; then
                agent_index=$i
                break
            fi
        done
        
        if [[ $agent_index -eq -1 ]]; then
            echo -e "${RED}Agent not found in current theme${NC}"
            return 1
        fi
        
        # Get display name
        agent_name=$(echo "$agent_id" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
        
        # Assign role based on index (cycling through standard roles)
        case $((agent_index % 6)) in
            0) agent_role="Critical Path Lead"; agent_color="🔴" ;;
            1) agent_role="Migration Specialist"; agent_color="🔵" ;;
            2) agent_role="Dashboard Developer"; agent_color="🟢" ;;
            3) agent_role="DevOps Engineer"; agent_color="🟡" ;;
            4) agent_role="Security Engineer"; agent_color="🟠" ;;
            5) agent_role="UX Engineer"; agent_color="🟣" ;;
        esac
    else
        # Fallback to hardcoded mapping
        case "$agent_id" in
            "alpha")
                agent_name="Alpha"
                agent_role="Critical Path Lead"
                agent_color="🔴"
                ;;
            "beta")
                agent_name="Beta"
                agent_role="Migration Specialist"
                agent_color="🔵"
                ;;
            "gamma")
                agent_name="Gamma"
                agent_role="Dashboard Developer"
                agent_color="🟢"
                ;;
            "delta")
                agent_name="Delta"
                agent_role="DevOps Engineer"
                agent_color="🟡"
                ;;
            "epsilon")
                agent_name="Epsilon"
                agent_role="Security Engineer"
                agent_color="🟠"
                ;;
            "zeta")
                agent_name="Zeta"
                agent_role="UX Engineer"
                agent_color="🟣"
                ;;
        esac
    fi
    
    # Create template
    cat > "$status_file" << EOF
{
  "agent_info": {
    "name": "$agent_name",
    "role": "$agent_role",
    "color": "$agent_color",
    "id": "$agent_id"
  },
  "current_status": {
    "task": "Initial setup and task assignment",
    "status": "🔵",
    "status_text": "Starting",
    "progress": 0,
    "progress_description": "Just started",
    "eta": "TBD",
    "last_update": "$(date -u +"%Y-%m-%d %H:%M UTC")"
  },
  "activities": {
    "completed": [],
    "in_progress": [
      "Reading agent instructions",
      "Setting up development environment"
    ],
    "pending": []
  },
  "blockers": {
    "current": [],
    "resolved": []
  },
  "decisions": [],
  "next_steps": [
    "Review agent-specific instructions",
    "Begin first assigned task"
  ],
  "communication": {
    "notes": [
      "Agent initialized and ready for task assignment"
    ],
    "requests": [],
    "offers": []
  },
  "dependencies": {
    "blocking": [],
    "blocked_by": [],
    "completed_dependencies": []
  },
  "metrics": {
    "tasks_completed": 0,
    "tasks_total": 0,
    "completion_percentage": 0,
    "days_ahead_of_schedule": 0
  },
  "deliverables": []
}
EOF
    
    echo -e "${GREEN}Created template status file: $status_file${NC}"
    log "Created template for agent $agent_id"
    return 0
}

# Function to show help
show_help() {
    show_header
    echo -e "${CYAN}=== Distributed Agent Coordination System ===${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo -e "${YELLOW}System Management:${NC}"
    echo "  init                    - Initialize the coordination system"
    echo "  status                  - Show system status"
    echo "  aggregate               - Aggregate agent statuses once"
    echo "  watch [mode]            - Start real-time watcher (default: enhanced)"
    echo "                            enhanced = real-time display with change queue"
    echo "                            basic = simple interval-based watching"
    echo "  migrate                 - Migrate from old coordination system"
    echo ""
    echo -e "${YELLOW}Agent Management:${NC}"
    echo "  show <agent>            - Show agent status"
    echo "  show-all                - Show all agent statuses"
    echo "  create <agent>          - Create agent status template"
    echo "  update <agent> [opts]   - Update agent status"
    echo ""
    echo -e "${YELLOW}Update Options:${NC}"
    echo "  --task <task>           - Update current task"
    echo "  --status <status>       - Update status (🟢🟡🔴🔵)"
    echo "  --progress <0-100>      - Update progress percentage"
    echo "  --add-activity <text>   - Add activity"
    echo "  --add-blocker <text>    - Add blocker"
    echo "  --resolve-blocker <text> - Resolve blocker"
    echo "  --add-decision <text>   - Add decision"
    echo "  --add-note <text>       - Add communication note"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 init                                    - Initialize system"
    echo "  $0 watch                                   - Start enhanced real-time monitoring"
    echo "  $0 watch basic                             - Use basic interval monitoring"
    echo "  $0 show alpha                              - Show Agent Alpha status"
    echo "  $0 update alpha --task \"New Task\" --progress 50  - Update task and progress"
    echo "  $0 create beta                             - Create Agent Beta template"
    echo ""
    echo -e "${YELLOW}Agent IDs:${NC}"
    echo "  alpha, beta, gamma, delta, epsilon, zeta"
    echo ""
    echo -e "${YELLOW}Files:${NC}"
    echo "  $AGENT_STATUS_DIR/                        - Individual agent status files"
    echo "  $COORDINATION_DIR/                        - Coordination system scripts"
    echo "  AGENT_COORDINATION_MASTER.json            - Master coordination data"
    echo "  AGENT_COORDINATION_GENERATED.md           - Generated coordination markdown"
}

# Main function
main() {
    local command=${1:-help}
    
    case "$command" in
        "init")
            initialize_system
            ;;
        "status")
            show_system_status
            ;;
        "aggregate")
            if check_requirements; then
                aggregate_statuses
            fi
            ;;
        "watch")
            if check_requirements; then
                start_watcher "$2"
            fi
            ;;
        "show")
            if check_requirements; then
                if [[ "$2" == "all" ]] || [[ "$2" == "-a" ]]; then
                    show_all_statuses
                else
                    show_agent_status "$2"
                fi
            fi
            ;;
        "show-all")
            if check_requirements; then
                show_all_statuses
            fi
            ;;
        "create")
            create_agent_template "$2"
            ;;
        "update")
            if check_requirements; then
                update_agent_status "${@:2}"
            fi
            ;;
        "migrate")
            migrate_from_old_system
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            show_help
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${GREEN}Goodbye!${NC}"; exit 0' INT

# Run main function
main "$@"