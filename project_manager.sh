#!/bin/bash
# Multi-Project Coordination Manager CLI
# Manages multiple concurrent projects with isolated agent workspaces

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Python script paths
PROJECT_MANAGER_PY="coordination_system/project_manager.py"
GLOBAL_POOL_PY="coordination_system/global_task_pool.py"

# Help function
show_help() {
    echo -e "${CYAN}Multi-Project Coordination Manager${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Project Management Commands:${NC}"
    echo "  create <name> <path>     Create a new project"
    echo "    Options:"
    echo "      -d, --description    Project description"
    echo "      -a, --agents N       Number of agents (default: 6)"
    echo "      -t, --theme NAME     Agent theme"
    echo ""
    echo "  create-smart <name> <path>  Create project with automatic analysis and workflow"
    echo "    Analyzes codebase to detect technologies and generate optimal workflow"
    echo "    Options:"
    echo "      -d, --description    Project description"
    echo "      -a, --agents N       Number of agents (default: auto-detected)"
    echo "      -t, --theme NAME     Agent theme"
    echo "      --max-weeks N        Maximum project timeline in weeks"
    echo "      --team-size N        Available team size"
    echo "      --skip-analysis      Skip codebase analysis"
    echo "      --skip-workflow      Skip workflow generation"
    echo "      --skip-tasks         Skip automatic task generation"
    echo ""
    echo "  analyze <project>        Analyze existing project codebase"
    echo "  generate-tasks <project> Generate tasks for existing project"
    echo ""
    echo "  list [--status STATUS]   List all projects"
    echo "  switch <project>         Switch active project"
    echo "  info <project>           Show project details"
    echo "  stats <project>          Show project statistics"
    echo ""
    echo "  start <project>          Start agents for a project"
    echo "  stop <project>           Stop agents for a project"
    echo "  pause <project>          Pause a project"
    echo "  resume <project>         Resume a paused project"
    echo "  archive <project>        Archive a completed project"
    echo "  delete <project>         Delete a project (requires --confirm)"
    echo ""
    echo "  reset <project> [opts]   Reset project to initial state"
    echo "    Clears: agent status, communication, tasks, logs, worktrees"
    echo "    Preserves: project config, directory structure"
    echo "    Options:"
    echo "      --confirm            Required for production projects (triggers challenge)"
    echo "      --test               Force treat as test project (skip confirmations)"
    echo "    Examples:"
    echo "      $0 reset \"Test Suite\"                    # Instant reset (test project)"
    echo "      $0 reset \"Production DB\" --confirm       # Challenge required"
    echo ""
    echo "  reset-tests              Reset all test projects at once"
    echo "    Finds all projects marked as test and resets them without confirmation"
    echo "    Example: $0 reset-tests"
    echo ""
    echo "  mark-test <project>      Mark/unmark project as test project"
    echo "    Test projects can be reset without confirmation"
    echo "    SECURITY: Marking production projects as test requires --confirm"
    echo "    Options:"
    echo "      --unmark             Remove test marking (make production)"
    echo "      --confirm            Required for marking production projects as test"
    echo "    Examples:"
    echo "      $0 mark-test \"Dev Environment\" --confirm # Mark production as test"
    echo "      $0 mark-test \"Dev Environment\" --unmark  # Make production"
    echo "      $0 mark-test \"Test Suite\"                # Already test, no confirm needed"
    echo ""
    echo -e "${YELLOW}Global Task Pool Commands:${NC}"
    echo "  pool mode <mode>         Set pool mode (global_priority|project_dedicated|hybrid)"
    echo "  pool priority <project> <value>  Set project priority (0.1-2.0)"
    echo "  pool queue [--project]   Show global task queue"
    echo "  pool assign              Process global task assignments"
    echo "  pool summary             Show pool summary"
    echo ""
    echo -e "${YELLOW}Import/Export Commands:${NC}"
    echo "  export <project> -o FILE Export project configuration"
    echo "  import <file> [--codebase PATH]  Import project from config"
    echo ""
    echo -e "${YELLOW}Monitoring Commands:${NC}"
    echo "  monitor [project]        Show project monitoring dashboard"
    echo "  status                   Show overall system status"
    echo ""
    echo -e "${YELLOW}Reset Safety Features:${NC}"
    echo "  • Test projects (name contains 'test' or marked) reset instantly"
    echo "  • Production projects require --confirm flag and challenge response"
    echo "  • Challenge types: UPPERCASE name, RESET prefix, project ID, DELETE ALL DATA"
    echo "  • Wrong challenge response cancels reset operation"
    echo "  • All resets preserve project config and directory structure"
    echo ""
    echo -e "${YELLOW}Documentation:${NC}"
    echo "  cat SYSTEM_OPERATIONS_GUIDE.md    # Complete system operations"
    echo "  cat STARTUP_PROCEDURES.md         # Detailed startup procedures"  
    echo "  cat MONITORING_MAINTENANCE_GUIDE.md # Monitoring and maintenance"
    echo "  cat SHUTDOWN_CLEANUP_GUIDE.md     # Shutdown and cleanup procedures"
    echo "  cat TROUBLESHOOTING_GUIDE.md      # Issue resolution guide"
    echo "  cat PROJECT_RESET_GUIDE.md        # Project reset functionality"
    echo "  cat TEST_SCRIPTS_DOCUMENTATION.md # Test validation info"
    echo "  cat CLAUDE.md                     # Main project documentation"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  # Create a new project"
    echo "  $0 create \"Web App\" ~/projects/webapp -d \"E-commerce platform\" -a 8"
    echo ""
    echo "  # Create project with automatic analysis and workflow generation"
    echo "  $0 create-smart \"ML Project\" ~/projects/ml-app -d \"Machine learning platform\""
    echo ""
    echo "  # Analyze existing project to detect technologies and patterns"
    echo "  $0 analyze \"Web App\""
    echo ""
    echo "  # Generate tasks for existing project based on codebase analysis"
    echo "  $0 generate-tasks \"ML Project\""
    echo ""
    echo "  # Switch to global priority mode"
    echo "  $0 pool mode global_priority"
    echo ""
    echo "  # Reset a test project (no confirmation needed)"
    echo "  $0 reset \"Test Project\""
    echo ""
    echo "  # Mark a project as test and reset it"
    echo "  $0 mark-test \"My Project\""
    echo "  $0 reset \"My Project\""
    echo ""
    echo "  # Set high priority for urgent project"
    echo "  $0 pool priority \"Web App\" 1.8"
    echo ""
    echo "  # Start agents with global task assignment"
    echo "  $0 pool assign"
}

