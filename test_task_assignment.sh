#!/bin/bash
# Test the complete task assignment system

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Complete Task Assignment System${NC}"
echo "=================================================="

# Set to simulator mode
export AGENT_MODE=simulator

# Clean up any existing processes
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "test_agent_simulator.py" 2>/dev/null || true
pkill -f "enhanced_lifecycle_manager.py" 2>/dev/null || true

# Reset agent status files
echo -e "${YELLOW}Resetting agent status files...${NC}"
python3 init_agent_status.py --force >/dev/null 2>&1

# Remove existing task files to start fresh
echo -e "${YELLOW}Cleaning up existing task files...${NC}"
rm -f coordination_system/task_queue.json
rm -f coordination_system/task_assignments.json
rm -f coordination_system/assignment_history.json

# Create sample tasks
echo -e "${YELLOW}Creating sample tasks...${NC}"
python3 coordination_system/task_communicator.py --create-samples

# Show initial status
echo ""
echo -e "${CYAN}Initial Task Status:${NC}"
python3 coordination_system/task_assignment_manager.py --status

echo ""
echo -e "${CYAN}Initial Agent Workloads:${NC}"
python3 coordination_system/task_assignment_manager.py --workloads

# Process task assignments
echo ""
echo -e "${YELLOW}Processing task assignments...${NC}"
python3 coordination_system/task_communicator.py --process

# Show updated status
echo ""
echo -e "${CYAN}After Assignment Task Status:${NC}"
python3 coordination_system/task_assignment_manager.py --status

echo ""
echo -e "${CYAN}After Assignment Agent Workloads:${NC}"
python3 coordination_system/task_assignment_manager.py --workloads

# Check if any tasks were assigned to agents
echo ""
echo -e "${CYAN}Checking agent inboxes for task assignments...${NC}"

for agent in shark dolphin whale octopus jellyfish seahorse; do
    inbox_file="agent_communication/$agent/input/inbox.json"
    if [ -f "$inbox_file" ]; then
        message_count=$(jq '.messages | length' "$inbox_file" 2>/dev/null || echo "0")
        if [ "$message_count" -gt 0 ]; then
            echo -e "${GREEN}  ✓ $agent has $message_count message(s)${NC}"
            # Show the first message
            jq -r '.messages[0].payload.title // "No title"' "$inbox_file" 2>/dev/null | head -1 | sed 's/^/    Task: /'
        else
            echo -e "${YELLOW}  - $agent has no messages${NC}"
        fi
    else
        echo -e "${RED}  ✗ $agent inbox not found${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ Task Assignment System Test Complete!${NC}"
echo ""
echo -e "${CYAN}Next steps to test end-to-end:${NC}"
echo "1. Start the enhanced lifecycle manager:"
echo "   python3 coordination_system/enhanced_lifecycle_manager.py"
echo ""
echo "2. Agents should automatically start and begin working on assigned tasks"
echo "3. Monitor progress with the coordination dashboard:"
echo "   ./coordination_manager.sh watch"