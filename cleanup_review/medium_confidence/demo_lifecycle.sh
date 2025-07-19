#!/bin/bash
# Demo script to showcase the automatic lifecycle management

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     Agent Coordination - Automatic Lifecycle Management Demo     ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Show current configuration
echo -e "${CYAN}Step 1: Current Configuration${NC}"
./agent_theme_manager.py show
echo ""

# Step 2: Generate agent files if needed
echo -e "${CYAN}Step 2: Ensuring agent files are generated${NC}"
if [[ ! -f "start_agent_alpha.sh" ]] && [[ ! -f "start_agent_$(./agent_theme_manager.py get-agents | head -1).sh" ]]; then
    echo "Generating agent files..."
    ./generate_agents.sh
else
    echo "Agent files already exist"
fi
echo ""

# Step 3: Initialize coordination system
echo -e "${CYAN}Step 3: Initialize coordination system${NC}"
./coordination_manager.sh init
echo ""

# Step 4: Create initial agent status with dependencies
echo -e "${CYAN}Step 4: Setting up agent dependencies for demo${NC}"
FIRST_AGENT=$(./agent_theme_manager.py get-agents | head -1)
SECOND_AGENT=$(./agent_theme_manager.py get-agents | head -2 | tail -1)
THIRD_AGENT=$(./agent_theme_manager.py get-agents | head -3 | tail -1)

echo "Creating demo scenario:"
echo "- $FIRST_AGENT: No dependencies (will start immediately)"
echo "- $SECOND_AGENT: Depends on $FIRST_AGENT"
echo "- $THIRD_AGENT: Initially blocked"

# Update second agent to depend on first
python3 -c "
import json
from pathlib import Path

# Update second agent status
status_file = Path('agent_status/${SECOND_AGENT}_status.json')
if status_file.exists():
    with open(status_file) as f:
        status = json.load(f)
    
    status['dependencies'] = ['${FIRST_AGENT}']
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print('✓ Set $SECOND_AGENT to depend on $FIRST_AGENT')

# Add blocker to third agent
status_file = Path('agent_status/${THIRD_AGENT}_status.json')
if status_file.exists():
    with open(status_file) as f:
        status = json.load(f)
    
    status['blockers'] = ['Demo blocker: Waiting for external resource']
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print('✓ Added blocker to $THIRD_AGENT')
"
echo ""

# Step 5: Start lifecycle daemon
echo -e "${CYAN}Step 5: Starting automatic lifecycle management${NC}"
echo "The daemon will:"
echo "  • Start $FIRST_AGENT immediately (no dependencies)"
echo "  • Start $SECOND_AGENT after $FIRST_AGENT is running"
echo "  • Keep $THIRD_AGENT stopped (blocked)"
echo ""

./lifecycle_daemon.sh start
echo ""

# Step 6: Monitor for a bit
echo -e "${CYAN}Step 6: Monitoring agent lifecycle (20 seconds)${NC}"
echo "Watch as agents start automatically..."
echo ""

for i in {1..4}; do
    sleep 5
    echo -e "${YELLOW}[$((i*5))s] Checking status...${NC}"
    ./lifecycle_daemon.sh status | grep -E "(is running|Agent Communication)"
    echo ""
done

# Step 7: Remove blocker
echo -e "${CYAN}Step 7: Removing blocker from $THIRD_AGENT${NC}"
python3 -c "
import json
from pathlib import Path

status_file = Path('agent_status/${THIRD_AGENT}_status.json')
if status_file.exists():
    with open(status_file) as f:
        status = json.load(f)
    
    status['blockers'] = []
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print('✓ Removed blocker from $THIRD_AGENT')
"
echo "Waiting for lifecycle daemon to detect change and start $THIRD_AGENT..."
echo ""

sleep 15

# Step 8: Final status
echo -e "${CYAN}Step 8: Final Status${NC}"
./lifecycle_daemon.sh status
echo ""

# Step 9: Cleanup option
echo -e "${CYAN}Step 9: Demo Complete${NC}"
echo ""
echo "To stop the lifecycle daemon and all agents:"
echo "  ./lifecycle_daemon.sh stop"
echo ""
echo "To see detailed logs:"
echo "  ./lifecycle_daemon.sh logs"
echo ""
echo -e "${GREEN}✓ Demo complete! The system is now managing agents automatically.${NC}"