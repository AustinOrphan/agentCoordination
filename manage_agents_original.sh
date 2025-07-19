#!/bin/bash
# Master Agent Management Script

show_help() {
    echo "🤖 File Organizer Agent Management"
    echo ""
    echo "Usage: $0 [command] [agent|option]"
    echo ""
    echo "Commands:"
    echo "  start <agent>    - Start a specific agent"
    echo "  auto             - Start all agents automatically based on dependencies"
    echo "  kickoff          - Start Agent Alpha and schedule dependent agents"
    echo "  status          - Show current agent status"
    echo "  list            - List all available agents"
    echo "  help            - Show this help message"
    echo ""
    echo "Agents:"
    echo "  alpha           - Critical Path Lead (starts immediately)"
    echo "  beta            - Migration Specialist (starts after alpha)"
    echo "  gamma           - Dashboard Developer (starts after alpha)"
    echo "  delta           - DevOps Engineer (starts after alpha)"
    echo "  epsilon         - Security Engineer (starts after alpha task 1.3)"
    echo "  zeta            - UX Engineer (starts after gamma task 3.2)"
    echo ""
    echo "Examples:"
    echo "  $0 start alpha         - Start Agent Alpha only"
    echo "  $0 auto               - Start all agents with dependency management"
    echo "  $0 kickoff            - Start Alpha and queue others"
    echo "  $0 status             - Check current status"
    echo ""
    echo "Note: Each agent opens in a new Terminal window."
    echo "You can run multiple Claude Code sessions simultaneously."
}

start_agent() {
    case $1 in
        "alpha")
            echo "🚀 Starting Agent Alpha (Critical Path Lead)"
            echo "Opening new Claude Code session..."
            ./start_agent_alpha.sh
            ;;
        "beta")
            echo "🚀 Starting Agent Beta (Migration Specialist)"
            echo "Opening new Claude Code session..."
            ./start_agent_beta.sh
            ;;
        "gamma")
            echo "🚀 Starting Agent Gamma (Dashboard Developer)"
            echo "Opening new Claude Code session..."
            ./start_agent_gamma.sh
            ;;
        "delta")
            echo "🚀 Starting Agent Delta (DevOps Engineer)"
            echo "Opening new Claude Code session..."
            ./start_agent_delta.sh
            ;;
        "epsilon")
            echo "🚀 Starting Agent Epsilon (Security Engineer)"
            echo "Opening new Claude Code session..."
            ./start_agent_epsilon.sh
            ;;
        "zeta")
            echo "🚀 Starting Agent Zeta (UX Engineer)"
            echo "Opening new Claude Code session..."
            ./start_agent_zeta.sh
            ;;
        *)
            echo "❌ Unknown agent: $1"
            echo "Available agents: alpha, beta, gamma, delta, epsilon, zeta"
            exit 1
            ;;
    esac
}

auto_start_agents() {
    echo "🚀 Starting File Organizer Project with Automatic Agent Management"
    echo ""
    echo "Phase 1: Starting Agent Alpha (Critical Path Lead)"
    echo "⏳ Agent Alpha will start immediately and work on Task 1.1 - Core Integration"
    start_agent alpha
    
    echo ""
    echo "Phase 2: Scheduling dependent agents (will start after Alpha completes Task 1.1)"
    echo "📅 Agent Beta - Migration Specialist (Task 2.1)"
    echo "📅 Agent Gamma - Dashboard Developer (Task 3.1)"  
    echo "📅 Agent Delta - DevOps Engineer (Task 2.2)"
    
    echo ""
    echo "Phase 3: Later agents (will start after their dependencies)"
    echo "📅 Agent Epsilon - Security Engineer (after Alpha Task 1.3)"
    echo "📅 Agent Zeta - UX Engineer (after Gamma Task 3.2)"
    
    echo ""
    echo "⚠️  IMPORTANT: You need to manually start dependent agents when their dependencies are satisfied."
    echo "   Monitor Agent Alpha's progress and start other agents with:"
    echo "   $0 start beta    (after Alpha completes Task 1.1)"
    echo "   $0 start gamma   (after Alpha completes Task 1.1)"
    echo "   $0 start delta   (after Alpha completes Task 1.1)"
    echo "   $0 start epsilon (after Alpha completes Task 1.3)"
    echo "   $0 start zeta    (after Gamma completes Task 3.2)"
    
    echo ""
    echo "💡 Pro tip: Use '$0 status' to monitor progress and check when dependencies are satisfied."
}

kickoff_project() {
    echo "🚀 Kickoff: File Organizer Project"
    echo ""
    echo "Starting Agent Alpha (Critical Path Lead) immediately..."
    start_agent alpha
    
    echo ""
    echo "📋 Next Steps:"
    echo "1. Monitor Agent Alpha's progress on Task 1.1 - Core Integration"
    echo "2. When Alpha completes Task 1.1, run: $0 start beta"
    echo "3. When Alpha completes Task 1.1, run: $0 start gamma"
    echo "4. When Alpha completes Task 1.1, run: $0 start delta"
    echo "5. When Alpha completes Task 1.3, run: $0 start epsilon"
    echo "6. When Gamma completes Task 3.2, run: $0 start zeta"
    echo ""
    echo "Use '$0 status' to check progress and dependencies."
}

show_status() {
    echo "📊 Current Agent Status:"
    echo ""
    if [ -f "AGENT_COORDINATION.md" ]; then
        echo "Reading from AGENT_COORDINATION.md..."
        # Show agent sections from coordination file
        grep -A 5 "Agent.*(" AGENT_COORDINATION.md 2>/dev/null || echo "No status found in coordination file"
    else
        echo "⚠️  AGENT_COORDINATION.md not found"
    fi
}

list_agents() {
    echo "🤖 Available Agents:"
    echo ""
    echo "Agent Alpha (Critical Path Lead):"
    echo "  Role: Senior Developer, Critical Path"
    echo "  Status: Ready to start"
    echo "  Task: 1.1 - Core Integration"
    echo ""
    echo "Agent Beta (Migration Specialist):"
    echo "  Role: Backend Developer, Migration"
    echo "  Status: Waiting for Alpha Task 1.1"
    echo "  Task: 2.1 - Advanced Migration Tools"
    echo ""
    echo "Agent Gamma (Dashboard Developer):"
    echo "  Role: Fullstack Developer, Dashboard"
    echo "  Status: Waiting for Alpha Task 1.1"
    echo "  Task: 3.1 - Advanced Dashboard"
    echo ""
    echo "Agent Delta (DevOps Engineer):"
    echo "  Role: DevOps Engineer, Infrastructure"
    echo "  Status: Waiting for Alpha Task 1.1"
    echo "  Task: 2.2 - CI/CD Pipeline"
    echo ""
    echo "Agent Epsilon (Security Engineer):"
    echo "  Role: Security Engineer, Compliance"
    echo "  Status: Waiting for Alpha Task 1.3"
    echo "  Task: 1.3 - Security Review"
    echo ""
    echo "Agent Zeta (UX Engineer):"
    echo "  Role: Frontend Developer, UX"
    echo "  Status: Waiting for Gamma Task 3.2"
    echo "  Task: 3.4 - Enhanced CLI Interface"
}

# Main script logic
case $1 in
    "start")
        if [ -z "$2" ]; then
            echo "❌ Please specify an agent to start"
            echo "Usage: $0 start <agent>"
            exit 1
        fi
        start_agent $2
        ;;
    "auto")
        auto_start_agents
        ;;
    "kickoff")
        kickoff_project
        ;;
    "status")
        show_status
        ;;
    "list")
        list_agents
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac