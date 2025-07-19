#!/bin/bash
# Start a project with the Multi-Agent Coordination System
# Supports both new and existing projects

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display usage
usage() {
    echo "Usage: $0 [new|existing] [options]"
    echo ""
    echo "For new projects:"
    echo "  $0 new \"Project Name\" [-d \"Description\"] [--deadline YYYY-MM-DD]"
    echo ""
    echo "For existing projects:"
    echo "  $0 existing /path/to/project [-n \"Custom Name\"] [--deadline YYYY-MM-DD]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d             Project description (new projects)"
    echo "  -n             Custom project name (existing projects)"
    echo "  --deadline     Project deadline in YYYY-MM-DD format"
    echo "  --no-auto      Don't start the lifecycle daemon automatically"
    echo "  --no-watch     Don't open the monitoring dashboard"
    exit 1
}

# Check if no arguments
if [ $# -eq 0 ]; then
    usage
fi

# Parse command type
COMMAND=$1
shift

# Default options
AUTO_START=true
AUTO_WATCH=true
PROJECT_NAME=""
DESCRIPTION=""
DEADLINE=""
PROJECT_PATH=""

# Parse arguments based on command
case $COMMAND in
    new)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Project name required for new projects${NC}"
            usage
        fi
        
        PROJECT_NAME=$1
        shift
        
        # Parse remaining options
        while [[ $# -gt 0 ]]; do
            case $1 in
                -d|--description)
                    DESCRIPTION="$2"
                    shift 2
                    ;;
                --deadline)
                    DEADLINE="$2"
                    shift 2
                    ;;
                --no-auto)
                    AUTO_START=false
                    shift
                    ;;
                --no-watch)
                    AUTO_WATCH=false
                    shift
                    ;;
                -h|--help)
                    usage
                    ;;
                *)
                    echo -e "${RED}Unknown option: $1${NC}"
                    usage
                    ;;
            esac
        done
        
        # Initialize new project
        echo -e "${BLUE}🚀 Initializing new project: ${PROJECT_NAME}${NC}"
        
        CMD="python3 coordination_system/init_new_project.py \"$PROJECT_NAME\""
        if [ -n "$DESCRIPTION" ]; then
            CMD="$CMD -d \"$DESCRIPTION\""
        fi
        if [ -n "$DEADLINE" ]; then
            CMD="$CMD --deadline \"$DEADLINE\""
        fi
        
        eval $CMD
        ;;
        
    existing)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Project path required for existing projects${NC}"
            usage
        fi
        
        PROJECT_PATH=$1
        shift
        
        # Validate project path
        if [ ! -d "$PROJECT_PATH" ]; then
            echo -e "${RED}Error: Project path does not exist: $PROJECT_PATH${NC}"
            exit 1
        fi
        
        # Parse remaining options
        while [[ $# -gt 0 ]]; do
            case $1 in
                -n|--name)
                    PROJECT_NAME="$2"
                    shift 2
                    ;;
                --deadline)
                    DEADLINE="$2"
                    shift 2
                    ;;
                --no-auto)
                    AUTO_START=false
                    shift
                    ;;
                --no-watch)
                    AUTO_WATCH=false
                    shift
                    ;;
                -h|--help)
                    usage
                    ;;
                *)
                    echo -e "${RED}Unknown option: $1${NC}"
                    usage
                    ;;
            esac
        done
        
        # Analyze existing project
        echo -e "${BLUE}🔍 Analyzing existing project at: $PROJECT_PATH${NC}"
        python3 coordination_system/analyze_existing_project.py "$PROJECT_PATH" -r
        
        # Check if analysis succeeded
        if [ ! -f "project_analysis.json" ]; then
            echo -e "${RED}Error: Project analysis failed${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Analysis complete! Review the report:${NC}"
        echo "   cat project_analysis_report.md"
        echo ""
        
        # Wait for user confirmation
        read -p "Press Enter to continue with initialization, or Ctrl+C to cancel..."
        
        # Initialize from analysis
        echo -e "${BLUE}🚀 Initializing coordination system from analysis${NC}"
        
        CMD="python3 coordination_system/init_existing_project.py project_analysis.json"
        if [ -n "$PROJECT_NAME" ]; then
            CMD="$CMD -n \"$PROJECT_NAME\""
        fi
        if [ -n "$DEADLINE" ]; then
            CMD="$CMD --deadline \"$DEADLINE\""
        fi
        
        eval $CMD
        ;;
        
    -h|--help)
        usage
        ;;
        
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo "Use 'new' or 'existing'"
        usage
        ;;
esac

# Success - now offer to start the system
echo ""
echo -e "${GREEN}✅ Project initialization complete!${NC}"
echo ""

# Start lifecycle daemon if requested
if [ "$AUTO_START" = true ]; then
    echo -e "${YELLOW}Starting lifecycle daemon...${NC}"
    ./manage_agents.sh auto
    
    # Give it a moment to start
    sleep 2
    
    # Check if daemon started
    if ./manage_agents.sh lifecycle status | grep -q "running"; then
        echo -e "${GREEN}✅ Lifecycle daemon started successfully${NC}"
    else
        echo -e "${RED}⚠️  Warning: Lifecycle daemon may not have started properly${NC}"
        echo "   Check with: ./manage_agents.sh lifecycle status"
    fi
fi

# Start monitoring dashboard if requested
if [ "$AUTO_WATCH" = true ]; then
    echo ""
    echo -e "${YELLOW}Starting monitoring dashboard in 3 seconds...${NC}"
    echo -e "${BLUE}(Press Ctrl+C to skip)${NC}"
    
    # Give user a chance to cancel
    sleep 3
    
    echo -e "${GREEN}Opening monitoring dashboard...${NC}"
    ./coordination_manager.sh watch &
    WATCH_PID=$!
    
    echo ""
    echo -e "${GREEN}🎉 System is running!${NC}"
    echo ""
    echo "Monitoring dashboard PID: $WATCH_PID"
    echo "To stop monitoring: kill $WATCH_PID"
else
    echo ""
    echo -e "${GREEN}🎉 Project ready!${NC}"
    echo ""
    echo "To start monitoring: ./coordination_manager.sh watch"
fi

echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Review agent assignments in AGENT_COORDINATION.md"
echo "2. Monitor progress in the dashboard"
echo "3. Update agent tasks as needed:"
echo "   ./coordination_manager.sh update <agent> --task \"New task\" --progress 50"
echo ""
echo -e "${YELLOW}📚 For more help, see:${NC}"
echo "   coordination_system/PROJECT_SETUP_GUIDE.md"
echo "   CLAUDE.md"