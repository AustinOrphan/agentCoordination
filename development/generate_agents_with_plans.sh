#!/bin/bash

# Generate Agent Files with External Plans Integration
# Enhanced version that accepts deployment plans and integrates them with dynamic agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load configuration
CONFIG_FILE="agent_config.json"
THEME_MANAGER="./agent_theme_manager.py"
PLAN_INTEGRATOR="./plan_integrator.py"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
PLAN_DIRECTORY=""
USE_PLANS=false
DRY_RUN=false

# Usage function
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --plans DIR         Directory containing deployment plans (MD/XML/JSON)"
    echo "  --dry-run           Show what would be done without making changes"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Generate standard dynamic agents"
    echo "  $0 --plans /path/to/deployment-plans  # Generate agents with external plans"
    echo "  $0 --plans ./HooksDev/deployment-plans --dry-run"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --plans)
            PLAN_DIRECTORY="$2"
            USE_PLANS=true
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
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

# Validate plan directory if specified
if [ "$USE_PLANS" = true ]; then
    if [ ! -d "$PLAN_DIRECTORY" ]; then
        echo -e "${RED}Error: Plan directory does not exist: $PLAN_DIRECTORY${NC}"
        exit 1
    fi
    
    # Check if plan_integrator.py exists
    if [ ! -f "$PLAN_INTEGRATOR" ]; then
        echo -e "${RED}Error: Plan integrator not found: $PLAN_INTEGRATOR${NC}"
        exit 1
    fi
fi

