#!/usr/bin/env python3
"""
Initialize the Multi-Agent Coordination System for an existing project.
This uses the analysis from analyze_existing_project.py to set up agents with appropriate tasks.
"""

import json
import os
from datetime import datetime, timedelta
import argparse
import sys
from pathlib import Path

def init_from_analysis(analysis_file, custom_name=None, deadline=None):
    """Initialize coordination system from project analysis."""
    
    # Load analysis
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Read agent configuration
    config_path = os.path.join(base_dir, 'agent_config.json')
    with open(config_path, 'r') as f:
        agent_config = json.load(f)
    
    agent_count = agent_config['agent_count']
    theme = agent_config['theme']
    agents = agent_config['agents'][:agent_count]
    
    # Use custom name or derive from analysis
    project_name = custom_name or analysis['project_info']['name']
    project_path = analysis['project_info']['path']
    
    # Create project description
    tech_stack = []
    if analysis['technologies']['languages']:
        tech_stack.append(f"{', '.join(analysis['technologies']['languages'][:3])}")
    if analysis['technologies']['frameworks']:
        tech_stack.append(f"{', '.join(analysis['technologies']['frameworks'][:2])}")
    
    description = f"Improving existing {' + '.join(tech_stack)} project at {project_path}"
    
    # Calculate deadline if not provided
    if not deadline:
        # Estimate based on number of high priority tasks
        high_priority_tasks = sum(1 for task in analysis['suggested_tasks'] if task['priority'] == 'high')
        medium_priority_tasks = sum(1 for task in analysis['suggested_tasks'] if task['priority'] == 'medium')
        
        # Rough estimate: 1 week per 3 high priority tasks, 1 week per 5 medium priority tasks
        estimated_weeks = (high_priority_tasks / 3) + (medium_priority_tasks / 5)
        estimated_weeks = max(2, min(12, int(estimated_weeks)))  # Between 2-12 weeks
        
        deadline_date = datetime.now() + timedelta(weeks=estimated_weeks)
        deadline = deadline_date.strftime('%Y-%m-%d')
    
    # Update AGENT_COORDINATION.md
    coordination_md_path = os.path.join(base_dir, 'AGENT_COORDINATION.md')
    start_date = datetime.now().strftime('%Y-%m-%d')
    
    # Generate quality summary
    quality = analysis['quality_metrics']
    quality_summary = []
    quality_summary.append(f"- Tests: {'✅' if quality['has_tests'] else '❌'}")
    quality_summary.append(f"- CI/CD: {'✅' if quality['has_ci'] else '❌'}")
    quality_summary.append(f"- Linting: {'✅' if quality['has_linting'] else '❌'}")
    quality_summary.append(f"- Docs: {'✅' if quality['has_documentation'] else '❌'}")
    
    coordination_content = f"""# 🎯 AGENT COORDINATION HUB - {project_name}

## 📋 Project Overview
**Project**: {project_name}
**Type**: Existing Project Enhancement
**Path**: {project_path}
**Description**: {description}
**Start Date**: {start_date}
**Deadline**: {deadline}
**Status**: 🟡 IN PROGRESS

## 📊 Project Analysis Summary
**Technologies**: {', '.join(analysis['technologies']['languages'][:3])} | {', '.join(analysis['technologies']['frameworks'][:3])}
**Size**: {analysis['project_info']['total_files']:,} files ({analysis['project_info']['total_size_mb']} MB)
**Quality Metrics**:
{chr(10).join(quality_summary)}
**Improvement Areas**: {len(analysis['improvements'])} identified
**Suggested Tasks**: {len(analysis['suggested_tasks'])} generated

## 🤖 Active Agents ({agent_count})
"""
    
    # Agent role mapping
    agent_roles = [
        "Critical Path Lead - Senior Developer",
        "Migration Specialist - Backend Developer",
        "Dashboard Developer - Fullstack Developer",
        "DevOps Engineer",
        "Security Engineer",
        "UX Engineer - Frontend Developer"
    ]
    
    # Assign tasks to agents
    agent_tasks = {}
    task_assignments = []
    
    # Sort tasks by priority
    sorted_tasks = sorted(analysis['suggested_tasks'], 
                         key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 3))
    
    # Distribute tasks among agents
    for i, agent_name in enumerate(agents):
        agent_letter = agent_name.upper()
        role = agent_roles[i % len(agent_roles)]
        
        # Find tasks for this agent's role
        agent_specific_tasks = []
        for task in sorted_tasks:
            if task.get('suggested_agent_role') and role.startswith(task['suggested_agent_role']):
                agent_specific_tasks.append(task)
        
        # If no specific tasks, assign some general tasks
        if not agent_specific_tasks and sorted_tasks:
            # Take next unassigned high priority task
            for task in sorted_tasks:
                if task not in task_assignments:
                    agent_specific_tasks.append(task)
                    break
        
        # Select primary task
        primary_task = agent_specific_tasks[0] if agent_specific_tasks else {
            'task': 'Review codebase and identify improvement opportunities',
            'priority': 'medium'
        }
        
        agent_tasks[agent_name] = primary_task
        if primary_task in sorted_tasks:
            task_assignments.append(primary_task)
        
        # Add to coordination content
        coordination_content += f"""
### Agent {agent_letter} ({role})
- **Status**: 🔵 Ready
- **Current Task**: {primary_task['task']}
- **Priority**: {primary_task['priority'].upper()}
- **Progress**: 0%
- **Dependencies**: {', '.join(primary_task.get('dependencies', [])) or 'None'}
- **Focus Area**: {primary_task.get('area', 'General')}
"""
    
    # Add improvement summary
    coordination_content += f"""
## 🎯 Key Improvement Areas
"""
    
    # Group improvements by priority
    improvements_by_priority = {}
    for imp in analysis['improvements']:
        priority = imp['priority']
        if priority not in improvements_by_priority:
            improvements_by_priority[priority] = []
        improvements_by_priority[priority].append(imp)
    
    for priority in ['high', 'medium', 'low']:
        if priority in improvements_by_priority:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[priority]
            coordination_content += f"\n### {priority_emoji} {priority.capitalize()} Priority\n"
            for imp in improvements_by_priority[priority]:
                coordination_content += f"- **{imp['area']}**: {imp['description']}\n"
    
    coordination_content += """
## 📊 Overall Progress
- **Total Progress**: 0%
- **Active Tasks**: 0
- **Completed Tasks**: 0
- **Blocked Tasks**: 0

## 🔄 Recent Updates
- Project analysis completed
- Agent tasks assigned based on codebase assessment
- Ready to begin coordinated improvements

## 🎯 Next Steps
1. Review assigned tasks with agents
2. Start lifecycle management daemon
3. Begin high-priority improvements
4. Monitor progress through coordination dashboard
"""
    
    with open(coordination_md_path, 'w') as f:
        f.write(coordination_content)
    
    # Update AGENT_COORDINATION_MASTER.json
    master_json_path = os.path.join(base_dir, 'AGENT_COORDINATION_MASTER.json')
    master_data = {
        "project_name": project_name,
        "project_type": "existing_project_enhancement",
        "project_path": project_path,
        "project_description": description,
        "start_date": start_date,
        "deadline": deadline,
        "overall_status": "IN PROGRESS",
        "total_progress": 0,
        "last_update": datetime.now().isoformat(),
        "analysis_summary": {
            "total_files": analysis['project_info']['total_files'],
            "technologies": analysis['technologies'],
            "quality_metrics": analysis['quality_metrics'],
            "improvement_count": len(analysis['improvements']),
            "task_count": len(analysis['suggested_tasks'])
        },
        "agents": {}
    }
    
    # Initialize agent data with assigned tasks
    for i, agent_name in enumerate(agents):
        task = agent_tasks.get(agent_name, {})
        master_data["agents"][agent_name] = {
            "status": "Ready",
            "current_task": task.get('task', 'Awaiting task assignment'),
            "task_priority": task.get('priority', 'medium'),
            "task_area": task.get('area', 'General'),
            "progress": 0,
            "dependencies": task.get('dependencies', []),
            "blockers": [],
            "deliverables": [],
            "recent_activities": [
                f"Assigned to {task.get('area', 'project')} improvements",
                f"Analyzing {project_name} codebase"
            ]
        }
    
    with open(master_json_path, 'w') as f:
        json.dump(master_data, f, indent=2)
    
    # Update individual agent status files
    agent_status_dir = os.path.join(base_dir, 'agent_status')
    
    for i, agent_name in enumerate(agents):
        status_file = os.path.join(agent_status_dir, f"{agent_name.lower()}_status.json")
        task = agent_tasks.get(agent_name, {})
        
        agent_status = {
            "agent_name": agent_name.upper(),
            "status": "Ready",
            "current_task": task.get('task', 'Awaiting task assignment'),
            "task_details": {
                "priority": task.get('priority', 'medium'),
                "area": task.get('area', 'General'),
                "estimated_effort": task.get('estimated_effort', 'medium')
            },
            "progress": 0,
            "last_update": datetime.now().isoformat(),
            "dependencies": task.get('dependencies', []),
            "blockers": [],
            "deliverables": [],
            "recent_activities": [
                f"Initialized for {project_name} enhancement",
                f"Assigned to {task.get('area', 'project')} improvements"
            ],
            "project_context": {
                "name": project_name,
                "path": project_path,
                "technologies": analysis['technologies']['languages'][:3]
            }
        }
        
        with open(status_file, 'w') as f:
            json.dump(agent_status, f, indent=2)
    
    # Create project memory with analysis results
    memory_dir = os.path.join(base_dir, 'project_memories')
    os.makedirs(memory_dir, exist_ok=True)
    
    memory_content = f"""# {project_name} - Existing Project Information

## Overview
- **Project**: {project_name}
- **Type**: Existing Project Enhancement
- **Path**: {project_path}
- **Description**: {description}
- **Start Date**: {start_date}
- **Deadline**: {deadline}
- **Framework**: Multi-Agent Coordination System
- **Theme**: {theme}
- **Active Agents**: {agent_count}

## Project Analysis Results
- **Total Files**: {analysis['project_info']['total_files']:,}
- **Size**: {analysis['project_info']['total_size_mb']} MB
- **Languages**: {', '.join(analysis['technologies']['languages'])}
- **Frameworks**: {', '.join(analysis['technologies']['frameworks'])}
- **Databases**: {', '.join(analysis['technologies']['databases'])}

## Quality Assessment
- Has Tests: {'Yes' if analysis['quality_metrics']['has_tests'] else 'No'}
- Has CI/CD: {'Yes' if analysis['quality_metrics']['has_ci'] else 'No'}
- Has Linting: {'Yes' if analysis['quality_metrics']['has_linting'] else 'No'}
- Has Documentation: {'Yes' if analysis['quality_metrics']['has_documentation'] else 'No'}

## Key Improvement Areas
{chr(10).join(f"- {imp['area']}: {imp['description']}" for imp in analysis['improvements'][:5])}

## Agent Task Distribution
Agents have been assigned tasks based on the project analysis:
{chr(10).join(f"- {agent.upper()}: {task.get('task', 'TBD')}" for agent, task in agent_tasks.items())}

## Key Commands
- Start lifecycle management: `./manage_agents.sh auto`
- Monitor dashboard: `./coordination_manager.sh watch`
- Update agent status: `./coordination_manager.sh update <agent> --task "Task Name" --progress 50`

## Notes
- This is an existing project requiring enhancement
- Tasks are prioritized based on code quality analysis
- Agents will focus on incremental improvements
- Original functionality must be preserved
"""
    
    memory_path = os.path.join(memory_dir, f"{project_name.lower().replace(' ', '_')}_existing_project.md")
    with open(memory_path, 'w') as f:
        f.write(memory_content)
    
    # Save reference to analysis file
    analysis_ref_path = os.path.join(memory_dir, f"{project_name.lower().replace(' ', '_')}_analysis_ref.json")
    with open(analysis_ref_path, 'w') as f:
        json.dump({
            "analysis_file": str(Path(analysis_file).absolute()),
            "analysis_date": datetime.now().isoformat(),
            "project_path": project_path
        }, f, indent=2)
    
    print(f"\n✅ Existing project '{project_name}' initialized successfully!")
    print(f"📍 Project Path: {project_path}")
    print(f"📍 Theme: {theme} with {agent_count} agents")
    print(f"📅 Start Date: {start_date}")
    print(f"📅 Estimated Deadline: {deadline}")
    print(f"📋 Project memory saved to: {memory_path}")
    print(f"\n📊 Task Distribution:")
    
    for agent, task in agent_tasks.items():
        print(f"   {agent.upper()}: {task.get('task', 'TBD')[:60]}...")
    
    print("\n🚀 Next steps:")
    print("1. Review the assigned tasks in AGENT_COORDINATION.md")
    print("2. Start the lifecycle daemon: ./manage_agents.sh auto")
    print("3. Monitor progress: ./coordination_manager.sh watch")
    print("4. Agents will begin analyzing and improving the codebase")

def main():
    parser = argparse.ArgumentParser(
        description="Initialize Multi-Agent Coordination for an existing project using analysis"
    )
    parser.add_argument(
        "analysis_file",
        help="Path to the project analysis JSON file"
    )
    parser.add_argument(
        "-n", "--name",
        help="Custom project name (overrides analyzed name)",
        default=None
    )
    parser.add_argument(
        "--deadline",
        help="Project deadline (YYYY-MM-DD format)",
        default=None
    )
    
    args = parser.parse_args()
    
    # Validate analysis file
    if not os.path.exists(args.analysis_file):
        print(f"❌ Error: Analysis file not found: {args.analysis_file}")
        sys.exit(1)
    
    # Validate deadline format if provided
    if args.deadline:
        try:
            datetime.strptime(args.deadline, '%Y-%m-%d')
        except ValueError:
            print("❌ Error: Deadline must be in YYYY-MM-DD format")
            sys.exit(1)
    
    init_from_analysis(args.analysis_file, args.name, args.deadline)

if __name__ == "__main__":
    main()