# Create project
create_project() {
    if [ $# -lt 2 ]; then
        echo -e "${RED}Error: Project name and codebase path required${NC}"
        echo "Usage: $0 create <name> <path> [-d description] [-a agents] [-t theme]"
        exit 1
    fi
    
    PROJECT_NAME="$1"
    CODEBASE_PATH="$2"
    shift 2
    
    # Build Python command
    CMD="python3 $PROJECT_MANAGER_PY create \"$PROJECT_NAME\" \"$CODEBASE_PATH\""
    
    # Parse additional options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--description)
                CMD="$CMD -d \"$2\""
                shift 2
                ;;
            -a|--agents)
                CMD="$CMD -a $2"
                shift 2
                ;;
            -t|--theme)
                CMD="$CMD -t \"$2\""
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}Creating project: $PROJECT_NAME${NC}"
    
    # Run command and capture output
    OUTPUT=$(eval $CMD)
    echo "$OUTPUT"
    
    # Extract project ID from output
    PROJECT_ID=$(echo "$OUTPUT" | grep -oE 'proj_[a-f0-9]{8}' | head -1)
    
    if [ -n "$PROJECT_ID" ]; then
        echo ""
        echo -e "${GREEN}✅ Project created successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Add tasks to the project:"
        echo "   ./coordination_manager.sh update <agent> --task \"Task description\""
        echo ""
        echo "2. Start agents for this project:"
        echo "   $0 start $PROJECT_ID"
        echo ""
        echo "Or use global priority mode:"
        echo "   $0 pool mode global_priority"
        echo "   $0 pool assign"
    fi
}

# Create smart project with analysis
create_smart_project() {
    if [ $# -lt 2 ]; then
        echo -e "${RED}Error: Project name and codebase path required${NC}"
        echo "Usage: $0 create-smart <name> <path> [options]"
        exit 1
    fi
    
    PROJECT_NAME="$1"
    CODEBASE_PATH="$2"
    shift 2
    
    # Build Python command
    CMD="python3 $PROJECT_MANAGER_PY create-smart \"$PROJECT_NAME\" \"$CODEBASE_PATH\""
    
    # Parse additional options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--description)
                CMD="$CMD -d \"$2\""
                shift 2
                ;;
            -a|--agents)
                CMD="$CMD -a $2"
                shift 2
                ;;
            -t|--theme)
                CMD="$CMD -t \"$2\""
                shift 2
                ;;
            --max-weeks)
                CMD="$CMD --max-weeks $2"
                shift 2
                ;;
            --team-size)
                CMD="$CMD --team-size $2"
                shift 2
                ;;
            --skip-analysis)
                CMD="$CMD --skip-analysis"
                shift
                ;;
            --skip-workflow)
                CMD="$CMD --skip-workflow"
                shift
                ;;
            --skip-tasks)
                CMD="$CMD --skip-tasks"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}Creating smart project: $PROJECT_NAME${NC}"
    echo -e "${YELLOW}Analyzing codebase and generating workflow...${NC}"
    
    # Run command and capture output
    OUTPUT=$(eval $CMD)
    echo "$OUTPUT"
    
    # Extract project ID from output
    PROJECT_ID=$(echo "$OUTPUT" | grep -oE 'proj_[a-f0-9]{8}' | head -1)
    
    if [ -n "$PROJECT_ID" ]; then
        echo ""
        echo -e "${GREEN}✅ Smart project created successfully!${NC}"
        echo ""
        echo "Auto-generated features:"
        echo "• Codebase analysis with technology detection"
        echo "• Optimized workflow template based on project type"
        echo "• Automatic task generation from detected gaps"
        echo "• Team size recommendation based on complexity"
        echo ""
        echo "Next steps:"
        echo "1. Review generated tasks:"
        echo "   $0 info $PROJECT_ID"
        echo ""
        echo "2. Start agents for this project:"
        echo "   $0 start $PROJECT_ID"
    fi
}

# Analyze existing project
analyze_project() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        echo "Usage: $0 analyze <project>"
        exit 1
    fi
    
    PROJECT="$1"
    
    echo -e "${BLUE}Analyzing project: $PROJECT${NC}"
    python3 $PROJECT_MANAGER_PY analyze "$PROJECT"
}

# Generate tasks for existing project
generate_project_tasks() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        echo "Usage: $0 generate-tasks <project>"
        exit 1
    fi
    
    PROJECT="$1"
    
    echo -e "${BLUE}Generating tasks for project: $PROJECT${NC}"
    python3 $PROJECT_MANAGER_PY generate-tasks "$PROJECT"
}

# List projects
list_projects() {
    echo -e "${CYAN}Projects:${NC}"
    
    CMD="python3 $PROJECT_MANAGER_PY list"
    
    # Add status filter if provided
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                CMD="$CMD --status $2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    eval $CMD
}

# Switch active project
switch_project() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        exit 1
    fi
    
    python3 $PROJECT_MANAGER_PY switch "$1"
}

