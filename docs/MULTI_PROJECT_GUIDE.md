# Multi-Project Coordination System Guide

## Overview

The Multi-Project Coordination System enables you to manage multiple software projects simultaneously from a centralized point. Agents are dynamically assigned to tasks across all projects based on global priority, ensuring optimal resource utilization.

## Key Features

### 1. **Project Isolation**
- Each project has its own isolated workspace
- Separate agent status, communication channels, and task queues
- Projects maintain their own git worktrees and configurations

### 2. **Global Priority Pool Mode**
- Tasks from ALL projects are ranked by priority
- Agents are assigned to highest priority tasks regardless of project
- Project-level priority multipliers (0.1-2.0) for fine-grained control
- Automatic rebalancing as tasks complete

### 3. **Flexible Agent Assignment**
- **Global Priority Mode**: Agents work on any project based on task priority
- **Project Dedicated Mode**: Agents assigned to specific projects
- **Hybrid Mode**: Mix of dedicated and pool agents

## Quick Start

### 1. Create Your First Multi-Project Setup

```bash
# Create a new project
./project_manager.sh create "Web App" ~/projects/webapp -d "E-commerce platform" -a 8

# Or integrate an existing project
./project_manager.sh existing ~/projects/existing-app -n "Legacy System"
```

### 2. Configure Global Task Pool

```bash
# Set to global priority mode (recommended)
./project_manager.sh pool mode global_priority

# Set project priority (higher = more urgent)
./project_manager.sh pool priority "Web App" 1.8
./project_manager.sh pool priority "Mobile App" 1.0
./project_manager.sh pool priority "Backend API" 0.5
```

### 3. Start the System

```bash
# Process global task assignments
./project_manager.sh pool assign

# Start the lifecycle daemon
./manage_agents.sh auto

# Monitor progress
./project_manager.sh monitor
```

## Project Management Commands

### Creating Projects

```bash
# New project with all options
./project_manager.sh create "Project Name" /path/to/code \
    -d "Description" \
    -a 8               # Number of agents
    -t ocean_creatures # Agent theme

# Existing project
./project_manager.sh existing /path/to/project \
    -n "Custom Name" \
    --deadline 2024-03-15
```

### Managing Projects

```bash
# List all projects
./project_manager.sh list
./project_manager.sh list --status active

# Project information
./project_manager.sh info "Project Name"
./project_manager.sh stats "Project Name"

# Project lifecycle
./project_manager.sh start "Project Name"
./project_manager.sh pause "Project Name"
./project_manager.sh resume "Project Name"
./project_manager.sh stop "Project Name"
./project_manager.sh archive "Project Name"

# Delete project (requires confirmation)
./project_manager.sh delete "Project Name" --confirm
```

### Import/Export Projects

```bash
# Export project configuration
./project_manager.sh export "Project Name" -o project_backup.json

# Import project configuration
./project_manager.sh import project_backup.json --codebase /new/path
```

## Global Task Pool Management

### Pool Modes

1. **global_priority** (Recommended)
   - All tasks from all projects in single priority queue
   - Agents assigned based on global task priority
   - Best for maximizing throughput

2. **project_dedicated**
   - Agents assigned to specific projects
   - Tasks stay within project boundaries
   - Best for project isolation

3. **hybrid**
   - Some agents dedicated, others in shared pool
   - Balance between isolation and flexibility

### Pool Commands

```bash
# Set pool mode
./project_manager.sh pool mode global_priority

# Set project priority multiplier (0.1-2.0)
./project_manager.sh pool priority "Critical Project" 2.0
./project_manager.sh pool priority "Maintenance Project" 0.3

# View global task queue
./project_manager.sh pool queue
./project_manager.sh pool queue --project "Web App"

# Process assignments (assigns tasks to agents)
./project_manager.sh pool assign

# View pool summary
./project_manager.sh pool summary
```

## Task Priority System

### Task Priorities
- **CRITICAL** (1000 base score)
- **HIGH** (100 base score)
- **NORMAL** (10 base score)
- **LOW** (1 base score)

### Global Score Calculation
```
Global Score = Task Priority × Project Priority × Age Factor × Dependency Factor
```

### Example Scenarios

1. **Urgent Project with Critical Bug**
   - Task: CRITICAL (1000) × Project: 1.8 = Score: 1800
   - Gets assigned immediately

2. **Normal Project with Feature Request**
   - Task: NORMAL (10) × Project: 1.0 = Score: 10
   - Waits for higher priority tasks

3. **Low Priority Maintenance**
   - Task: LOW (1) × Project: 0.5 = Score: 0.5
   - Only assigned when no other work

## Project Workspace Structure

Each project maintains isolated workspace:

