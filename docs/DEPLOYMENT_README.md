# Multi-Agent Coordination System - Deployment Guide

A comprehensive guide for deploying the Multi-Agent Coordination System on any software project.

## Overview

The Multi-Agent Coordination System orchestrates multiple Claude AI instances working collaboratively on software projects. The system supports 1-24+ agents with dynamic authority management, real-time coordination, and parallel execution through git worktrees.

**NEW**: The system now supports **external deployment plans** in Markdown, XML, and JSON formats, allowing you to integrate existing project workflows with the dynamic agent coordination system.

## Quick Start

### Interactive Mode (Default)

Simply run:
```bash
./start_project.sh
```

The interactive setup will guide you through:
- Choosing new or existing project
- Setting project name and details
- Auto-detecting deployment plans
- Configuring optional deadline
- Starting agents automatically

### Command Line Mode

For **existing projects**:
```bash
./start_project.sh existing /path/to/your/project -n "Your Project Name"
```

For **new projects**:
```bash
./start_project.sh new "Your Project Name" -d "Project description"
```

For **projects with external deployment plans**:
```bash
# Plans are auto-detected in deployment-plans/ or plans/ directories
./start_project.sh existing /path/to/your/project -n "Your Project Name"

# Or specify custom plan location
./start_project.sh existing /path/to/your/project --plans /path/to/deployment-plans -n "Your Project Name"
```

**Note**: Deadline is always optional in both interactive and command line modes.

That's it! The system will automatically:
- ✅ Analyze your project structure
- ✅ Parse external deployment plans (MD/XML/JSON)
- ✅ Initialize coordination system  
- ✅ Generate enhanced agent files with specialized assignments
- ✅ Start lifecycle management
- ✅ Open monitoring dashboard

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or WSL2
- **Python**: 3.8+
- **Git**: 2.28+ (for worktree support)
- **Claude CLI**: Latest version
- **Disk Space**: ~100MB + project size × agent count

### Dependencies
```bash
# Install Python dependencies
pip install -r requirements-test.txt

# Ensure git worktree support
git --version  # Should be 2.28+
```

## Manual Deployment

If you need more control over the deployment process:

### 1. Initialize Coordination System
```bash
./coordination_manager.sh init
```

### 2. Configure Agent Theme & Count
```bash
# Choose from available themes
./manage_agents.sh themes

# Set theme and agent count (1-24 depending on theme)
./manage_agents.sh set-theme greek_letters
./manage_agents.sh set-count 6

# View current configuration
./agent_theme_manager.py show
```

### 3. Generate Agent Files
```bash
# Generate dynamic agent files (recommended)
./generate_agents_dynamic.sh

# Generate agents with external deployment plans (enhanced)
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# OR generate theme-specific files
./generate_agents.sh
```

### 4. Set Up Git Worktrees
```bash
# Create isolated workspaces for all agents
./worktree_manager.sh setup-all

# Verify setup
./worktree_manager.sh list
```

### 5. Start Coordination System
```bash
# Start automatic lifecycle management
./manage_agents.sh auto

# Start monitoring dashboard (in separate terminal)
./coordination_manager.sh watch
```

## Available Themes

The system supports multiple agent themes with varying numbers of agents:

| Theme | Agent Count | Examples |
|-------|-------------|----------|
| `greek_letters` | 24 | Alpha, Beta, Gamma, Delta... |
| `greek_mythology` | 24 | Zeus, Hera, Poseidon, Athena... |
| `marvel` | 24 | Iron Man, Captain America, Thor... |
| `ocean_creatures` | 24 | Shark, Dolphin, Whale, Octopus... |
| `programming_languages` | 24 | Python, JavaScript, Java, TypeScript... |
| `nato_phonetic` | 26 | Alpha, Bravo, Charlie, Delta... |

**View all themes:**
```bash
./manage_agents.sh themes
```

## System Architecture

### Dynamic Authority System
- **Task-Based Authority**: Authority assigned based on current work, not agent position
- **Automatic Rebalancing**: Prevents bottlenecks by redistributing workload
- **Emergency Protocols**: Agents can assume emergency authority when needed
- **Scalable Design**: Works identically with 1 agent or 24+ agents

