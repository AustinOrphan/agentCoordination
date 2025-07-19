#!/bin/bash
# Dynamic Agent Management Script

# Configuration
THEME_MANAGER="./agent_theme_manager.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get current agents
get_agents() {
    if [[ -f "$THEME_MANAGER" ]]; then
        mapfile -t AGENTS < <("$THEME_MANAGER" get-agents)
    else
        # Fallback to default agents
        AGENTS=("alpha" "beta" "gamma" "delta" "epsilon" "zeta")
    fi
}

# Get agent display name
get_agent_display_name() {
    local agent=$1
    echo "$agent" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1'
}

# Get agent role based on index
get_agent_role() {
    local index=$1
    case $((index % 6)) in
        0) echo "Critical Path Lead" ;;
        1) echo "Migration Specialist" ;;
        2) echo "Dashboard Developer" ;;
        3) echo "DevOps Engineer" ;;
        4) echo "Security Engineer" ;;
        5) echo "UX Engineer" ;;
    esac
}

show_help() {
    get_agents
    local theme=$("$THEME_MANAGER" show 2>/dev/null | grep "Theme:" | sed 's/.*: \(.*\) (.*/\1/' || echo "Default")
    
    echo "🤖 Agent Management System"
    echo -e "${CYAN}Current Theme: $theme${NC}"
    echo -e "${CYAN}Active Agents: ${#AGENTS[@]}${NC}"
    echo ""
    echo "Usage: $0 [command] [agent|option]"
    echo ""
    echo "Commands:"
    echo "  start <agent>    - Start a specific agent"
    echo "  auto             - Start lifecycle daemon for automatic agent management"
    echo "  status           - Show current agent status"
    echo "  list             - List all available agents"
    echo "  lifecycle        - Manage the lifecycle daemon"
    echo "  help             - Show this help message"
    echo ""
    echo "Theme Management:"
    echo "  themes           - List available themes"
    echo "  set-theme <name> - Change agent theme"
    echo "  set-count <n>    - Set number of agents"
    echo ""
    echo "Available Agents:"
    for i in "${!AGENTS[@]}"; do
        local agent="${AGENTS[$i]}"
        local display_name=$(get_agent_display_name "$agent")
        local role=$(get_agent_role $i)
        echo "  $agent - $display_name ($role)"
    done
    echo ""
    echo "Examples:"
    echo "  $0 start ${AGENTS[0]}    - Start first agent"
    echo "  $0 auto               - Start all agents"
    echo "  $0 set-theme marvel   - Switch to Marvel theme"
    echo "  $0 set-count 10       - Use 10 agents"
}

start_agent() {
    local agent=$1
    get_agents
    
    # Check if agent exists
    if [[ ! " ${AGENTS[@]} " =~ " ${agent} " ]]; then
        echo -e "${RED}❌ Unknown agent: $agent${NC}"
        echo "Available agents: ${AGENTS[*]}"
        return 1
    fi
    
    # Get agent info
    local display_name=$(get_agent_display_name "$agent")
    local agent_index=-1
    for i in "${!AGENTS[@]}"; do
        if [[ "${AGENTS[$i]}" == "$agent" ]]; then
            agent_index=$i
            break
        fi
    done
    local role=$(get_agent_role $agent_index)
    
    echo -e "🚀 Starting Agent ${GREEN}$display_name${NC} ($role)"
    
    # Check if startup script exists
    if [[ -f "./start_agent_${agent}.sh" ]]; then
        echo "Opening new Claude Code session..."
        ./start_agent_${agent}.sh
    else
        echo -e "${RED}❌ Startup script not found: start_agent_${agent}.sh${NC}"
        echo "Run './generate_agents.sh' to create agent files"
        return 1
    fi
}

