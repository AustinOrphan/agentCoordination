#!/usr/bin/env python3
"""
Agent Simulator - Simulates agent work without launching Claude Code
This allows testing the coordination system without actual Claude instances
"""

import json
import time
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

class AgentSimulator:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.status_file = Path(f"agent_status/{agent_name}_status.json")
        self.comm_dir = Path(f"agent_communication/{agent_name}")
        self.inbox = self.comm_dir / "input" / "inbox.json"
        self.outbox = self.comm_dir / "output" / "outbox.json"
        
    def load_status(self):
        """Load current status"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_status(self, status):
        """Save status"""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def update_progress(self, progress, description="Working..."):
        """Update agent progress"""
        status = self.load_status()
        if status:
            status['current_status']['progress'] = progress
            status['current_status']['progress_description'] = description
            status['current_status']['status'] = '🟡'
            status['current_status']['status_text'] = 'Working'
            status['current_status']['last_update'] = datetime.now(timezone.utc).isoformat()
            self.save_status(status)
            print(f"[{self.agent_name}] Progress: {progress}% - {description}")
    
    def simulate_work(self):
        """Simulate agent doing work"""
        print(f"🤖 Agent {self.agent_name} simulator starting...")
        
        # Update to working status
        self.update_progress(10, "Analyzing task requirements")
        time.sleep(5)
        
        self.update_progress(25, "Setting up environment")
        time.sleep(5)
        
        self.update_progress(50, "Implementing solution")
        time.sleep(10)
        
        self.update_progress(75, "Testing implementation")
        time.sleep(5)
        
        self.update_progress(90, "Finalizing work")
        time.sleep(3)
        
        self.update_progress(100, "Task completed")
        
        # Update to completed status
        status = self.load_status()
        if status:
            status['current_status']['status'] = '🟢'
            status['current_status']['status_text'] = 'Completed'
            self.save_status(status)
        
        print(f"✅ Agent {self.agent_name} completed simulation")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_agent_simulator.py <agent_name>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    simulator = AgentSimulator(agent_name)
    
    try:
        simulator.simulate_work()
    except KeyboardInterrupt:
        print(f"\n⚠️ Agent {agent_name} simulation interrupted")
        sys.exit(0)

if __name__ == "__main__":
    main()