### Agent Communication
Each agent has dedicated communication channels:
```
agent_communication/
├── <agent_name>/
│   ├── input/inbox.json      # Messages TO the agent
│   ├── output/outbox.json    # Messages FROM the agent
│   └── status/lifecycle.json # Agent lifecycle status
```

### Git Worktree Integration (Enhanced)
- **Parallel Execution**: Each agent works in isolated git worktree
- **No Conflicts**: Agents can modify same files simultaneously
- **Branch Isolation**: Each agent works on `agent/<name>` branch
- **Clean Merging**: Changes merged back via pull requests
- **Worktree Locking**: Prevent accidental removal of active worktrees
- **Health Monitoring**: Automatic detection and repair of corrupted worktrees
- **Configuration Isolation**: Agent-specific git configs per worktree

## Agent Management

### Lifecycle Management
```bash
# Start automatic lifecycle management
./manage_agents.sh auto

# Manual agent control
./manage_agents.sh start <agent_name>
./manage_agents.sh stop <agent_name>
./manage_agents.sh restart <agent_name>

# Check daemon status
./manage_agents.sh lifecycle status
./manage_agents.sh lifecycle logs
```

### Status Updates
```bash
# Update agent status
./coordination_manager.sh update <agent> --task "Task Name" --progress 75

# Python status updates
python3 coordination_system/update_agent_status.py <agent> \
  --task "Current task" \
  --progress 50 \
  --add-activity "Working on feature X"
```

### Monitoring
```bash
# Real-time dashboard
./coordination_manager.sh watch

# View all agent statuses
./coordination_manager.sh show-all

# Check specific agent
cat agent_status/<agent>_status.json
```

## Project Integration

### For Existing Projects

The system analyzes your project and creates appropriate agent assignments:

```bash
./start_project.sh existing /path/to/project
```

**What gets analyzed:**
- File structure and technologies
- Dependencies and build systems
- Documentation and testing frameworks
- Git history and development patterns

### For Projects with External Deployment Plans

Integrate existing deployment workflows with the coordination system:

```bash
./start_project.sh existing /path/to/project --plans /path/to/deployment-plans
```

**Supported plan formats:**
- **Markdown (.md)**: Human-readable deployment instructions
- **XML (.xml)**: Structured deployment definitions
- **JSON (.json)**: Machine-readable deployment specifications

**What gets integrated:**
- Agent role assignments from plans
- Specialized responsibilities and tasks
- Success criteria and timelines
- Dependencies and coordination requirements

### For New Projects

```bash
./start_project.sh new "Project Name" -d "Description" --deadline 2025-12-31
```

**What gets created:**
- Project structure recommendations
- Agent role assignments
- Development workflow setup
- Coordination protocols

### Custom Agent Instructions

After deployment, customize agent behavior by editing:
- `AGENT_*_PROMPT.md` - Agent-specific instructions (enhanced with plan content if using external plans)
- `agent_workloads.json` - Workload distribution
- `authority_pool.json` - Authority assignments

### Plan Integration Options

```bash
# Standard dynamic agents (no external plans)
./generate_agents_dynamic.sh

# Enhanced agents with external deployment plans
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# Test plan integration without making changes
./generate_agents_with_plans.sh --plans /path/to/plans --dry-run

# Direct plan integration (advanced)
python3 plan_integrator.py /path/to/deployment-plans --agent-count 6
```

## Command Reference

### Core Commands
```bash
# Project initialization
./start_project.sh [new|existing] [options]

# Coordination management  
./coordination_manager.sh [init|watch|update|show-all]

# Agent lifecycle
./manage_agents.sh [auto|start|stop|restart|list|themes]

# Git worktrees (enhanced)
./worktree_manager_enhanced.sh [setup-all|create|remove|list|sync|lock|unlock|repair|health-check]

# Theme management
./agent_theme_manager.py [show|set-theme|set-count|get-agents]
```

### System Utilities
```bash
# Generate agent files
./generate_agents_dynamic.sh              # Dynamic (recommended)
./generate_agents_with_plans.sh --plans   # Dynamic with external plans (NEW)
./generate_agents.sh                      # Theme-specific

# Plan integration
python3 plan_integrator.py /path/to/plans # Direct plan parsing and integration

# Test system
pytest                         # All tests
pytest -m integration         # Integration tests only
pytest tests/stress/           # Stress tests

# Code quality
black . && isort . && flake8   # Format and lint
```

## Testing and Validation

### Built-in Test Suite
```bash
# Run comprehensive test suite (100% success rate)
pytest --cov=coordination_system --cov-report=html

# Test categories
pytest -m unit                # Unit tests
pytest -m integration         # Integration tests  
pytest -m e2e                 # End-to-end tests
pytest tests/stress/           # Performance/stress tests
```

### Validation Levels
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-agent coordination testing
- **BDD Tests**: 60+ edge case scenarios
- **Stress Tests**: 1-24 agent scaling validation

## Configuration

### Agent Configuration (`agent_config.json`)
```json
{
  "current_theme": "programming_languages",
  "agent_count": 6,
  "themes": { ... }
}
```

### System Settings
- **Max Agents**: 24 per theme
- **Communication Interval**: 30 seconds
- **Status Update Frequency**: Real-time
- **Git Worktree Location**: `../agent-<name>/`

## Troubleshooting

### Common Issues

**Agents not starting:**
```bash
# Check lifecycle daemon
./manage_agents.sh lifecycle status

# Restart daemon
./manage_agents.sh lifecycle restart

# Check logs
tail -f lifecycle_daemon.log
```

**Git worktree conflicts:**
```bash
# Check worktree health
./worktree_manager_enhanced.sh health-check

# Repair corrupted worktree
./worktree_manager_enhanced.sh repair <agent>

# Remove stuck worktree (with safety checks)
./worktree_manager_enhanced.sh remove <agent>

# Force remove if necessary
./worktree_manager_enhanced.sh remove <agent> --force

# List all worktrees with detailed status
./worktree_manager_enhanced.sh list
```

**Communication issues:**
```bash
# Check communication channels
ls -la agent_communication/

# Reset communication system
python3 coordination_system/agent_communication.py --reset
```

**Authority conflicts:**
```bash
# Check authority pool
cat authority_pool.json

# Rebalance authorities
python3 coordination_system/dynamic_authority_manager.py --rebalance
```

### Performance Optimization

**For large projects (1000+ files):**
```bash
# Increase agent count
./manage_agents.sh set-count 12

# Use performance theme
./manage_agents.sh set-theme programming_languages
```

**For resource-constrained environments:**
```bash
# Reduce agent count
./manage_agents.sh set-count 3

# Disable real-time monitoring
./start_project.sh --no-watch
```

## Git Worktree Best Practices

### Parallel Claude Code Sessions

Based on [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees), the system supports true parallel agent execution:

**Key Benefits:**
- Each agent runs in a completely isolated environment
- No merge conflicts between concurrent agents
- Agents can work on the same files simultaneously
- Clean integration through pull requests

### Enhanced Worktree Management

The enhanced worktree manager provides advanced features based on [Git worktree documentation](https://git-scm.com/docs/git-worktree):

**Worktree Locking:**
```bash
# Lock worktree to prevent accidental removal
./worktree_manager_enhanced.sh lock <agent> "Critical work in progress"

# Unlock when ready
./worktree_manager_enhanced.sh unlock <agent>
```

**Health Monitoring:**
```bash
# Check all worktrees for issues
./worktree_manager_enhanced.sh health-check

# Repair corrupted worktree
./worktree_manager_enhanced.sh repair <agent>

# Clean up stale references
./worktree_manager_enhanced.sh prune
```

**Worktree Configuration:**
```bash
# Set agent-specific git config
./worktree_manager_enhanced.sh config <agent>

# Each agent gets:
# - Custom user.name: "Agent <name>"
# - Custom user.email: "agent-<name>@coordination.local"
# - Isolated configuration settings
```

### Safe Worktree Operations

**Before Removing:**
The enhanced manager checks for:
- Uncommitted changes
- Unpushed commits
- Lock status
- Stale references

**Sync Strategies:**
```bash
# Merge strategy (default)
./worktree_manager_enhanced.sh sync <agent>

# Rebase strategy
./worktree_manager_enhanced.sh sync <agent> rebase
```

### Parallel Workflow Example

```bash
# 1. Setup worktrees for all agents
./worktree_manager_enhanced.sh setup-all

# 2. Health check before starting
./worktree_manager_enhanced.sh health-check

# 3. Lock critical agent worktrees
./worktree_manager_enhanced.sh lock shark "Production deployment"

# 4. Agents work independently
# - Each agent modifies files in their worktree
# - No conflicts even on same files
# - Changes isolated to agent branches

# 5. Check detailed status
./worktree_manager_enhanced.sh status shark

# 6. Sync with main when ready
./worktree_manager_enhanced.sh sync shark

# 7. Unlock and clean up
./worktree_manager_enhanced.sh unlock shark
```

## Advanced Usage

### Custom Themes
Create custom themes by editing `agent_config.json`:
```json
{
  "custom_theme": {
    "name": "My Theme",
    "emoji": "🎯",
    "agents": ["agent1", "agent2", "agent3"],
    "agent_emojis": ["🔥", "⚡", "🚀"]
  }
}
```

### Emergency Procedures
```bash
# Emergency stop all agents
./manage_agents.sh emergency-stop

# Rollback to last stable state
git checkout main
./coordination_manager.sh rollback

# Recovery procedures
./manage_agents.sh recovery-mode
```

### Integration with CI/CD
```bash
# In your CI pipeline
./start_project.sh existing . --no-watch --no-auto
pytest tests/
./coordination_manager.sh validate-completion
```

## Performance Metrics

### Expected Performance
- **Startup Time**: 30 seconds - 2 minutes
- **Agent Coordination Overhead**: <5% CPU
- **Memory Usage**: ~50MB per agent
- **Disk Usage**: ~10MB per agent worktree

### Scaling Characteristics
- **1-6 agents**: Optimal for most projects
- **7-12 agents**: Large/complex projects
- **13-24 agents**: Enterprise/massive codebases

## Security Considerations

- **File Access**: Agents operate within project boundaries
- **Network Access**: Limited to project-related APIs
- **Authority Validation**: All actions require appropriate authority
- **Emergency Protocols**: Built-in safety mechanisms

## Support and Documentation

### Key Documentation Files
- `CLAUDE.md` - Complete system reference
- `DYNAMIC_AUTHORITY_SYSTEM.md` - Authority system details
- `PLAN_INTEGRATION_GUIDE.md` - External deployment plan integration
- `PARALLEL_SESSION_GUIDE.md` - Git worktree parallel execution guide (NEW)
- `coordination_system/PROJECT_SETUP_GUIDE.md` - Setup guide
- `docs/TEST_SUITE_DOCUMENTATION.md` - Testing documentation

### Getting Help
1. Check system logs: `tail -f coordination_system.log`
2. Review agent status: `./coordination_manager.sh show-all`
3. Run diagnostics: `python3 coordination_system/diagnostics.py`

---

## Quick Reference

### Essential Commands
```bash
# Deploy on existing project
./start_project.sh existing /path/to/project

# Deploy with external deployment plans (NEW)
./start_project.sh existing /path/to/project --plans /path/to/deployment-plans

# Deploy new project  
./start_project.sh new "Project Name"

# Generate agents with external plans (NEW)
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# Monitor system
./coordination_manager.sh watch

# Check status
./coordination_manager.sh show-all

# Stop system
./manage_agents.sh lifecycle stop
```

### Project Structure After Deployment
```
your-project/
├── agentCoordination/           # Coordination system
├── agent-alpha/                 # Agent Alpha worktree  
├── agent-beta/                  # Agent Beta worktree
└── agent-gamma/                 # Agent Gamma worktree
```

**Success Indicator**: All agents show "🟢 Active" status in the monitoring dashboard.