auto_start_agents() {
    get_agents
    echo "🚀 Auto-Mode: Intelligent Agent Lifecycle Management"
    echo -e "${CYAN}Theme: $("$THEME_MANAGER" show 2>/dev/null | grep "Theme:" | sed 's/.*: \(.*\) (.*/\1/' || echo "Default")${NC}"
    echo -e "${CYAN}Agent Count: ${#AGENTS[@]}${NC}"
    echo ""
    
    # Check if lifecycle daemon is running
    if [[ -f "lifecycle_daemon.sh" ]]; then
        if ./lifecycle_daemon.sh status | grep -q "is running"; then
            echo -e "${YELLOW}⚠️  Lifecycle daemon is already running${NC}"
            echo "Agents are being managed automatically based on blockers and dependencies"
            echo ""
            ./lifecycle_daemon.sh status
        else
            echo -e "${CYAN}Starting Lifecycle Daemon for automatic agent management...${NC}"
            echo ""
            echo "The daemon will:"
            echo "  ✓ Start agents when dependencies are met and no blockers exist"
            echo "  ✓ Stop agents when they become blocked"
            echo "  ✓ Route messages between agents"
            echo "  ✓ Monitor agent health through heartbeats"
            echo ""
            
            if ./lifecycle_daemon.sh start; then
                echo ""
                echo -e "${GREEN}✅ Lifecycle management activated!${NC}"
                echo ""
                echo "Agents will be automatically started as their dependencies are met."
                echo "First agent(s) with no dependencies will start in ~10 seconds."
                echo ""
                echo "Monitor with:"
                echo "  ./lifecycle_daemon.sh status   - Check daemon and agent status"
                echo "  ./lifecycle_daemon.sh logs     - View detailed logs"
                echo "  tail -f lifecycle_daemon.log   - Follow live activity"
            else
                echo -e "${RED}❌ Failed to start lifecycle daemon${NC}"
                echo "Falling back to manual mode - start agents individually"
            fi
        fi
    else
        echo -e "${RED}❌ Lifecycle daemon not found${NC}"
        echo "Falling back to sequential start mode..."
        echo ""
        
        # Fallback: start all agents sequentially
        for i in "${!AGENTS[@]}"; do
            local agent="${AGENTS[$i]}"
            local display_name=$(get_agent_display_name "$agent")
            local role=$(get_agent_role $i)
            
            echo -e "Starting Agent ${GREEN}$display_name${NC} ($role)..."
            
            # Add delay between launches
            if [[ $i -gt 0 ]]; then
                echo "Waiting 3 seconds before next agent..."
                sleep 3
            fi
            
            start_agent "$agent"
        done
        
        echo ""
        echo -e "${GREEN}✅ All agents launched!${NC}"
        echo "Use '$0 status' to monitor progress"
    fi
}

show_status() {
    get_agents
    echo "📊 Current Agent Status:"
    echo -e "${CYAN}Theme: $("$THEME_MANAGER" show 2>/dev/null | grep "Theme:" | sed 's/.*: \(.*\) (.*/\1/' || echo "Default")${NC}"
    echo -e "${CYAN}Active Agents: ${#AGENTS[@]}${NC}"
    echo ""
    
    if [ -f "AGENT_COORDINATION.md" ]; then
        echo "Reading from AGENT_COORDINATION.md..."
        # Show agent sections from coordination file
        grep -A 5 "Agent.*(" AGENT_COORDINATION.md 2>/dev/null || echo "No status found in coordination file"
    else
        echo "⚠️  AGENT_COORDINATION.md not found"
    fi
    
    # Show status files
    echo ""
    echo "Agent Status Files:"
    for agent in "${AGENTS[@]}"; do
        if [[ -f "agent_status/${agent}_status.json" ]]; then
            echo -e "  ${GREEN}✓${NC} ${agent}_status.json"
        else
            echo -e "  ${RED}✗${NC} ${agent}_status.json"
        fi
    done
}

