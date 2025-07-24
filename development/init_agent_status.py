#!/usr/bin/env python3
"""
Initialize agent status files for all agents in current theme
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

def load_agent_config():
    """Load current agent configuration"""
    config_file = Path("agent_config.json")
    if not config_file.exists():
        print("❌ agent_config.json not found. Run generate_agents_dynamic.sh first.")
        return None
    
    with open(config_file, 'r') as f:
        return json.load(f)

def get_current_agents(config):
    """Get list of current agents from config"""
    if not config:
        return []
    
    current_theme = config.get('current_theme', 'greek_letters')
    agent_count = config.get('agent_count', 6)
    
    themes = config.get('themes', {})
    if current_theme not in themes:
        print(f"❌ Theme {current_theme} not found in config")
        return []
    
    theme_data = themes[current_theme]
    agents = theme_data.get('agents', [])
    
    return agents[:agent_count]

def create_status_file(agent_name, agent_info, force=False):
    """Create initial status file for an agent"""
    status_dir = Path("agent_status")
    status_dir.mkdir(exist_ok=True)
    
    status_file = status_dir / f"{agent_name}_status.json"
    
    # Don't overwrite existing status files unless force mode
    if status_file.exists() and not force:
        print(f"✅ Status file already exists for {agent_name}")
        return
    elif status_file.exists() and force:
        print(f"🔄 Recreating status file for {agent_name}")
    
    # Create initial status
    timestamp = datetime.now(timezone.utc).isoformat()
    
    initial_status = {
        "agent_info": {
            "name": agent_info.get('display_name', agent_name.title()),
            "role": agent_info.get('role', 'General Agent'),
            "theme": agent_info.get('theme', 'default'),
            "color": agent_info.get('color', '⚪'),
            "emoji": agent_info.get('emoji', '🤖')
        },
        "current_status": {
            "status": "🔵",
            "status_text": "Initialized",
            "task": "Awaiting assignment",
            "progress": 0,
            "progress_description": "Agent initialized and ready",
            "last_update": timestamp
        },
        "activities": {
            "completed": [],
            "in_progress": [],
            "planned": []
        },
        "blockers": {
            "current": [],
            "resolved": []
        },
        "metrics": {
            "tasks_completed": 0,
            "total_progress": 0,
            "efficiency": 1.0,
            "last_activity": timestamp
        },
        "authority": {
            "current_authorities": [],
            "authority_requests": [],
            "authority_history": []
        }
    }
    
    # Write status file
    with open(status_file, 'w') as f:
        json.dump(initial_status, f, indent=2)
    
    print(f"✅ Created status file for {agent_name}")

def create_communication_structure(agent_name):
    """Create communication directories and files"""
    comm_dir = Path("agent_communication") / agent_name
    
    # Create directories
    (comm_dir / "input").mkdir(parents=True, exist_ok=True)
    (comm_dir / "output").mkdir(parents=True, exist_ok=True)
    (comm_dir / "status").mkdir(parents=True, exist_ok=True)
    
    # Create empty inbox and outbox
    inbox = comm_dir / "input" / "inbox.json"
    outbox = comm_dir / "output" / "outbox.json"
    lifecycle = comm_dir / "status" / "lifecycle.json"
    heartbeat = comm_dir / "status" / "heartbeat.json"
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if not inbox.exists():
        with open(inbox, 'w') as f:
            json.dump({"messages": [], "last_checked": timestamp}, f, indent=2)
    
    if not outbox.exists():
        with open(outbox, 'w') as f:
            json.dump({"messages": [], "last_sent": timestamp}, f, indent=2)
    
    if not lifecycle.exists():
        with open(lifecycle, 'w') as f:
            json.dump({"status": "offline", "last_update": timestamp}, f, indent=2)
    
    if not heartbeat.exists():
        with open(heartbeat, 'w') as f:
            json.dump({"last_heartbeat": timestamp, "health": "unknown"}, f, indent=2)

def main():
    import sys
    force = "--force" in sys.argv
    
    print("🚀 Initializing Agent Status Files")
    if force:
        print("⚠️  Force mode: Recreating all status files")
    print("-" * 40)
    
    # Load configuration
    config = load_agent_config()
    if not config:
        return
    
    # Get current agents
    agents = get_current_agents(config)
    if not agents:
        print("❌ No agents found in current theme")
        return
    
    print(f"Found {len(agents)} agents in current theme")
    
    # Get theme info
    current_theme = config.get('current_theme', 'greek_letters')
    theme_data = config.get('themes', {}).get(current_theme, {})
    
    # Initialize each agent
    for i, agent_name in enumerate(agents):
        # Get agent-specific info from theme
        agent_info = {
            'display_name': agent_name.replace('_', ' ').title(),
            'role': get_agent_role(i),
            'theme': current_theme,
            'color': theme_data.get('colors', ['⚪'] * len(agents))[i] if i < len(theme_data.get('colors', [])) else '⚪',
            'emoji': theme_data.get('agent_emojis', ['🤖'] * len(agents))[i] if i < len(theme_data.get('agent_emojis', [])) else '🤖'
        }
        
        # Create status file
        create_status_file(agent_name, agent_info, force=force)
        
        # Create communication structure
        create_communication_structure(agent_name)
    
    print("-" * 40)
    print(f"✅ Initialized {len(agents)} agents successfully!")
    print("\nNext steps:")
    print("1. Start lifecycle daemon: ./manage_agents.sh auto")
    print("2. Monitor progress: ./coordination_manager.sh watch")

def get_agent_role(index):
    """Get agent role based on index (cycling through 6 roles)"""
    roles = [
        "Critical Path Lead",
        "Migration Specialist", 
        "Dashboard Developer",
        "DevOps Engineer",
        "Security Engineer",
        "UX Engineer"
    ]
    return roles[index % len(roles)]

if __name__ == "__main__":
    main()