# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Multi-Agent Coordination System designed to orchestrate multiple Claude AI instances working collaboratively on software projects. The system supports both single-project and multi-project modes, with global task prioritization across all projects. Successfully tested with 6 concurrent agents achieving 100% task completion with real-time status tracking and dependency management.

## Project Initialization

- Start a project with the Multi-Agent Coordination System using start_project.sh
- Supports both new and existing projects

## Multi-Project Support (NEW)

The system now supports managing multiple projects simultaneously with global task prioritization:

### Multi-Project Commands
```bash
# Create a new project
./project_manager.sh create "Project Name" /path/to/code -d "Description" -a 8

# Set global priority mode (recommended)
./project_manager.sh pool mode global_priority

# Set project priority (0.1-2.0, higher = more urgent)
./project_manager.sh pool priority "Project Name" 1.8

# Process global task assignments
./project_manager.sh pool assign

# Monitor all projects
./project_manager.sh monitor

# See full multi-project guide
cat MULTI_PROJECT_GUIDE.md
```

### Project Reset Commands (NEW)
```bash
# Reset a test project (instant, no confirmation needed)
./project_manager.sh reset "Test Project Name"

# Reset a production project (requires confirmation and challenge)
./project_manager.sh reset "Production Project" --confirm

# Mark a project as a test project (requires --confirm for production)
./project_manager.sh mark-test "Project Name" --confirm

# Reset all test projects at once
./project_manager.sh reset-tests

# See full reset guide
cat PROJECT_RESET_GUIDE.md
```

**Safety Features:**
- Test projects (containing "test" in name or marked as test) reset instantly
- Production projects require `--confirm` flag and challenge-response for reset
- Marking production projects as test requires `--confirm` flag and warning
- Challenge types include typing project name in uppercase, project ID, or specific phrases
- All reset operations preserve project structure but clear data

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
./development/agent_theme_manager.py show
```

### Task Assignment and Management (NEW)
```bash
# Create sample tasks for testing
python3 coordination_system/task_communicator.py --create-samples

# Process task assignments manually
python3 coordination_system/task_communicator.py --process

# Check task queue status
python3 coordination_system/task_assignment_manager.py --status

# View agent workloads
python3 coordination_system/task_assignment_manager.py --workloads
```

### Enhanced Lifecycle Management with Task Assignment
The lifecycle daemon now includes integrated task assignment:
- **Automatic Task Assignment**: Tasks are assigned to agents based on their roles and capabilities
- **Smart Agent Startup**: Agents automatically start when they have tasks assigned
- **Load Balancing**: Tasks distributed evenly across available agents
- **Priority Handling**: Critical tasks get assigned and processed first
- **Competency-Based Assignment**: Tasks matched to agents with highest competency scores

To start the enhanced lifecycle daemon:
```bash
./manage_agents.sh auto
# or
./lifecycle_daemon.sh start
```

## Session Learnings (2025-07-23)

### File Organization After Cleanup
During this session, I discovered that many key files were relocated during a codebase cleanup:
- **Theme Manager**: `agent_theme_manager.py` → `development/agent_theme_manager.py`
- **Status Scripts**: `update_agent_status.py`, `enhanced_status_aggregator.py` remain in `coordination_system/`
- **Agent Prompts**: Moved to `archive/` but symlinked back to root directory for backward compatibility
- **Documentation**: Consolidated into `docs/` folder with root symlinks

### Path Resolution Issues Fixed
Several hardcoded paths needed updating after the file reorganization:
1. **Config Path**: Changed from `../agent_config.json` to `runtime/agent_config.json` in enhanced_status_aggregator.py
2. **Shell Scripts**: Updated THEME_MANAGER variable in multiple scripts to point to `development/` folder
3. **Symbolic Links**: Created for CLAUDE.md and AGENT_*_PROMPT.md files to maintain compatibility

### Shell Compatibility Fixes
1. **Grep Errors**: Agent startup showed repetitive "grep: invalid repetition count(s)" errors
   - Caused by oh-my-zsh plugins with invalid regex patterns
   - Fixed by using `exec /bin/bash -c` instead of direct shell invocation in startup scripts
   - Redirected stderr with `2>/dev/null` to suppress cosmetic errors

2. **Bash Syntax**: `${variable^^}` syntax not portable across shell versions
   - Replaced with `$(echo "$variable" | tr '[:lower:]' '[:upper:]')`
   - Updated in manage_agents.sh, generate_agents_dynamic.sh, and generate_agents_with_plans.sh

### Migration Analysis Import Fix
The migration_cli.py had relative import issues when run as a script:
```python
# Fixed by adding try/except blocks:
try:
    from .migration_analyzer import MigrationAnalyzer
except ImportError:
    from migration_analyzer import MigrationAnalyzer
```
Applied same fix to migration_workflows.py for robustness.

### Key Testing Commands
```bash
# Verify theme switching
./manage_agents.sh set-theme marvel
./manage_agents.sh set-count 6
./generate_agents.sh

# Test agent workflow
./worktree_manager.sh create shark
./start_agent_shark.sh  # Opens Claude Code in agent worktree

# Migration analysis
python3 coordination_system/migration_cli.py analyze .
python3 coordination_system/migration_cli.py workflow --type monolith_to_microservices --complexity high
```

[... rest of the existing content remains unchanged ...]