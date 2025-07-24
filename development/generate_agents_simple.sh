#!/bin/bash
# Simple Agent Generator Script - Creates agent files that work with lifecycle daemon

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_MANAGER="$SCRIPT_DIR/agent_theme_manager.py"

# Function to show header
show_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                              SIMPLE AGENT GENERATOR                                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to get current configuration
get_config() {
    local theme=$("$THEME_MANAGER" show | grep "Theme:" | sed 's/.*(\(.*\))/\1/')
    local count=$("$THEME_MANAGER" show | grep "Agent count:" | awk '{print $3}')
    echo "$theme $count"
}

# Function to create simple agent startup script
create_startup_script() {
    local agent_name=$1
    local agent_index=$2
    local display_name=$(echo "$agent_name" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    
    # Determine agent role
    local agent_role=""
    case $((agent_index % 6)) in
        0) agent_role="Critical Path Lead" ;;
        1) agent_role="Migration Specialist" ;;
        2) agent_role="Dashboard Developer" ;;
        3) agent_role="DevOps Engineer" ;;
        4) agent_role="Security Engineer" ;;
        5) agent_role="UX Engineer" ;;
    esac
    
    cat > "start_agent_${agent_name}.sh" << EOF
#!/bin/bash
# Agent $display_name Startup Script (Simple)

# Agent configuration
AGENT_NAME="$agent_name"
AGENT_UPPER="$(echo "$agent_name" | tr '[:lower:]' '[:upper:]')"
AGENT_ROLE="$agent_role"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get directories
REPO_ROOT="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

echo -e "\${BLUE}🚀 Starting Agent \$AGENT_UPPER (\$AGENT_ROLE)\${NC}"

# Initialize agent
echo -e "\${YELLOW}Initializing agent...\${NC}"
python3 "\$REPO_ROOT/coordination_system/initialize_agent.py" "\$AGENT_NAME"

# Run the agent using agent_runner.sh
exec "\$REPO_ROOT/agent_runner.sh" "\$AGENT_NAME"
EOF
    
    chmod +x "start_agent_${agent_name}.sh"
    
    echo -e "${GREEN}✓ Created start_agent_${agent_name}.sh (simple version)${NC}"
}

# Main function
main() {
    show_header
    
    # Get current configuration
    read theme count <<< $(get_config)
    echo -e "${CYAN}Current Theme: $theme${NC}"
    echo -e "${CYAN}Agent Count: $count${NC}"
    echo ""
    
    # Get agent names (compatible with older bash)
    agents=()
    while IFS= read -r line; do
        agents+=("$line")
    done < <("$THEME_MANAGER" get-agents)
    
    if [ ${#agents[@]} -eq 0 ]; then
        echo -e "${RED}Error: No agents found for current configuration${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Generating simple startup scripts for agents:${NC}"
    for agent in "${agents[@]}"; do
        echo "  - $agent"
    done
    echo ""
    
    # Generate files for each agent
    for i in "${!agents[@]}"; do
        agent="${agents[$i]}"
        echo -e "${BLUE}Processing Agent $agent (index $i)...${NC}"
        
        create_startup_script "$agent" "$i"
        
        echo ""
    done
    
    echo ""
    echo -e "${GREEN}✅ Simple agent generation complete!${NC}"
    echo ""
    echo -e "${CYAN}These scripts work with the lifecycle daemon.${NC}"
    echo -e "${CYAN}They use agent_runner.sh which defaults to simulator mode.${NC}"
    echo ""
    echo -e "${YELLOW}To use real Claude Code instead of simulator:${NC}"
    echo "  export AGENT_MODE=claude"
    echo ""
    echo -e "${YELLOW}To test with simulator:${NC}"
    echo "  ./manage_agents.sh auto  # or"
    echo "  ./start_agent_shark.sh   # for individual agents"
}

# Run main function
main "$@"