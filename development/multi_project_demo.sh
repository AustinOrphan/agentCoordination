#!/bin/bash
# Multi-Project Coordination System Demo
# This script demonstrates setting up and running multiple projects simultaneously

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Multi-Project Coordination System Demo${NC}"
echo ""

# Check if we have sample projects
if [ ! -d "../sample-projects" ]; then
    echo -e "${YELLOW}Creating sample project directories...${NC}"
    mkdir -p ../sample-projects/{web-app,mobile-app,backend-api}
    
    # Create minimal project files
    echo '{"name": "web-app", "version": "1.0.0"}' > ../sample-projects/web-app/package.json
    echo '{"name": "mobile-app", "version": "1.0.0"}' > ../sample-projects/mobile-app/package.json
    echo 'from flask import Flask' > ../sample-projects/backend-api/app.py
fi

# Step 1: Create multiple projects
echo -e "${BLUE}Step 1: Creating three projects${NC}"
echo ""

# Clean up any existing projects first
echo -e "${YELLOW}Cleaning up any existing projects...${NC}"
rm -rf projects/* 2>/dev/null
rm -f coordination_system/project_registry.json 2>/dev/null
rm -f coordination_system/global_pool_config.json 2>/dev/null
rm -f coordination_system/global_assignments.json 2>/dev/null

# Project 1: High-priority Web Application
echo -e "${GREEN}Creating Project 1: Web Application (High Priority)${NC}"
./project_manager.sh create "Web App" ../sample-projects/web-app \
    -d "E-commerce platform with urgent deadline" \
    -a 8 \
    -t ocean_creatures

# Get project ID - take the first one if multiple exist
WEB_PROJECT_ID=$(./project_manager.sh list | grep "Web App" | head -1 | awk '{print $1}')

# Project 2: Medium-priority Mobile App
echo ""
echo -e "${GREEN}Creating Project 2: Mobile App (Medium Priority)${NC}"
./project_manager.sh create "Mobile App" ../sample-projects/mobile-app \
    -d "Companion mobile application" \
    -a 6 \
    -t greek_letters

# Get project ID - take the first one if multiple exist  
MOBILE_PROJECT_ID=$(./project_manager.sh list | grep "Mobile App" | head -1 | awk '{print $1}')

# Project 3: Low-priority Backend API
echo ""
echo -e "${GREEN}Creating Project 3: Backend API (Low Priority)${NC}"
./project_manager.sh create "Backend API" ../sample-projects/backend-api \
    -d "Microservices backend" \
    -a 4 \
    -t marvel

# Get project ID - take the first one if multiple exist
API_PROJECT_ID=$(./project_manager.sh list | grep "Backend API" | head -1 | awk '{print $1}')

# Step 2: Mark all projects as active (without starting lifecycle managers)
echo ""
echo -e "${BLUE}Step 2: Activating All Projects${NC}"
# Just mark projects as active without starting the lifecycle managers
python3 -c "
from coordination_system.project_manager import ProjectManager, ProjectStatus
pm = ProjectManager()
for pid in ['$WEB_PROJECT_ID', '$MOBILE_PROJECT_ID', '$API_PROJECT_ID']:
    project = pm.get_project(pid)
    if project:
        project.status = ProjectStatus.ACTIVE
        pm._save_project(project)
        print(f'Activated project: {project.name}')
"

# Step 3: Set up global priority mode
echo ""
echo -e "${BLUE}Step 3: Configuring Global Priority Pool Mode${NC}"
./project_manager.sh pool mode global_priority

# Step 4: Set project priorities
echo ""
echo -e "${BLUE}Step 4: Setting Project Priority Multipliers${NC}"
echo -e "${YELLOW}Web App: 1.8 (High priority - urgent deadline)${NC}"
./project_manager.sh pool priority "Web App" 1.8

echo -e "${YELLOW}Mobile App: 1.0 (Normal priority)${NC}"
./project_manager.sh pool priority "Mobile App" 1.0

echo -e "${YELLOW}Backend API: 0.5 (Low priority - maintenance mode)${NC}"
./project_manager.sh pool priority "Backend API" 0.5

# Step 5: Show current state
echo ""
echo -e "${BLUE}Step 5: Current System State${NC}"
./project_manager.sh list
echo ""
./project_manager.sh pool summary

# Step 6: Create sample tasks for each project
echo ""
echo -e "${BLUE}Step 6: Creating Sample Tasks${NC}"

# Function to create tasks for a project
create_project_tasks() {
    local project_id=$1
    local project_name=$2
    local task_file="projects/$project_id/task_assignments/task_queue.json"
    
    echo -e "${GREEN}Creating tasks for $project_name${NC}"
    
    # Create task directory if needed
    mkdir -p "projects/$project_id/task_assignments"
    
    # Generate sample tasks based on project type
    case "$project_name" in
        "Web App")
            cat > "$task_file" << EOF
{
  "project_id": "$project_id",
  "tasks": [
    {
      "task_id": "web_task_001",
      "title": "Fix Critical Payment Processing Bug",
      "description": "Payment gateway is failing for international customers",
      "task_type": "bugfix",
      "priority": "critical",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 4.0,
      "tags": ["payment", "critical", "production"],
      "dependencies": []
    },
    {
      "task_id": "web_task_002",
      "title": "Implement Shopping Cart Persistence",
      "description": "Cart items should persist across sessions",
      "task_type": "development",
      "priority": "high",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 6.0,
      "tags": ["cart", "feature"],
      "dependencies": []
    },
    {
      "task_id": "web_task_003",
      "title": "Add Product Search Filters",
      "description": "Add category and price range filters",
      "task_type": "development",
      "priority": "normal",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 3.0,
      "tags": ["search", "ui"],
      "dependencies": []
    }
  ],
  "queue": ["web_task_001", "web_task_002", "web_task_003"],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
            ;;
            
        "Mobile App")
            cat > "$task_file" << EOF
{
  "project_id": "$project_id",
  "tasks": [
    {
      "task_id": "mobile_task_001",
      "title": "Implement Push Notifications",
      "description": "Add support for order status notifications",
      "task_type": "development",
      "priority": "high",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 8.0,
      "tags": ["notifications", "feature"],
      "dependencies": []
    },
    {
      "task_id": "mobile_task_002",
      "title": "Optimize App Launch Time",
      "description": "Reduce cold start time by 50%",
      "task_type": "refactor",
      "priority": "normal",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 5.0,
      "tags": ["performance"],
      "dependencies": []
    },
    {
      "task_id": "mobile_task_003",
      "title": "Add Offline Mode",
      "description": "Allow browsing products without internet",
      "task_type": "development",
      "priority": "low",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 10.0,
      "tags": ["offline", "feature"],
      "dependencies": ["mobile_task_001"]
    }
  ],
  "queue": ["mobile_task_001", "mobile_task_002", "mobile_task_003"],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
            ;;
            
        "Backend API")
            cat > "$task_file" << EOF
{
  "project_id": "$project_id",
  "tasks": [
    {
      "task_id": "api_task_001",
      "title": "Update API Documentation",
      "description": "Document new endpoints for v2 API",
      "task_type": "documentation",
      "priority": "low",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 2.0,
      "tags": ["documentation"],
      "dependencies": []
    },
    {
      "task_id": "api_task_002",
      "title": "Add Rate Limiting",
      "description": "Implement rate limiting for public endpoints",
      "task_type": "security",
      "priority": "normal",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 4.0,
      "tags": ["security", "infrastructure"],
      "dependencies": []
    },
    {
      "task_id": "api_task_003",
      "title": "Database Query Optimization",
      "description": "Optimize slow queries in analytics service",
      "task_type": "refactor",
      "priority": "low",
      "status": "pending",
      "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "estimated_hours": 6.0,
      "tags": ["database", "performance"],
      "dependencies": []
    }
  ],
  "queue": ["api_task_001", "api_task_002", "api_task_003"],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
            ;;
    esac
}

# Create tasks for each project
create_project_tasks "$WEB_PROJECT_ID" "Web App"
create_project_tasks "$MOBILE_PROJECT_ID" "Mobile App" 
create_project_tasks "$API_PROJECT_ID" "Backend API"

# Step 7: Show global task queue
echo ""
echo -e "${BLUE}Step 7: Global Task Queue (Priority Ordered)${NC}"
./project_manager.sh pool queue

# Step 8: Process global task assignments
echo ""
echo -e "${BLUE}Step 8: Processing Global Task Assignments${NC}"
./project_manager.sh pool assign --no-prompt

# Step 9: Show final state
echo ""
echo -e "${BLUE}Step 9: Final System State${NC}"
./project_manager.sh status

echo ""
echo -e "${GREEN}✅ Multi-Project Demo Complete!${NC}"
echo ""
echo -e "${CYAN}Key Observations:${NC}"
echo "1. Tasks from the high-priority Web App project get assigned first"
echo "2. Critical and high-priority tasks across all projects take precedence"
echo "3. Low-priority projects (Backend API) wait until higher priority tasks complete"
echo "4. Agents work on tasks from different projects based on global priority"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Monitor progress: ./project_manager.sh monitor"
echo "2. Check specific project: ./project_manager.sh info <project>"
echo "3. Update task status: ./coordination_manager.sh update <agent> --task \"Task\" --progress 50"
echo "4. Add new tasks to any project and they'll be globally prioritized"
echo ""
echo -e "${MAGENTA}💡 TIP: The system automatically rebalances as tasks complete!${NC}"