# Show project info
show_project_info() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        exit 1
    fi
    
    python3 $PROJECT_MANAGER_PY stats "$1"
}

# Start agents for a project
start_project() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        exit 1
    fi
    
    PROJECT="$1"
    
    # Get project ID
    PROJECT_ID=$(python3 -c "
from coordination_system.project_manager import ProjectManager
pm = ProjectManager()
p = pm.get_project('$PROJECT') or pm.get_project_by_name('$PROJECT')
if p: print(p.project_id)
")
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Project not found: $PROJECT${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Starting agents for project: $PROJECT${NC}"
    
    # Switch to project
    python3 $PROJECT_MANAGER_PY switch "$PROJECT_ID"
    
    # Generate agent files for this project
    WORKSPACE="projects/$PROJECT_ID"
    if [ -d "$WORKSPACE" ]; then
        echo -e "${YELLOW}Generating agent configurations...${NC}"
        ./generate_agents_dynamic.sh --project "$PROJECT_ID"
    fi
    
    # Start project-aware lifecycle manager
    echo -e "${YELLOW}Starting project lifecycle manager...${NC}"
    
    # Get pool mode from global config
    POOL_MODE=$(python3 -c "
from coordination_system.global_task_pool import GlobalTaskPoolManager
from coordination_system.project_manager import ProjectManager
pm = ProjectManager()
gtp = GlobalTaskPoolManager(pm)
print(gtp.pool_mode.value)
" 2>/dev/null || echo "global_priority")
    
    PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH" python3 coordination_system/project_lifecycle_manager.py \
        --project "$PROJECT_ID" \
        --pool-mode "$POOL_MODE" \
        --create-tasks &
    
    LIFECYCLE_PID=$!
    echo "Lifecycle manager PID: $LIFECYCLE_PID"
    
    # Save PID for later
    echo $LIFECYCLE_PID > "$WORKSPACE/lifecycle.pid"
    
    echo -e "${GREEN}✅ Agents started for project: $PROJECT${NC}"
}

# Stop agents for a project
stop_project() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Project ID or name required${NC}"
        exit 1
    fi
    
    PROJECT="$1"
    
    # Get project ID
    PROJECT_ID=$(python3 -c "
from coordination_system.project_manager import ProjectManager
pm = ProjectManager()
p = pm.get_project('$PROJECT') or pm.get_project_by_name('$PROJECT')
if p: print(p.project_id)
")
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Project not found: $PROJECT${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Stopping agents for project: $PROJECT${NC}"
    
    # Check for PID file
    WORKSPACE="projects/$PROJECT_ID"
    PID_FILE="$WORKSPACE/lifecycle.pid"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo -e "${GREEN}✅ Stopped lifecycle manager (PID: $PID)${NC}"
        fi
        rm -f "$PID_FILE"
    else
        echo -e "${YELLOW}No running processes found for project${NC}"
    fi
}

# Handle pool commands
handle_pool_command() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Pool subcommand required${NC}"
        echo "Available: mode, priority, queue, assign, summary"
        exit 1
    fi
    
    POOL_CMD="$1"
    shift
    
    case $POOL_CMD in
        mode)
            if [ -z "$1" ]; then
                echo -e "${RED}Error: Mode required (global_priority|project_dedicated|hybrid)${NC}"
                exit 1
            fi
            python3 $GLOBAL_POOL_PY mode "$1"
            ;;
            
        priority)
            if [ $# -lt 2 ]; then
                echo -e "${RED}Error: Project and priority value required${NC}"
                exit 1
            fi
            python3 $GLOBAL_POOL_PY priority "$1" "$2"
            ;;
            
        queue)
            CMD="python3 $GLOBAL_POOL_PY queue"
            if [ "$1" = "--project" ] && [ -n "$2" ]; then
                CMD="$CMD --project \"$2\""
            fi
            eval $CMD
            ;;
            
        assign)
            echo -e "${BLUE}Processing global task assignments...${NC}"
            python3 $GLOBAL_POOL_PY assign
            
            # Check for --no-prompt flag
            if [[ "$1" != "--no-prompt" ]]; then
                # Optionally start agents if not running
                echo ""
                read -p "Start lifecycle manager for assigned agents? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo -e "${YELLOW}Starting global lifecycle manager...${NC}"
                    ./manage_agents.sh auto
                fi
            fi
            ;;
            
        summary)
            python3 $GLOBAL_POOL_PY summary
            ;;
            
        *)
            echo -e "${RED}Unknown pool command: $POOL_CMD${NC}"
            exit 1
            ;;
    esac
}

