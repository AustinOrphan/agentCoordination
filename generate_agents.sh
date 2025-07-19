#!/bin/bash
# Agent Generator Script - Creates agent files based on current theme and count

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_MANAGER="$SCRIPT_DIR/agent_theme_manager.py"

# Function to show header
show_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                    AGENT GENERATOR                                           ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to get current configuration
get_config() {
    local theme=$("$THEME_MANAGER" show | grep "Theme:" | sed 's/.*(\(.*\))/\1/')
    local count=$("$THEME_MANAGER" show | grep "Agent count:" | awk '{print $3}')
    echo "$theme $count"
}

# Function to create agent startup script
create_startup_script() {
    local agent_name=$1
    local agent_index=$2
    local display_name=$(echo "$agent_name" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    
    cat > "start_agent_${agent_name}.sh" << 'EOF'
#!/bin/bash
# Start Agent [AGENT_NAME_UPPER] ([DISPLAY_NAME])

# Configuration
AGENT_NAME="[AGENT_NAME]"
AGENT_PROMPT="AGENT_[AGENT_NAME_UPPER]_PROMPT.md"
LOG_FILE="agent_[AGENT_NAME].log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Start message
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                              Starting Agent [DISPLAY_NAME]                                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if prompt file exists
if [ ! -f "$AGENT_PROMPT" ]; then
    echo -e "${RED}Error: Agent prompt file $AGENT_PROMPT not found${NC}"
    exit 1
fi

# Log start time
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Agent [DISPLAY_NAME]" >> "$LOG_FILE"

# Display agent info
echo -e "${GREEN}Agent Name:${NC} [DISPLAY_NAME]"
echo -e "${GREEN}Agent ID:${NC} $AGENT_NAME"
echo -e "${GREEN}Prompt File:${NC} $AGENT_PROMPT"
echo -e "${GREEN}Log File:${NC} $LOG_FILE"
echo ""

# Start claude with the agent prompt
echo -e "${YELLOW}Launching Claude CLI...${NC}"
echo ""

# Execute claude
claude code -m "$(cat "$AGENT_PROMPT")" 2>&1 | tee -a "$LOG_FILE"

# Log end time
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Agent [DISPLAY_NAME] session ended" >> "$LOG_FILE"
EOF

    # Replace placeholders
    sed -i '' "s/\[AGENT_NAME\]/$agent_name/g" "start_agent_${agent_name}.sh"
    sed -i '' "s/\[AGENT_NAME_UPPER\]/${agent_name^^}/g" "start_agent_${agent_name}.sh"
    sed -i '' "s/\[DISPLAY_NAME\]/$display_name/g" "start_agent_${agent_name}.sh"
    
    chmod +x "start_agent_${agent_name}.sh"
    
    echo -e "${GREEN}✓ Created start_agent_${agent_name}.sh${NC}"
}

# Function to create agent prompt file
create_prompt_file() {
    local agent_name=$1
    local agent_index=$2
    local display_name=$(echo "$agent_name" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    local agent_role=""
    
    # Assign roles based on index (cycling through standard roles)
    case $((agent_index % 6)) in
        0) agent_role="Critical Path Lead - Senior Developer" ;;
        1) agent_role="Migration Specialist - Backend Developer" ;;
        2) agent_role="Dashboard Developer - Fullstack Developer" ;;
        3) agent_role="DevOps Engineer" ;;
        4) agent_role="Security Engineer" ;;
        5) agent_role="UX Engineer - Frontend Developer" ;;
    esac
    
    cat > "AGENT_${agent_name^^}_PROMPT.md" << EOF
# Agent $display_name - $agent_role

You are Agent $display_name, part of a distributed multi-agent system working on a collaborative software project.

## Your Identity
- **Agent Name**: $display_name
- **Agent ID**: $agent_name
- **Role**: $agent_role
- **Agent Index**: $agent_index

## Your Responsibilities

Based on your role as $agent_role, you will be assigned specific tasks through the new bidirectional communication system.

## NEW: Bidirectional Communication System

You now have dedicated communication channels for asynchronous message passing:

### Your Communication Files
- **Inbox**: \`agent_communication/$agent_name/input/inbox.json\` - Messages TO you
- **Outbox**: \`agent_communication/$agent_name/output/outbox.json\` - Messages FROM you
- **Heartbeat**: Send regular heartbeats to show you're active

### Checking for New Messages
Check your inbox every 30 seconds for new instructions:
\`\`\`python
from coordination_system.agent_communication import CommunicationChannel, Message, MessageType

channel = CommunicationChannel("$agent_name")
messages = channel.receive_messages()

for msg in messages:
    print(f"New message: {msg.type} from {msg.from_id}")
    print(f"Payload: {msg.payload}")
    
    # Always acknowledge messages that require it
    if msg.requires_ack:
        channel.acknowledge_message(msg)
\`\`\`

### Sending Messages
Send status updates and requests through your outbox:
\`\`\`python
# Status update
status_msg = Message(
    from_id="$agent_name",
    to_id="central",
    msg_type=MessageType.STATUS_UPDATE,
    payload={
        "task_id": "task_123",
        "status": "in_progress",
        "progress": 50,
        "message": "Completed unit tests"
    }
)
channel.send_message(status_msg)

# Report a blocker
blocker_msg = Message(
    from_id="$agent_name",
    to_id="central",
    msg_type=MessageType.BLOCKER_REPORT,
    payload={
        "blocker_id": "block_001",
        "description": "Need database schema from Agent Alpha",
        "blocking_agent": "alpha",
        "severity": "high"
    }
)
channel.send_message(blocker_msg)
\`\`\`

### Sending Heartbeats
Send heartbeats every 30 seconds to show you're active:
\`\`\`python
from coordination_system.agent_communication import AgentStatus

channel.send_heartbeat(
    status=AgentStatus.WORKING,
    current_task="Implementing feature X",
    metrics={"cpu_usage": 45, "memory_usage": 1024}
)
\`\`\`

## Legacy Status Updates

You should still update your status file for compatibility:
\`\`\`bash
python3 coordination_system/update_agent_status.py $agent_name --task "Task Name" --progress 50
\`\`\`

## Working Process

1. **Initialize Communication**: Set up your communication channel
2. **Check Messages**: Poll inbox every 30 seconds for new tasks/updates
3. **Send Heartbeats**: Every 30 seconds to show you're active
4. **Execute Tasks**: Work on assigned tasks
5. **Report Progress**: Send status updates through outbox
6. **Handle Blockers**: Report blockers immediately, monitor for resolutions
7. **Acknowledge Messages**: Always acknowledge messages that require it

## Lifecycle Management

The system now automatically:
- **Starts** agents when dependencies are met and no blockers exist
- **Stops** agents when they become blocked
- **Monitors** agent health through heartbeats

If you receive a lifecycle control message to stop, wrap up your current work and shut down gracefully.

## Important Files

### Communication Files
- \`agent_communication/$agent_name/input/inbox.json\` - Your message inbox
- \`agent_communication/$agent_name/output/outbox.json\` - Your message outbox
- \`agent_communication/$agent_name/status/lifecycle.json\` - Your lifecycle status
- \`agent_communication/$agent_name/status/heartbeat.json\` - Your last heartbeat

### Legacy Files (still used)
- \`AGENT_COORDINATION.md\` - Overall project coordination
- \`agent_status/${agent_name}_status.json\` - Your status file
- \`coordination_system/update_agent_status.py\` - Status update utility

## Initial Actions

1. Import and initialize your communication channel
2. Send initial heartbeat to announce you're online
3. Check inbox for any pending messages
4. Read AGENT_COORDINATION.md for context
5. Update your status to show you're starting
6. Begin monitoring inbox every 30 seconds
7. Send heartbeats every 30 seconds
4. Provide regular progress updates

Remember: You are part of a team. Communicate clearly, update your status frequently, and help other agents when they're blocked.
EOF

    echo -e "${GREEN}✓ Created AGENT_${agent_name^^}_PROMPT.md${NC}"
}

# Function to create agent status file
create_status_file() {
    local agent_name=$1
    local agent_index=$2
    
    cat > "agent_status/${agent_name}_status.json" << EOF
{
  "agent_name": "$agent_name",
  "agent_index": $agent_index,
  "status": "initializing",
  "current_task": "Awaiting assignment",
  "progress": 0,
  "last_update": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "activities": [
    {
      "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
      "activity": "Agent initialized"
    }
  ],
  "blockers": [],
  "dependencies": [],
  "communication": {
    "requests": [],
    "offers": []
  },
  "metrics": {
    "tasks_completed": 0,
    "total_progress": 0,
    "time_active": 0
  }
}
EOF

    echo -e "${GREEN}✓ Created agent_status/${agent_name}_status.json${NC}"
}

# Function to update manage_agents.sh
update_manage_agents() {
    local agents=("$@")
    
    # Read the current script
    local script_content=$(cat manage_agents.sh)
    
    # Create new agent array
    local agent_array="AGENTS=("
    for agent in "${agents[@]}"; do
        agent_array+="\"$agent\" "
    done
    agent_array="${agent_array% })"
    
    # Replace the AGENTS array line
    echo "$script_content" | sed "s/^AGENTS=.*/$agent_array/" > manage_agents.sh.tmp
    mv manage_agents.sh.tmp manage_agents.sh
    chmod +x manage_agents.sh
    
    echo -e "${GREEN}✓ Updated manage_agents.sh${NC}"
}

# Main function
main() {
    show_header
    
    # Get current configuration
    read theme count <<< $(get_config)
    echo -e "${CYAN}Current Theme: $theme${NC}"
    echo -e "${CYAN}Agent Count: $count${NC}"
    echo ""
    
    # Get agent names
    mapfile -t agents < <("$THEME_MANAGER" get-agents)
    
    if [ ${#agents[@]} -eq 0 ]; then
        echo -e "${RED}Error: No agents found for current configuration${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Generating files for agents:${NC}"
    for agent in "${agents[@]}"; do
        echo "  - $agent"
    done
    echo ""
    
    # Create agent_status directory if it doesn't exist
    mkdir -p agent_status
    
    # Generate files for each agent
    for i in "${!agents[@]}"; do
        agent="${agents[$i]}"
        echo -e "${BLUE}Processing Agent $agent (index $i)...${NC}"
        
        create_startup_script "$agent" "$i"
        create_prompt_file "$agent" "$i"
        create_status_file "$agent" "$i"
        
        echo ""
    done
    
    # Update manage_agents.sh
    update_manage_agents "${agents[@]}"
    
    # Clean up old agent files if theme changed
    echo -e "${YELLOW}Cleaning up old agent files...${NC}"
    
    # Get all possible agent names from all themes
    all_agents=()
    while IFS= read -r line; do
        all_agents+=("$line")
    done < <(python3 -c "
import json
with open('agent_config.json') as f:
    config = json.load(f)
    for theme in config['themes'].values():
        for agent in theme['agents']:
            print(agent)
")
    
    # Remove files for agents not in current set
    for agent in "${all_agents[@]}"; do
        if [[ ! " ${agents[@]} " =~ " ${agent} " ]]; then
            # Remove files if they exist
            [ -f "start_agent_${agent}.sh" ] && rm "start_agent_${agent}.sh" && echo -e "${YELLOW}  Removed start_agent_${agent}.sh${NC}"
            [ -f "AGENT_${agent^^}_PROMPT.md" ] && rm "AGENT_${agent^^}_PROMPT.md" && echo -e "${YELLOW}  Removed AGENT_${agent^^}_PROMPT.md${NC}"
            [ -f "agent_status/${agent}_status.json" ] && rm "agent_status/${agent}_status.json" && echo -e "${YELLOW}  Removed agent_status/${agent}_status.json${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ Agent generation complete!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "1. Run './coordination_manager.sh init' to initialize the coordination system"
    echo "2. Start agents with './agent_manager.sh auto' or individual startup scripts"
    echo "3. Monitor progress with './coordination_manager.sh watch'"
    echo ""
    echo -e "${CYAN}To change theme or agent count:${NC}"
    echo "  ./agent_theme_manager.py set-theme <theme_id>"
    echo "  ./agent_theme_manager.py set-count <number>"
    echo "  ./generate_agents.sh  # Regenerate agent files"
}

# Run main function
main "$@"