```
projects/
├── proj_abc123/                    # Project ID
│   ├── config.json                 # Project configuration
│   ├── agent_status/               # Agent status files
│   │   ├── agent_1_status.json
│   │   └── agent_2_status.json
│   ├── agent_communication/        # Communication channels
│   │   ├── agent_1/
│   │   └── agent_2/
│   ├── task_assignments/           # Task queues
│   │   └── task_queue.json
│   ├── agent_prompts/             # Generated prompts
│   ├── worktrees/                 # Git worktrees
│   └── logs/                      # Project logs
└── proj_def456/                   # Another project
```

## Monitoring and Debugging

### Real-time Monitoring
```bash
# Monitor all projects
./project_manager.sh monitor

# Monitor specific project
./project_manager.sh monitor "Web App"

# System status
./project_manager.sh status
```

### Lifecycle Daemon
```bash
# Check daemon status
./lifecycle_daemon.sh status

# View logs
./lifecycle_daemon.sh logs
tail -f lifecycle_daemon.log

# Restart daemon
./lifecycle_daemon.sh restart
```

### Debugging Commands
```bash
# Check global assignments
cat coordination_system/global_assignments.json

# View pool configuration
cat coordination_system/global_pool_config.json

# Project-specific logs
cat projects/proj_*/logs/activity.log
```

## Best Practices

### 1. **Project Priority Guidelines**
- **2.0**: Critical/Emergency projects
- **1.5-1.8**: High priority with deadlines
- **1.0**: Normal priority
- **0.5-0.8**: Maintenance/Low priority
- **0.1-0.4**: Background/Research projects

### 2. **Task Organization**
- Use CRITICAL sparingly (production issues only)
- Set realistic estimated_hours for better scheduling
- Use dependencies to enforce task order
- Tag tasks for better categorization

### 3. **Agent Management**
- Start with `global_priority` mode
- Use 6-12 agents per project for balance
- Monitor agent utilization regularly
- Let lifecycle daemon handle start/stop

### 4. **Scaling Considerations**
- System handles up to 10 concurrent projects well
- Each project can have 1-24 agents
- Global pool can manage 100+ agents
- Task queue performs well up to 1000 tasks

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Create Project in Coordination System
  run: |
    ./project_manager.sh create "${{ github.event.repository.name }}" . \
      -d "Auto-created from GitHub" \
      -a 6
```

### Deployment Plans
```bash
# Auto-detect deployment plans
./project_manager.sh existing /project/path

# Plans detected in:
# - deployment-plans/
# - plans/
# - .deploy/
```

## Troubleshooting

### Common Issues

1. **"No agents starting"**
   - Check pool mode: `./project_manager.sh pool summary`
   - Verify tasks exist: `./project_manager.sh pool queue`
   - Run assignment: `./project_manager.sh pool assign`

2. **"Tasks not being assigned"**
   - Check project priority isn't too low
   - Verify task dependencies are met
   - Ensure lifecycle daemon is running

3. **"Agent communication failing"**
   - Check project workspace exists
   - Verify agent_communication directories
   - Restart lifecycle daemon

### Reset Commands
```bash
# Reset global pool
rm coordination_system/global_pool_config.json
rm coordination_system/global_assignments.json

# Reset project
./project_manager.sh pause "Project"
./project_manager.sh resume "Project"

# Full system restart
./lifecycle_daemon.sh stop
./manage_agents.sh lifecycle stop
./manage_agents.sh auto
```

## Example: Running Multiple Projects

See `multi_project_demo.sh` for a complete example:

```bash
# Run the demo
./multi_project_demo.sh

# This will:
# 1. Create 3 projects with different priorities
# 2. Set up global task pool
# 3. Create sample tasks
# 4. Show task prioritization
# 5. Assign agents globally
```

## Architecture

### Components

1. **ProjectManager** (`project_manager.py`)
   - Manages project lifecycles
   - Maintains project isolation
   - Handles configuration

2. **GlobalTaskPoolManager** (`global_task_pool.py`)
   - Implements global priority queue
   - Calculates task scores
   - Assigns agents optimally

3. **ProjectLifecycleManager** (`project_lifecycle_manager.py`)
   - Project-aware agent lifecycle
   - Integrates with global pool
   - Manages cross-project agents

4. **Project CLI** (`project_manager.sh`)
   - User-friendly interface
   - Wraps Python components
   - Provides monitoring

## Future Enhancements

- [ ] Web dashboard for multi-project monitoring
- [ ] Agent performance metrics per project
- [ ] Task estimation accuracy tracking
- [ ] Project templates for common patterns
- [ ] Integration with more CI/CD platforms
- [ ] Real-time task rebalancing
- [ ] Agent expertise tracking
- [ ] Project cost allocation

## Summary

The Multi-Project Coordination System brings enterprise-grade project management to your AI agent coordination. By prioritizing tasks globally across all projects, you ensure that your most critical work gets done first, while maintaining project isolation and tracking.

Start with `./multi_project_demo.sh` to see it in action!