list_agents() {
    get_agents
    echo "🤖 Available Agents:"
    echo -e "${CYAN}Theme: $("$THEME_MANAGER" show 2>/dev/null | grep "Theme:" | sed 's/.*: \(.*\) (.*/\1/' || echo "Default")${NC}"
    echo ""
    
    for i in "${!AGENTS[@]}"; do
        local agent="${AGENTS[$i]}"
        local display_name=$(get_agent_display_name "$agent")
        local role=$(get_agent_role $i)
        
        echo -e "${GREEN}Agent $display_name${NC} ($agent):"
        echo "  Role: $role"
        echo "  Index: $i"
        
        # Check if files exist
        if [[ -f "./start_agent_${agent}.sh" ]]; then
            echo "  Startup Script: ✓"
        else
            echo "  Startup Script: ✗ (run ./generate_agents.sh)"
        fi
        
        if [[ -f "./AGENT_${agent^^}_PROMPT.md" ]]; then
            echo "  Prompt File: ✓"
        else
            echo "  Prompt File: ✗"
        fi
        echo ""
    done
}

list_themes() {
    echo "🎨 Available Themes:"
    echo ""
    
    if [[ -f "$THEME_MANAGER" ]]; then
        "$THEME_MANAGER" list-themes
    else
        echo -e "${RED}Theme manager not found${NC}"
    fi
}

set_theme() {
    local theme=$1
    if [[ -z "$theme" ]]; then
        echo -e "${RED}❌ Please specify a theme${NC}"
        list_themes
        return 1
    fi
    
    echo "🎨 Setting theme to: $theme"
    
    if [[ -f "$THEME_MANAGER" ]]; then
        if "$THEME_MANAGER" set-theme "$theme"; then
            echo -e "${GREEN}✅ Theme changed successfully${NC}"
            echo ""
            echo -e "${YELLOW}⚠️  Important: Run './generate_agents.sh' to create new agent files${NC}"
        else
            echo -e "${RED}❌ Failed to set theme${NC}"
            return 1
        fi
    else
        echo -e "${RED}Theme manager not found${NC}"
        return 1
    fi
}

set_count() {
    local count=$1
    if [[ -z "$count" ]]; then
        echo -e "${RED}❌ Please specify agent count${NC}"
        return 1
    fi
    
    echo "🔢 Setting agent count to: $count"
    
    if [[ -f "$THEME_MANAGER" ]]; then
        if "$THEME_MANAGER" set-count "$count"; then
            echo -e "${GREEN}✅ Agent count changed successfully${NC}"
            echo ""
            echo -e "${YELLOW}⚠️  Important: Run './generate_agents.sh' to create new agent files${NC}"
        else
            echo -e "${RED}❌ Failed to set agent count${NC}"
            return 1
        fi
    else
        echo -e "${RED}Theme manager not found${NC}"
        return 1
    fi
}

# Function to manage lifecycle daemon
manage_lifecycle() {
    local subcommand=${1:-status}
    
    if [[ ! -f "lifecycle_daemon.sh" ]]; then
        echo -e "${RED}❌ Lifecycle daemon script not found${NC}"
        return 1
    fi
    
    case $subcommand in
        start|stop|restart|status|logs)
            ./lifecycle_daemon.sh "$subcommand"
            ;;
        *)
            echo -e "${RED}❌ Unknown lifecycle command: $subcommand${NC}"
            echo "Valid commands: start, stop, restart, status, logs"
            return 1
            ;;
    esac
}

# Main script logic
case $1 in
    "start")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please specify an agent to start${NC}"
            echo "Usage: $0 start <agent>"
            get_agents
            echo "Available agents: ${AGENTS[*]}"
            exit 1
        fi
        start_agent $2
        ;;
    "auto")
        auto_start_agents
        ;;
    "status")
        show_status
        ;;
    "list")
        list_agents
        ;;
    "lifecycle")
        manage_lifecycle "$2"
        ;;
    "themes")
        list_themes
        ;;
    "set-theme")
        set_theme "$2"
        ;;
    "set-count")
        set_count "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        if [[ -n "$1" ]]; then
            echo -e "${RED}❌ Unknown command: $1${NC}"
        fi
        show_help
        exit 1
        ;;
esac