# Monitor project or system
monitor_project() {
    if [ -n "$1" ]; then
        # Monitor specific project
        PROJECT="$1"
        PROJECT_ID=$(python3 -c "
from coordination_system.project_manager import ProjectManager
pm = ProjectManager()
p = pm.get_project('$PROJECT') or pm.get_project_by_name('$PROJECT')
if p: print(p.project_id)
")
        
        if [ -z "$PROJECT_ID" ]; then
            echo -e "${RED}Project not found: $PROJECT${NC}"
            exit 1
        fi
        
        echo -e "${CYAN}Monitoring project: $PROJECT${NC}"
        # Set project context and monitor
        python3 $PROJECT_MANAGER_PY switch "$PROJECT_ID"
        ./coordination_manager.sh watch
    else
        # Monitor all projects
        echo -e "${CYAN}Global System Monitor${NC}"
        watch -n 2 "$0 status"
    fi
}

# Show system status
show_status() {
    echo -e "${CYAN}=== Multi-Project Coordination Status ===${NC}"
    echo ""
    
    # Show active projects
    echo -e "${YELLOW}Active Projects:${NC}"
    python3 $PROJECT_MANAGER_PY list --status active | tail -n +3
    
    # Show pool mode
    echo ""
    echo -e "${YELLOW}Task Pool Mode:${NC}"
    MODE=$(python3 -c "
from coordination_system.global_task_pool import GlobalTaskPoolManager
from coordination_system.project_manager import ProjectManager
pm = ProjectManager()
gtp = GlobalTaskPoolManager(pm)
print(gtp.pool_mode.value)
" 2>/dev/null || echo "Not configured")
    echo "  $MODE"
    
    # Show global queue summary
    echo ""
    echo -e "${YELLOW}Global Task Summary:${NC}"
    python3 $GLOBAL_POOL_PY summary 2>/dev/null | grep -E "(Total tasks:|By Priority:)" -A 5 || echo "  No tasks in queue"
    
    # Check if lifecycle daemon is running
    echo ""
    echo -e "${YELLOW}Lifecycle Manager:${NC}"
    if ./manage_agents.sh lifecycle status 2>/dev/null | grep -q "running"; then
        echo -e "  ${GREEN}✓ Running${NC}"
    else
        echo -e "  ${RED}✗ Not running${NC}"
    fi
}

# Main command routing
case "${1:-help}" in
    create)
        shift
        create_project "$@"
        ;;
        
    create-smart)
        shift
        create_smart_project "$@"
        ;;
        
    analyze)
        analyze_project "$2"
        ;;
        
    generate-tasks)
        generate_project_tasks "$2"
        ;;
        
    list)
        shift
        list_projects "$@"
        ;;
        
    switch)
        switch_project "$2"
        ;;
        
    info|stats)
        show_project_info "$2"
        ;;
        
    start)
        start_project "$2"
        ;;
        
    stop)
        stop_project "$2"
        ;;
        
    pause|resume|archive)
        python3 $PROJECT_MANAGER_PY "$1" "$2"
        ;;
        
    delete)
        if [ "$3" != "--confirm" ]; then
            echo -e "${RED}Error: Delete requires --confirm flag${NC}"
            echo "Usage: $0 delete <project> --confirm"
            exit 1
        fi
        python3 $PROJECT_MANAGER_PY delete "$2" --confirm
        ;;
        
    reset)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Project name required${NC}"
            echo "Usage: $0 reset <project> [--confirm] [--test]"
            exit 1
        fi
        
        PROJECT_NAME="$2"
        
        # Check if it's a test project by name first
        if [[ "$PROJECT_NAME" =~ [Tt]est ]]; then
            echo -e "${CYAN}Detected test project by name.${NC}"
        fi
        
        # Build command
        CMD="python3 $PROJECT_MANAGER_PY reset \"$PROJECT_NAME\""
        
        # Check for flags
        shift 2  # Skip 'reset' and project name
        HAS_CONFIRM=false
        HAS_TEST=false
        
        while [[ $# -gt 0 ]]; do
            case $1 in
                --confirm)
                    CMD="$CMD --confirm"
                    HAS_CONFIRM=true
                    ;;
                --test)
                    CMD="$CMD --test"
                    HAS_TEST=true
                    ;;
                *)
                    echo -e "${RED}Unknown option: $1${NC}"
                    exit 1
                    ;;
            esac
            shift
        done
        
        # Add warning for production resets
        if [ "$HAS_CONFIRM" = true ] && [ "$HAS_TEST" = false ]; then
            echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
            echo -e "${RED}⚠️  PRODUCTION PROJECT RESET WARNING ⚠️${NC}"
            echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
            echo ""
            echo -e "${RED}You are about to reset a production project.${NC}"
            echo -e "${RED}This will permanently delete:${NC}"
            echo "  • All agent status and communication data"
            echo "  • All task assignments and queues"
            echo "  • All agent prompts and configurations"
            echo "  • All worktrees and logs"
            echo ""
            echo -e "${YELLOW}This action CANNOT be undone!${NC}"
            echo ""
            echo -e "${CYAN}You will be asked to complete a challenge to proceed.${NC}"
            echo ""
            read -p "Press ENTER to continue or Ctrl+C to cancel..."
        fi
        
        # Run the command with proper TTY handling for interactive input
        eval $CMD
        ;;
        
    reset-tests)
        echo -e "${BLUE}Resetting all test projects...${NC}"
        python3 $PROJECT_MANAGER_PY reset-tests
        ;;
        
    mark-test)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Project name required${NC}"
            echo "Usage: $0 mark-test <project> [--unmark] [--confirm]"
            exit 1
        fi
        
        CMD="python3 $PROJECT_MANAGER_PY mark-test \"$2\""
        
        # Process flags
        shift 2  # Skip 'mark-test' and project name
        while [[ $# -gt 0 ]]; do
            case $1 in
                --unmark)
                    CMD="$CMD --unmark"
                    ;;
                --confirm)
                    CMD="$CMD --confirm"
                    ;;
                *)
                    echo -e "${RED}Error: Unknown flag: $1${NC}"
                    echo "Usage: $0 mark-test <project> [--unmark] [--confirm]"
                    exit 1
                    ;;
            esac
            shift
        done
        
        eval $CMD
        ;;
        
    export)
        if [ -z "$2" ] || [ "$3" != "-o" ] || [ -z "$4" ]; then
            echo -e "${RED}Error: Export requires project and output file${NC}"
            echo "Usage: $0 export <project> -o <file>"
            exit 1
        fi
        python3 $PROJECT_MANAGER_PY export "$2" -o "$4"
        ;;
        
    import)
        CMD="python3 $PROJECT_MANAGER_PY import \"$2\""
        if [ "$3" = "--codebase" ] && [ -n "$4" ]; then
            CMD="$CMD --codebase \"$4\""
        fi
        eval $CMD
        ;;
        
    pool)
        shift
        handle_pool_command "$@"
        ;;
        
    monitor)
        monitor_project "$2"
        ;;
        
    status)
        show_status
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac