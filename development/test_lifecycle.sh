#!/bin/bash
# Test the lifecycle daemon with simulated agents

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Lifecycle Daemon with Simulated Agents${NC}"
echo "----------------------------------------"

# Set to simulator mode
export AGENT_MODE=simulator

# Clean up any existing agent processes
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "test_agent_simulator.py" 2>/dev/null || true
pkill -f "agent_lifecycle_manager.py" 2>/dev/null || true

# Reset all agent statuses
echo -e "${YELLOW}Resetting agent statuses...${NC}"
python3 init_agent_status.py --force >/dev/null 2>&1

# Assign initial tasks
echo -e "${YELLOW}Assigning initial tasks...${NC}"
python3 coordination_system/update_agent_status.py shark --task "Implement authentication module" --progress 0
python3 coordination_system/update_agent_status.py dolphin --task "Create database schema" --progress 0
python3 coordination_system/update_agent_status.py whale --task "Design API endpoints" --progress 0

# Add a dependency - dolphin depends on shark completing authentication
echo -e "${YELLOW}Setting up dependencies...${NC}"
python3 -c "
import json
with open('agent_status/dolphin_status.json', 'r') as f:
    status = json.load(f)
status['dependencies'] = {'blocking': [], 'blocked_by': ['shark:authentication'], 'completed_dependencies': []}
with open('agent_status/dolphin_status.json', 'w') as f:
    json.dump(status, f, indent=2)
"

# Add a blocker to whale
echo -e "${YELLOW}Adding blocker to whale...${NC}"
python3 coordination_system/update_agent_status.py whale --add-blocker "Waiting for API specifications from product team"

echo ""
echo -e "${GREEN}✅ Test setup complete!${NC}"
echo ""
echo -e "${CYAN}Current state:${NC}"
echo "- Shark: Has task, no blockers → Should start"
echo "- Dolphin: Has task, depends on shark → Should wait"
echo "- Whale: Has task, but blocked → Should not start"
echo "- Others: No tasks → Should not start"
echo ""
echo -e "${CYAN}Starting lifecycle daemon...${NC}"
echo "Press Ctrl+C to stop"
echo ""

# Start the lifecycle daemon
python3 coordination_system/agent_lifecycle_manager.py