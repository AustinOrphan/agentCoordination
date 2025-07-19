#!/usr/bin/env python3
"""
Initialize the Multi-Agent Coordination System for a new project.
This script sets up the coordination framework with project-specific details.
"""

import json
import os
from datetime import datetime
import argparse
import sys

def init_project(project_name, description=None, deadline=None):
    """Initialize the coordination system for a new project."""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Read agent configuration
    config_path = os.path.join(base_dir, 'agent_config.json')
    with open(config_path, 'r') as f:
        agent_config = json.load(f)
    
    agent_count = agent_config['agent_count']
    current_theme = agent_config.get('current_theme', 'greek_letters')
    theme_data = agent_config['themes'][current_theme]
    theme_name = theme_data['name']
    theme_emoji = theme_data.get('emoji', '🤖')
    agents = theme_data['agents'][:agent_count]
    agent_emojis = theme_data.get('agent_emojis', [])
    
    # Update AGENT_COORDINATION.md
    coordination_md_path = os.path.join(base_dir, 'AGENT_COORDINATION.md')
    start_date = datetime.now().strftime('%Y-%m-%d')
    
    coordination_content = f"""# 🎯 AGENT COORDINATION HUB - {project_name}

## 📋 Project Overview
**Project**: {project_name}
**Description**: {description or 'Multi-agent collaborative development project'}
**Start Date**: {start_date}
**Deadline**: {deadline or 'TBD'}
**Status**: 🟡 IN PROGRESS

## 🤖 Active Agents ({agent_count})
"""
    
    # Add agent sections
    for i, agent_name in enumerate(agents):
        agent_letter = agent_name.upper()
        agent_emoji = agent_emojis[i] if i < len(agent_emojis) else theme_emoji
        coordination_content += f"""
### {agent_emoji} Agent {agent_letter}
- **Status**: 🔵 Ready
- **Current Task**: Awaiting task assignment
- **Progress**: 0%
- **Dependencies**: None
- **Blockers**: None
"""
    
    coordination_content += """
## 📊 Overall Progress
- **Total Progress**: 0%
- **Active Tasks**: 0
- **Completed Tasks**: 0
- **Blocked Tasks**: 0

## 🔄 Recent Updates
- Project initialized and ready for task assignments

## 🎯 Next Steps
1. Define project requirements and milestones
2. Break down work into parallel tasks
3. Assign tasks to agents based on dependencies
4. Start agent lifecycle management
5. Monitor progress through the coordination dashboard
"""
    
    with open(coordination_md_path, 'w') as f:
        f.write(coordination_content)
    
    # Update AGENT_COORDINATION_MASTER.json
    master_json_path = os.path.join(base_dir, 'AGENT_COORDINATION_MASTER.json')
    master_data = {
        "project_name": project_name,
        "project_description": description or "Multi-agent collaborative development project",
        "start_date": start_date,
        "deadline": deadline or "TBD",
        "overall_status": "IN PROGRESS",
        "total_progress": 0,
        "last_update": datetime.now().isoformat(),
        "agents": {}
    }
    
    # Initialize agent data
    for agent_name in agents:
        master_data["agents"][agent_name] = {
            "status": "Ready",
            "current_task": "Awaiting task assignment",
            "progress": 0,
            "dependencies": [],
            "blockers": [],
            "deliverables": [],
            "recent_activities": [
                f"Agent {agent_name.upper()} initialized for {project_name}"
            ]
        }
    
    with open(master_json_path, 'w') as f:
        json.dump(master_data, f, indent=2)
    
    # Create project memory file
    memory_dir = os.path.join(base_dir, 'project_memories')
    os.makedirs(memory_dir, exist_ok=True)
    
    memory_content = f"""# {project_name} - Project Information

## Overview
- **Project**: {project_name}
- **Description**: {description or 'Multi-agent collaborative development project'}
- **Start Date**: {start_date}
- **Deadline**: {deadline or 'TBD'}
- **Framework**: Multi-Agent Coordination System
- **Theme**: {theme_emoji} {theme_name}
- **Active Agents**: {agent_count}

## Agent Assignments
Agents will be assigned tasks based on project requirements.

## Key Commands
- Start lifecycle management: `./manage_agents.sh auto`
- Monitor dashboard: `./coordination_manager.sh watch`
- Update agent status: `./coordination_manager.sh update <agent> --task "Task Name" --progress 50`

## Notes
- This project uses the {theme_name} theme with {agent_count} agents
- Agents will automatically start/stop based on dependencies and blockers
- Use the coordination dashboard to monitor real-time progress
"""
    
    memory_path = os.path.join(memory_dir, f"{project_name.lower().replace(' ', '_')}_info.md")
    with open(memory_path, 'w') as f:
        f.write(memory_content)
    
    print(f"✅ Project '{project_name}' initialized successfully!")
    print(f"{theme_emoji} Theme: {theme_name} with {agent_count} agents")
    print(f"📅 Start Date: {start_date}")
    print(f"📋 Project memory saved to: {memory_path}")
    print("\n🚀 Next steps:")
    print("1. Define and assign tasks to agents")
    print("2. Start the lifecycle daemon: ./manage_agents.sh auto")
    print("3. Monitor progress: ./coordination_manager.sh watch")

def main():
    parser = argparse.ArgumentParser(
        description="Initialize the Multi-Agent Coordination System for a new project"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project"
    )
    parser.add_argument(
        "-d", "--description",
        help="Project description",
        default=None
    )
    parser.add_argument(
        "--deadline",
        help="Project deadline (YYYY-MM-DD format)",
        default=None
    )
    
    args = parser.parse_args()
    
    # Validate deadline format if provided
    if args.deadline:
        try:
            datetime.strptime(args.deadline, '%Y-%m-%d')
        except ValueError:
            print("❌ Error: Deadline must be in YYYY-MM-DD format")
            sys.exit(1)
    
    init_project(args.project_name, args.description, args.deadline)

if __name__ == "__main__":
    main()