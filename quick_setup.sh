#\!/bin/bash
# Quick Setup Script for Multi-Agent Coordination System

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Multi-Agent Coordination System - Quick Setup ===${NC}"
echo ""

# Function to prompt for input
prompt() {
    local question=$1
    local default=$2
    local var_name=$3
    
    if [[ -n "$default" ]]; then
        read -p "$question [$default]: " value
        value=${value:-$default}
    else
        read -p "$question: " value
    fi
    
    eval "$var_name='$value'"
}

echo -e "${YELLOW}Welcome\! Let's set up your multi-agent coordination system.${NC}"
echo ""

# Get project information
prompt "What's your project name?" "My Project" PROJECT_NAME
prompt "Where is your project code located?" "$(pwd)" PROJECT_PATH
prompt "How many agents would you like to start with?" "4" AGENT_COUNT
prompt "Which theme would you prefer? (ocean_creatures/marvel/greek_letters)" "ocean_creatures" THEME

echo ""
echo -e "${BLUE}Setting up your project...${NC}"

# Initialize coordination system
echo "1. Initializing coordination system..."
./coordination_manager.sh init > /dev/null 2>&1

# Set theme and agent count
echo "2. Configuring theme and agents..."
./manage_agents.sh set-theme "$THEME" > /dev/null
./manage_agents.sh set-count "$AGENT_COUNT" > /dev/null

# Generate agent files
echo "3. Generating agent files..."
./generate_agents.sh > /dev/null

# Create project
echo "4. Creating project..."
./project_manager.sh create "$PROJECT_NAME" "$PROJECT_PATH" \
    --description "Created by quick setup" \
    --agents "$AGENT_COUNT" > /dev/null 2>&1 || echo "   Note: Project manager may need manual setup"

echo ""
echo -e "${GREEN}✓ Setup complete\!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Start the coordination system:"
echo "   ${GREEN}./manage_agents.sh auto${NC}"
echo ""
echo "2. Monitor agent activity:"
echo "   ${GREEN}./coordination_manager.sh watch${NC}"
echo ""
echo "3. View available agents:"
echo "   ${GREEN}./manage_agents.sh list${NC}"
echo ""
echo "4. Read the full getting started guide:"
echo "   ${GREEN}cat GETTING_STARTED.md${NC}"
echo ""
echo -e "${YELLOW}Happy coordinating\!${NC}"
EOF < /dev/null