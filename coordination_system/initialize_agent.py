#!/usr/bin/env python3
"""
Initialize a specific agent for execution
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def initialize_agent(agent_name):
    """Initialize agent for startup"""
    print(f"🔧 Initializing agent {agent_name}")
    
    # Update agent status to starting
    status_file = Path("agent_status") / f"{agent_name}_status.json"
    
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        # Update status to starting
        status['current_status']['status'] = '🟡'
        status['current_status']['status_text'] = 'Starting'
        status['current_status']['last_update'] = datetime.now(timezone.utc).isoformat()
        
        # Add startup activity
        if 'activities' not in status:
            status['activities'] = {'in_progress': [], 'completed': [], 'planned': []}
        
        status['activities']['in_progress'].append(f"Agent {agent_name} initializing")
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"✅ Agent {agent_name} status updated to 'Starting'")
    else:
        print(f"❌ Status file not found for agent {agent_name}")
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 initialize_agent.py <agent_name>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    if initialize_agent(agent_name):
        print(f"🚀 Agent {agent_name} initialized successfully")
    else:
        print(f"❌ Failed to initialize agent {agent_name}")
        sys.exit(1)

if __name__ == "__main__":
    main()