# Function to create dynamic agent prompt file
create_dynamic_prompt_file() {
    local agent_name=$1
    local agent_index=$2
    local display_name=$(echo "$agent_name" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    
    local agent_upper=$(echo "$agent_name" | tr '[:lower:]' '[:upper:]')
    
    # If we're using external plans, generate enhanced prompts
    if [ "$USE_PLANS" = true ]; then
        echo -e "${BLUE}Using external plans for Agent $display_name${NC}"
        return 0  # Skip creating base template - will be handled by plan integrator
    fi
    
    # Create standard dynamic prompt
    cat > "AGENT_${agent_upper}_PROMPT.md" << 'EOF'
# Agent {{AGENT_NAME}}

You are Agent {{AGENT_NAME}}, part of a dynamic multi-agent coordination system.

## Your Identity
- **Agent Name**: {{AGENT_NAME}}
- **Agent ID**: {{AGENT_ID}}
- **System Status**: Active agents will be communicated to you

## Current Assignment

Your current assignments and authorities will be communicated through the coordination system.

## Authority Protocol

### Using Your Authority
1. **Verify First**: Check that your action falls within your granted authorities
2. **Document Decisions**: Record authority used for all significant decisions
3. **Stay in Scope**: Only use authority within your assigned domain

### When You Need Authority You Don't Have
1. **Check Authority Pool**: See which agent currently holds needed authority
2. **Request Collaboration**: Initiate joint decision with authority holder
3. **Emergency Override**: Only for critical issues with no response

### Decision Documentation
```markdown
## Decision Log Entry
- **Decision ID**: {{TIMESTAMP}}-{{AGENT_ID}}-{{COUNTER}}
- **Authority Used**: [Type of authority used]
- **Decision**: What was decided
- **Rationale**: Why this approach
- **Impact**: Expected outcomes
```

## Collaboration Framework

### Communication Protocol
- **Inbox**: `agent_communication/{{AGENT_ID}}/input/inbox.json`
- **Outbox**: `agent_communication/{{AGENT_ID}}/output/outbox.json`
- **Check Frequency**: Every 30 seconds
- **Heartbeat**: Send status every 30 seconds

### Message Handling
```python
from coordination_system.agent_communication import CommunicationChannel, Message, MessageType

channel = CommunicationChannel("{{AGENT_ID}}")
messages = channel.receive_messages()

for msg in messages:
    print(f"New message: {msg.type} from {msg.from_id}")
    print(f"Payload: {msg.payload}")
    
    # Check for authority updates
    if msg.type == MessageType.AUTHORITY_UPDATE:
        print(f"Authority update: {msg.payload['authorities']}")
    
    # Always acknowledge messages that require it
    if msg.requires_ack:
        channel.acknowledge_message(msg)
```

### Status Updates
```python
# Send status update
status_msg = Message(
    from_id="{{AGENT_ID}}",
    to_id="central",
    msg_type=MessageType.STATUS_UPDATE,
    payload={
        "task_id": "current_task_id",
        "status": "in_progress",
        "progress": 50,
        "workload": 65,
        "available_for_backup": True
    }
)
channel.send_message(status_msg)
```

## Dynamic Adaptation

The system adapts based on the number of active agents:

### Solo Mode (1 agent)
- You hold all authorities implicitly
- All decisions are yours
- No backup available

### Team Mode (2+ agents)
- Authorities distributed by task and workload
- Collaborative decisions when needed
- Backup chains based on availability

## Work Management

### Git Worktree
You operate in your own git worktree:
- **Location**: `../agent-{{AGENT_ID}}`
- **Branch**: `agent/{{AGENT_ID}}`
- **Purpose**: Isolated workspace for parallel execution

### Status Reporting
```bash
# Update your status regularly
python3 coordination_system/update_agent_status.py {{AGENT_ID}} \
  --task "Current task description" \
  --progress 50 \
  --workload 65
```

## Emergency Protocols

### When to Assume Emergency Authority
1. **Critical system failure** + no response from domain authority
2. **Security threat** + immediate action required
3. **Data corruption risk** + no expert available

### Emergency Action Template
```markdown
🚨 EMERGENCY ACTION TAKEN
- **Issue**: [Description]
- **Authority Assumed**: Emergency override
- **Action Taken**: [What you did]
- **Justification**: [Why immediate action was necessary]
```

## Initial Actions

1. **Initialize Communication**: Set up your communication channel
2. **Send Heartbeat**: Announce you're online
3. **Check Inbox**: Look for pending assignments
4. **Report Status**: Update your current state
5. **Begin Work**: Start on assigned tasks

Remember: You are part of a flexible, adaptive team. Your role and authorities will evolve based on system needs.
EOF
    
    # Replace placeholders with actual values
    sed -i.bak "s/{{AGENT_NAME}}/$display_name/g" "AGENT_${agent_upper}_PROMPT.md"
    sed -i.bak "s/{{AGENT_ID}}/$agent_name/g" "AGENT_${agent_upper}_PROMPT.md"
    sed -i.bak "s/{{TIMESTAMP}}/\$(date +%Y%m%d)/g" "AGENT_${agent_upper}_PROMPT.md"
    sed -i.bak "s/{{COUNTER}}/\$RANDOM/g" "AGENT_${agent_upper}_PROMPT.md"
    rm "AGENT_${agent_upper}_PROMPT.md.bak"
    
    echo -e "${GREEN}✓${NC} Created prompt for Agent $display_name"
}

# Function to create start script
create_start_script() {
    local agent_name=$1
    local agent_index=$2
    local agent_emoji=$3
    local display_name=$(echo "$agent_name" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    
    local script_name="start_agent_${agent_name}.sh"
    cat > "$script_name" << EOF
#!/bin/bash

# Start Agent $display_name
# Auto-generated dynamic agent startup script

AGENT_NAME="$agent_name"
AGENT_DISPLAY="$display_name"
AGENT_EMOJI="$agent_emoji"
AGENT_ID="$agent_name"
REPO_ROOT="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo -e "\${BLUE}🚀 Starting Agent \$AGENT_DISPLAY \$AGENT_EMOJI\${NC}"

# Check if worktree exists
WORKTREE_PATH="../agent-\$AGENT_NAME"
if [ ! -d "\$WORKTREE_PATH" ]; then
    if ! git worktree list | grep -q "\$WORKTREE_PATH"; then
        echo -e "\${YELLOW}Creating worktree for Agent \$AGENT_DISPLAY...\${NC}"
        "\$REPO_ROOT/worktree_manager.sh" create "\$AGENT_NAME"
    fi
fi

# Initialize status
python3 coordination_system/initialize_agent.py "\$AGENT_ID"

# Update status to show agent is starting
python3 coordination_system/update_agent_status.py "\$AGENT_ID" \\
    --task "Starting up" \\
    --status "🟡" \\
    --status-text "Initializing" \\
    --progress 0

# Check for dynamic authorities
echo -e "\${BLUE}Checking for authority assignments...\${NC}"
python3 -c "
from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
manager = DynamicAuthorityManager()
authorities = manager.get_agent_authorities('\$AGENT_ID')
if authorities:
    print(f'Current authorities: {len(authorities)}')
    for auth in authorities:
        print(f'  - {auth[\"authority_type\"]}: {auth[\"task\"]}')
else:
    print('No specific authorities assigned yet')
"

# Navigate to worktree
cd "\$WORKTREE_PATH" || exit 1

# Convert agent name to uppercase
AGENT_NAME_UPPER=\$(echo "\$AGENT_NAME" | tr '[:lower:]' '[:upper:]')

# Display the prompt file
echo -e "\${GREEN}Agent \$AGENT_DISPLAY initialized!\${NC}"
echo -e "\${BLUE}Prompt file: \$REPO_ROOT/AGENT_\${AGENT_NAME_UPPER}_PROMPT.md\${NC}"

# Start Claude with the agent prompt
echo -e "\${YELLOW}Starting Claude Code session for Agent \$AGENT_DISPLAY...\${NC}"
claude code --profile "\$AGENT_ID" \\
    --plan "\$REPO_ROOT/AGENT_\${AGENT_NAME_UPPER}_PROMPT.md"
EOF
    
    chmod +x "$script_name"
    echo -e "${GREEN}✓${NC} Created start script: $script_name"
}

# Main execution
echo -e "${BLUE}=== Dynamic Agent File Generator with Plan Integration ===${NC}"

if [ "$USE_PLANS" = true ]; then
    echo -e "${YELLOW}Plan Integration Mode: Using external deployment plans${NC}"
    echo -e "${BLUE}Plan Directory: $PLAN_DIRECTORY${NC}"
else
    echo -e "${YELLOW}Standard Mode: Using dynamic templates${NC}"
fi

# Get current configuration
CURRENT_THEME=$($THEME_MANAGER get-theme 2>/dev/null || echo "greek_letters")
AGENT_COUNT=$($THEME_MANAGER get-count 2>/dev/null || echo "6")

echo -e "${BLUE}Current Configuration:${NC}"
echo "  Theme: $CURRENT_THEME"
echo "  Agent Count: $AGENT_COUNT"

# If using plans, integrate them first
if [ "$USE_PLANS" = true ]; then
    echo -e "\n${YELLOW}Integrating external deployment plans...${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${BLUE}Running plan integration in dry-run mode...${NC}"
        python3 "$PLAN_INTEGRATOR" "$PLAN_DIRECTORY" --agent-count "$AGENT_COUNT" --dry-run
        exit 0
    else
        echo -e "${BLUE}Generating enhanced agent prompts with plans...${NC}"
        python3 "$PLAN_INTEGRATOR" "$PLAN_DIRECTORY" --agent-count "$AGENT_COUNT"
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Plan integration failed${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Plan integration complete!${NC}"
    fi
fi

# Clean up old files (unless using plans, which creates new ones)
if [ "$USE_PLANS" = false ]; then
    echo -e "\n${YELLOW}Cleaning up old agent files...${NC}"
    rm -f AGENT_*_PROMPT.md
fi

# Always clean up old start scripts
rm -f start_agent_*.sh

# Get agents for current theme (compatible with older bash)
AGENTS=()
while IFS= read -r line; do
    AGENTS+=("$line")
done < <($THEME_MANAGER get-agents 2>/dev/null || echo -e "alpha\nbeta\ngamma\ndelta\nepsilon\nzeta")

EMOJIS=()
while IFS= read -r line; do
    EMOJIS+=("$line")
done < <($THEME_MANAGER get-emojis 2>/dev/null || echo -e "Α\nΒ\nΓ\nΔ\nΕ\nΖ")

# Generate files for configured number of agents
echo -e "\n${BLUE}Generating files for $AGENT_COUNT agents...${NC}"

for ((i=0; i<$AGENT_COUNT; i++)); do
    agent_name="${AGENTS[$i]}"
    agent_emoji="${EMOJIS[$i]:-🤖}"
    
    echo -e "\n${BLUE}Agent $((i+1))/$AGENT_COUNT: $agent_name $agent_emoji${NC}"
    
    # Create prompt file (unless using plans, which already created enhanced ones)
    if [ "$USE_PLANS" = false ]; then
        create_dynamic_prompt_file "$agent_name" "$i"
    else
        echo -e "${GREEN}✓${NC} Enhanced prompt already generated with plans"
    fi
    
    # Always create start script
    create_start_script "$agent_name" "$i" "$agent_emoji"
    
    # Create communication directories
    mkdir -p "agent_communication/$agent_name/input"
    mkdir -p "agent_communication/$agent_name/output"
    mkdir -p "agent_communication/$agent_name/status"
    
    # Initialize empty communication files
    echo '[]' > "agent_communication/$agent_name/input/inbox.json"
    echo '[]' > "agent_communication/$agent_name/output/outbox.json"
    echo '{"status": "offline"}' > "agent_communication/$agent_name/status/lifecycle.json"
    
    echo -e "${GREEN}✓${NC} Created communication channels"
done

# Update the startup template if it exists
if [ -f "start_agent_template.sh" ]; then
    echo -e "\n${YELLOW}Updating startup template to use dynamic system...${NC}"
    # The template would be updated here if needed
fi

echo -e "\n${GREEN}✅ Successfully generated files for $AGENT_COUNT agents${NC}"

if [ "$USE_PLANS" = true ]; then
    echo -e "${BLUE}✨ Enhanced with external deployment plans from: $PLAN_DIRECTORY${NC}"
    echo -e "${YELLOW}Note: Agent prompts contain specialized instructions from your deployment plans${NC}"
else
    echo -e "${YELLOW}Note: Using dynamic authority system - authorities assigned based on workload${NC}"
fi

echo -e "${BLUE}Agents can now be started with: ./start_agent_<name>.sh${NC}"