# Coordination System Cleaning Guide

## Overview

The coordination system can accumulate project-specific data over time. This guide explains how to reset the system to a project-agnostic state, ready for a new project.

## What Gets Cleaned

### 1. **Status Files**
- `AGENT_COORDINATION.md` - Reset to template with placeholders
- `AGENT_COORDINATION_MASTER.json` - Reset with all agents in "ready" state
- `agent_status/*.json` - Individual agent status files reset to initial state

### 2. **Log Files**
- `coordination_system/agent_updates.log` - Cleared
- `coordination_system/coordination_manager.log` - Cleared
- `coordination_system/coordination_system.log` - Cleared

### 3. **Communication Channels** (if present)
- `agent_communication/*/input/inbox.json` - Cleared
- `agent_communication/*/output/outbox.json` - Cleared
- `agent_communication/*/status/lifecycle.json` - Reset to "stopped"

## How to Clean

### Automatic Cleaning

Use the provided cleaning script:

```bash
cd /path/to/agentCoordination
python3 clean_coordination_system.py
```

The script will:
1. Reset all agent status files to "Awaiting task assignment"
2. Create a project-agnostic AGENT_COORDINATION.md template
3. Reset AGENT_COORDINATION_MASTER.json
4. Clear all log files
5. Reset agent communication channels (if present)

### Manual Cleaning

If you prefer to clean manually:

1. **Reset Agent Status Files:**
   - Navigate to `agent_status/` directory
   - Edit each `*_status.json` file to reset task, progress, and activities

2. **Reset Coordination Documents:**
   - Replace AGENT_COORDINATION.md with the template
   - Reset AGENT_COORDINATION_MASTER.json

3. **Clear Logs:**
   - Delete or empty files in `coordination_system/` directory

## After Cleaning

1. **Update Project Details:**
   - Edit AGENT_COORDINATION.md to add your project name and start date
   - Update the project objectives and initial tasks

2. **Assign Tasks:**
   - Use the update scripts to assign tasks to agents:
     ```bash
     python3 coordination_system/update_agent_status.py alpha \
       --task "Your first task" \
       --progress 0
     ```

3. **Start Monitoring:**
   - Launch the coordination manager:
     ```bash
     ./coordination_manager.sh watch
     ```

4. **Launch Agents:**
   - Start agents as needed for your project:
     ```bash
     ./manage_agents.sh start alpha
     ```

## Project-Specific Data to Note

When cleaning, be aware that these items contain project-specific data:
- Task descriptions and progress
- Completed activities and deliverables
- Decision logs and blockers
- Cross-agent communication history
- Dependencies and integration points
- Daily standup notes
- Milestone schedules

All of these are reset to generic placeholders during cleaning.

## Best Practices

1. **Archive Before Cleaning:** Consider backing up the current state before cleaning if you need to reference it later
2. **Document Lessons Learned:** Extract any valuable insights from the previous project before cleaning
3. **Clean Between Projects:** Always clean the system between different projects to avoid confusion
4. **Verify Clean State:** After cleaning, verify that all files show "Awaiting task assignment" status