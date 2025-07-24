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

# Default options
AUTO_START=true
AUTO_WATCH=true
PROJECT_NAME=""
DESCRIPTION=""
DEADLINE=""
PROJECT_PATH=""
PLANS_PATH=""
COMMAND=""

# Display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Interactive mode (default):"
    echo "  $0"
    echo ""
    echo "Command line mode:"
    echo "  $0 new \"Project Name\" [-d \"Description\"] [--deadline YYYY-MM-DD] [--plans /path/to/plans]"
    echo "  $0 existing /path/to/project [-n \"Custom Name\"] [--deadline YYYY-MM-DD] [--plans /path/to/plans]"
    echo ""
    echo "Note: For existing projects, deployment plans are auto-detected in 'deployment-plans' or 'plans' directories"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d             Project description (new projects)"
    echo "  -n             Custom project name (existing projects)"
    echo "  --deadline     Project deadline in YYYY-MM-DD format (optional)"
    echo "  --plans        Path to deployment plans directory"
    echo "  --no-auto      Don't start the lifecycle daemon automatically"
    echo "  --no-watch     Don't open the monitoring dashboard"
    echo "  --non-interactive  Skip interactive prompts"
    exit 1
}

# Function for interactive mode
interactive_mode() {
    echo -e "${BLUE}🚀 Multi-Agent Coordination System - Interactive Setup${NC}"
    echo ""
    
    # Ask for project type
    echo "Is this a new project or an existing one?"
    echo "1) New project"
    echo "2) Existing project"
    read -p "Select (1-2): " project_type
    
    case $project_type in
        1)
            COMMAND="new"
            # Get project name
            read -p "Enter project name: " PROJECT_NAME
            if [ -z "$PROJECT_NAME" ]; then
                echo -e "${RED}Error: Project name cannot be empty${NC}"
                exit 1
            fi
            
            # Get optional description
            read -p "Enter project description (optional): " DESCRIPTION
            ;;
        2)
            COMMAND="existing"
            # Check if we're already in a project directory
            current_dir=$(pwd)
            if [ -f "$current_dir/package.json" ] || [ -f "$current_dir/requirements.txt" ] || \
               [ -f "$current_dir/Gemfile" ] || [ -f "$current_dir/pom.xml" ] || \
               [ -f "$current_dir/Cargo.toml" ] || [ -f "$current_dir/go.mod" ] || \
               [ -d "$current_dir/.git" ] || [ -d "$current_dir/src" ]; then
                echo -e "${GREEN}Detected project in current directory: $current_dir${NC}"
                read -p "Use current directory as project? (Y/n): " use_current
                if [[ ! "$use_current" =~ ^[Nn]$ ]]; then
                    PROJECT_PATH="$current_dir"
                else
                    read -p "Enter path to existing project: " PROJECT_PATH
                fi
            else
                # Check parent directory
                parent_dir=$(dirname "$current_dir")
                if [ -f "$parent_dir/package.json" ] || [ -f "$parent_dir/requirements.txt" ] || \
                   [ -f "$parent_dir/Gemfile" ] || [ -f "$parent_dir/pom.xml" ] || \
                   [ -f "$parent_dir/Cargo.toml" ] || [ -f "$parent_dir/go.mod" ] || \
                   [ -d "$parent_dir/.git" ] || [ -d "$parent_dir/src" ]; then
                    echo -e "${GREEN}Detected project in parent directory: $parent_dir${NC}"
                    read -p "Use parent directory as project? (Y/n): " use_parent
                    if [[ ! "$use_parent" =~ ^[Nn]$ ]]; then
                        PROJECT_PATH="$parent_dir"
                    else
                        read -p "Enter path to existing project: " PROJECT_PATH
                    fi
                else
                    read -p "Enter path to existing project (or press Enter for current directory): " PROJECT_PATH
                    # Default to current directory if empty
                    if [ -z "$PROJECT_PATH" ]; then
                        PROJECT_PATH="$current_dir"
                        echo -e "${BLUE}Using current directory: $PROJECT_PATH${NC}"
                    fi
                fi
            fi
            
            if [ ! -d "$PROJECT_PATH" ]; then
                echo -e "${RED}Error: Directory does not exist: $PROJECT_PATH${NC}"
                exit 1
            fi
            
            # Get optional custom name
            read -p "Enter custom project name (optional, press Enter to skip): " PROJECT_NAME
            ;;
        *)
            echo -e "${RED}Invalid selection${NC}"
            exit 1
            ;;
    esac
    
    # Ask about deployment plans
    echo ""
    echo "Do you have deployment plans to integrate?"
    if [ "$COMMAND" = "existing" ] && [ -d "$PROJECT_PATH/deployment-plans" ]; then
        echo -e "${GREEN}(Auto-detected plans in $PROJECT_PATH/deployment-plans)${NC}"
    elif [ "$COMMAND" = "existing" ] && [ -d "$PROJECT_PATH/plans" ]; then
        echo -e "${GREEN}(Auto-detected plans in $PROJECT_PATH/plans)${NC}"
    fi
    read -p "Enter path to plans directory (optional, press Enter to skip or use auto-detected): " PLANS_PATH
    
    # Ask about deadline (optional)
    echo ""
    read -p "Enter project deadline YYYY-MM-DD (optional, press Enter to skip): " DEADLINE
    if [ -n "$DEADLINE" ]; then
        # Basic date validation
        if ! [[ "$DEADLINE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            echo -e "${YELLOW}Warning: Deadline format should be YYYY-MM-DD${NC}"
            DEADLINE=""
        fi
    fi
    
    # Ask about auto-start
    echo ""
    read -p "Start lifecycle daemon automatically? (Y/n): " auto_response
    if [[ "$auto_response" =~ ^[Nn]$ ]]; then
        AUTO_START=false
    fi
    
    # Ask about monitoring
    read -p "Open monitoring dashboard? (Y/n): " watch_response
    if [[ "$watch_response" =~ ^[Nn]$ ]]; then
        AUTO_WATCH=false
    fi
    
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo "- Type: $COMMAND project"
    if [ "$COMMAND" = "new" ]; then
        echo "- Name: $PROJECT_NAME"
        [ -n "$DESCRIPTION" ] && echo "- Description: $DESCRIPTION"
    else
        echo "- Path: $PROJECT_PATH"
        [ -n "$PROJECT_NAME" ] && echo "- Custom name: $PROJECT_NAME"
    fi
    [ -n "$PLANS_PATH" ] && echo "- Plans: $PLANS_PATH"
    [ -n "$DEADLINE" ] && echo "- Deadline: $DEADLINE"
    echo "- Auto-start daemon: $AUTO_START"
    echo "- Open dashboard: $AUTO_WATCH"
    echo ""
    
    read -p "Proceed with setup? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
}

# Check for help flag first
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# Check if no arguments - run interactive mode
INTERACTIVE_MODE=false
if [ $# -eq 0 ]; then
    interactive_mode
    INTERACTIVE_MODE=true
    # Skip command parsing - go directly to execution
else
    # Parse command type
    COMMAND=$1
    shift
fi

# Only parse arguments if NOT in interactive mode
if [ "$INTERACTIVE_MODE" = false ]; then
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
                --plans)
                    PLANS_PATH="$2"
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
                --plans)
                    PLANS_PATH="$2"
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
fi

