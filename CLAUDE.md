# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Multi-Agent Coordination System designed to orchestrate multiple Claude AI instances working collaboratively on software projects. The system successfully coordinated 6 concurrent agents (Alpha through Zeta) achieving 100% task completion with real-time status tracking and dependency management.

## Key Commands

### Theme and Agent Configuration
```bash
# List available themes (Greek letters, Greek mythology, Marvel, etc.)
./manage_agents.sh themes

# Change theme (e.g., marvel, greek_mythology, vegetables)
./manage_agents.sh set-theme <theme_name>

# Set number of agents (1-24 depending on theme)
./manage_agents.sh set-count <number>

# Generate agent files after theme/count change
./generate_agents.sh

# Show current theme configuration
./agent_theme_manager.py show
```

### Coordination System Management
```bash
# Initialize the coordination system
./coordination_manager.sh init

# Start real-time monitoring dashboard
./coordination_manager.sh watch

# Update agent status
./coordination_manager.sh update <agent> --task "Task Name" --progress 50

# Show all agent statuses
./coordination_manager.sh show-all
```

### Agent Management
```bash
# Start automatic lifecycle management (recommended)
./manage_agents.sh auto

# Manage lifecycle daemon
./manage_agents.sh lifecycle start|stop|restart|status|logs

# Start individual agent manually
./manage_agents.sh start <agent_name>

# List available agents in current theme
./manage_agents.sh list

# Monitor agent dashboard
./agent_manager.sh monitor
```

### Git Worktrees for Parallel Agent Execution (NEW)
```bash
# Create worktrees for all agents
./worktree_manager.sh setup-all

# Create worktree for specific agent
./worktree_manager.sh create <agent_name>

# List all agent worktrees
./worktree_manager.sh list

# Remove agent worktree
./worktree_manager.sh remove <agent_name>

# Sync agent worktree with main branch
./worktree_manager.sh sync <agent_name>
```

Each agent works in their own git worktree:
- **Isolation**: Agents work on separate branches without conflicts
- **Path**: `../agent-<name>` relative to main repository
- **Branch**: `agent/<name>` for each agent
- **Merging**: Changes merged back to main when tasks complete

### Python Status Updates
```bash
# Update agent task and progress
python3 coordination_system/update_agent_status.py <agent> \
  --task "Task Name" \
  --progress 75 \
  --add-activity "Activity description"

# Add/resolve blockers
python3 coordination_system/update_agent_status.py <agent> \
  --add-blocker "Blocker description" \
  --resolve-blocker "Blocker description"

# Update authority information
python3 coordination_system/update_agent_status.py <agent> --update-authority

# Record a decision with authority
python3 coordination_system/update_agent_status.py <agent> \
  --record-decision "ID:Title:Level:Source:Decision:Rationale"
```

## Architecture

### Dynamic Authority System (NEW)
The system implements a flexible, task-based authority model that scales from 1 to 24+ agents:
- **Task-Based Authority**: Authority comes from current assignments, not agent position
- **Dynamic Assignment**: Any agent can hold any authority based on workload and expertise
- **Scalable Design**: Works identically with 1 agent (all authorities) or 24+ agents (distributed)
- **Smart Backup Selection**: Backups chosen by availability and expertise, not position
- **Load Balancing**: Authorities automatically rebalance to prevent bottlenecks
- **No Role Limitations**: Agents adapt to any task type without hardcoded roles

### Git Worktree Integration (NEW)
The system uses git worktrees for true parallel agent execution:
- **One worktree per agent**: Each agent has dedicated workspace at `../agent-<name>`
- **Branch isolation**: Each agent works on `agent/<name>` branch
- **No conflicts**: Agents can modify same files without interference
- **Clean merging**: Agent work merged back via pull requests
- **Automatic setup**: Worktrees created automatically on agent start

### Automatic Lifecycle Management (NEW)
The system now features intelligent agent lifecycle management:
- **Auto-start**: Agents start automatically when dependencies are met and no blockers exist
- **Auto-stop**: Agents stop automatically when they become blocked
- **Health monitoring**: Agents are restarted if they become unresponsive
- **Message routing**: Asynchronous bidirectional communication between agents

### Bidirectional Communication System
Each agent has dedicated communication channels:
```
agent_communication/
├── <agent_name>/
│   ├── input/
│   │   └── inbox.json      # Messages TO the agent
│   ├── output/
│   │   └── outbox.json     # Messages FROM the agent
│   └── status/
│       ├── lifecycle.json  # Running/stopped status
│       └── heartbeat.json  # Health monitoring
```

### Dynamic Agent System
The system supports multiple themes with varying numbers of agents. Agent roles cycle through these 6 standard roles:
1. Critical Path Lead - Senior Developer
2. Migration Specialist - Backend Developer  
3. Dashboard Developer - Fullstack Developer
4. DevOps Engineer
5. Security Engineer
6. UX Engineer - Frontend Developer

### Available Themes
- **greek_letters**: Alpha, Beta, Gamma, Delta, etc. (24 agents)
- **greek_mythology**: Zeus, Hera, Poseidon, Athena, etc. (24 agents)
- **marvel**: Iron Man, Captain America, Thor, etc. (24 agents)
- **vegetables**: Carrot, Broccoli, Spinach, etc. (24 agents)
- **salad_dressings**: Ranch, Caesar, Italian, etc. (24 agents)
- **pasta**: Spaghetti, Penne, Rigatoni, etc. (24 agents)
- **programming_languages**: Python, JavaScript, Java, etc. (24 agents)
- **musical_instruments**: Piano, Guitar, Violin, etc. (24 agents)
- **celestial_bodies**: Mercury, Venus, Earth, etc. (24 agents)
- **colors**: Red, Blue, Green, etc. (24 agents)

### Key Files
- `agent_config.json`: Theme and agent configuration
- `AGENT_COORDINATION.md`: Central coordination hub tracking all agent status
- `AGENT_COORDINATION_MASTER.json`: Machine-readable coordination data
- `agent_status/*.json`: Individual agent status files (names depend on theme)
- `AGENT_*_PROMPT.md`: Agent-specific instructions (names depend on theme)
- `start_agent_*.sh`: Agent startup scripts (generated by theme)
- `DYNAMIC_AUTHORITY_SYSTEM.md`: Flexible authority system documentation
- `authority_pool.json`: Current authority assignments and requests
- `agent_workloads.json`: Real-time agent workload tracking
- `authority_history.json`: Historical record of all authority assignments
- `DECISION_LOG.json`: Master log of all decisions with authority tracking
- `PENDING_DECISIONS.json`: Active decisions awaiting authority
- `EMERGENCY_DECISIONS.md`: Log of emergency authority activations

### Status Tracking System
The system uses Python scripts in `coordination_system/` to:
1. Aggregate individual agent status from JSON files
2. Generate master coordination documents
3. Provide real-time monitoring with change detection
4. Handle inter-agent communication through status updates

### Workflow with Automatic Lifecycle Management

#### Initial Setup
1. Configure theme and agent count
2. Generate agent files with `./generate_agents.sh`
3. Start lifecycle daemon with `./manage_agents.sh auto`

#### Automatic Agent Management
1. Lifecycle daemon monitors agent status files every 10 seconds
2. When agent has no blockers and dependencies are met → Agent starts automatically
3. When agent reports a blocker → Agent stops automatically
4. When blocker is resolved → Agent restarts automatically
5. Agents communicate asynchronously through inbox/outbox files
6. Central dispatcher routes messages between agents

#### Communication Flow
1. Agents poll their inbox every 30 seconds for new messages
2. Agents send heartbeats every 30 seconds
3. Status updates go through both:
   - Legacy status files (for compatibility)
   - New message system (for real-time updates)
4. Blockers reported via messages trigger automatic lifecycle changes

## Development Notes

- No traditional build/test commands - this is a coordination framework
- Shell scripts invoke Claude CLI with specific prompts
- Communication between agents happens through status JSON files
- The system includes security measures for safe file operations
- Real-time monitoring uses file watching for immediate updates

## Git Worktree Workflow Example

```bash
# Setup worktrees for all agents
./worktree_manager.sh setup-all

# Agents work independently in their worktrees:
# - Shark works in ../agent-shark on branch agent/shark
# - Dolphin works in ../agent-dolphin on branch agent/dolphin
# - etc.

# Check worktree status
./worktree_manager.sh list

# When agent completes work:
cd ../agent-shark
git add .
git commit -m "Shark: Completed authentication module"
git push origin agent/shark

# Create PR or merge back to main
cd ../agentCoordination
git merge agent/shark

# Clean up worktree when done
./worktree_manager.sh remove shark
```

## Theme Workflow Example

```bash
# Switch to Marvel theme with 8 agents
./manage_agents.sh set-theme marvel
./manage_agents.sh set-count 8
./generate_agents.sh

# Start the coordination system
./coordination_manager.sh init
./coordination_manager.sh watch  # In another terminal

# Launch automatic lifecycle management
./manage_agents.sh auto

# Agents will automatically:
# - Iron Man starts (no dependencies)
# - When Iron Man completes tasks → dependent agents start
# - If any agent gets blocked → it stops automatically
# - When blocker resolved → agent restarts automatically

# Monitor lifecycle daemon
./manage_agents.sh lifecycle status
tail -f lifecycle_daemon.log
```

## Key Benefits

1. **No Manual Intervention**: Agents start/stop automatically based on real conditions
2. **Efficient Resource Usage**: Only unblocked agents consume resources
3. **Asynchronous Communication**: Agents don't block each other when communicating
4. **Automatic Recovery**: Failed agents are detected and restarted
5. **Scalable**: Supports up to 24 agents per theme