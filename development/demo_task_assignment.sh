#!/bin/bash
# Demo script to showcase the enhanced task assignment system

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🚀 Task Assignment System Demo${NC}"
echo "====================================="
echo ""

# Step 1: Create sample tasks
echo -e "${CYAN}Step 1: Creating sample tasks...${NC}"
python3 coordination_system/task_communicator.py --create-samples
echo ""

# Step 2: Show task queue status
echo -e "${CYAN}Step 2: Task Queue Status${NC}"
python3 coordination_system/task_assignment_manager.py --status
echo ""

# Step 3: Show agent workloads (before assignment)
echo -e "${CYAN}Step 3: Agent Workloads (Before Assignment)${NC}"
python3 coordination_system/task_assignment_manager.py --workloads
echo ""

# Step 4: Process task assignments
echo -e "${CYAN}Step 4: Processing task assignments...${NC}"
python3 coordination_system/task_communicator.py --process
echo ""

# Step 5: Show updated status
echo -e "${CYAN}Step 5: Task Queue Status (After Assignment)${NC}"
python3 coordination_system/task_assignment_manager.py --status
echo ""

# Step 6: Show agent workloads (after assignment)
echo -e "${CYAN}Step 6: Agent Workloads (After Assignment)${NC}"
python3 coordination_system/task_assignment_manager.py --workloads
echo ""

echo -e "${GREEN}✅ Demo complete!${NC}"
echo ""
echo -e "${YELLOW}To start agents with automatic task processing:${NC}"
echo "  ./manage_agents.sh auto"
echo ""
echo -e "${YELLOW}Or start the lifecycle daemon directly:${NC}"
echo "  ./lifecycle_daemon.sh start"