# Success - now offer to start the system
echo ""
echo -e "${GREEN}✅ Project initialization complete!${NC}"
echo ""

# Check for deployment plans
if [ -n "$PLANS_PATH" ]; then
    echo -e "${BLUE}📋 Integrating deployment plans from: $PLANS_PATH${NC}"
    if [ -d "$PLANS_PATH" ]; then
        ./generate_agents_with_plans.sh --plans "$PLANS_PATH"
        echo -e "${GREEN}✅ Deployment plans integrated successfully!${NC}"
    else
        echo -e "${RED}⚠️  Warning: Plans directory not found: $PLANS_PATH${NC}"
    fi
elif [ "$COMMAND" = "existing" ] && [ -d "$PROJECT_PATH/deployment-plans" ]; then
    # Auto-detect deployment plans in existing project
    echo -e "${BLUE}📋 Found deployment plans in project, integrating...${NC}"
    ./generate_agents_with_plans.sh --plans "$PROJECT_PATH/deployment-plans"
    echo -e "${GREEN}✅ Deployment plans integrated successfully!${NC}"
elif [ "$COMMAND" = "existing" ] && [ -d "$PROJECT_PATH/plans" ]; then
    # Alternative location for plans
    echo -e "${BLUE}📋 Found plans directory in project, integrating...${NC}"
    ./generate_agents_with_plans.sh --plans "$PROJECT_PATH/plans"
    echo -e "${GREEN}✅ Plans integrated successfully!${NC}"
else
    # No deployment plans found - generate default agents
    echo -e "${BLUE}📋 No deployment plans found, generating default agents...${NC}"
    ./generate_agents_dynamic.sh
    echo -e "${GREEN}✅ Default agents generated successfully!${NC}"
fi

# Initialize agent status files
echo -e "${BLUE}📊 Initializing agent status files...${NC}"
python3 init_agent_status.py
echo -e "${GREEN}✅ Agent status files initialized!${NC}"

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