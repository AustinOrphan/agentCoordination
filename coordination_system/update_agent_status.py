#!/usr/bin/env python3
"""
Agent Status Update Utility
Allows agents to update their individual status files safely.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import argparse
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_updates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentStatusUpdater:
    """Safely updates individual agent status files."""
    
    def __init__(self, agent_status_dir: str = "agent_status", config_file: str = "agent_config.json"):
        self.agent_status_dir = Path(agent_status_dir)
        self.config_file = config_file
        self.agents = self._load_agents()
        
        # Ensure directory exists
        self.agent_status_dir.mkdir(exist_ok=True)
    
    def _load_agents(self) -> List[str]:
        """Load agents from config file or use defaults."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Get current theme and agent count
                current_theme = config.get('current_theme', 'greek_letters')
                agent_count = config.get('agent_count', 6)
                
                # Get agents from current theme
                if current_theme in config.get('themes', {}):
                    agents = config['themes'][current_theme]['agents'][:agent_count]
                    logger.info(f"Loaded {len(agents)} agents from theme '{current_theme}'")
                    return agents
        except Exception as e:
            logger.warning(f"Error loading agent config: {e}, using defaults")
        
        # Fallback to default agents
        return ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
        
    def get_agent_status_file(self, agent_id: str) -> Path:
        """Get the path to an agent's status file."""
        return self.agent_status_dir / f"{agent_id}_status.json"
    
    def load_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Load current status for an agent."""
        status_file = self.get_agent_status_file(agent_id)
        
        if not status_file.exists():
            logger.warning(f"Status file not found for agent {agent_id}: {status_file}")
            return None
            
        try:
            with open(status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading status for agent {agent_id}: {e}")
            return None
    
    def save_agent_status(self, agent_id: str, status: Dict) -> bool:
        """Safely save agent status using atomic write."""
        status_file = self.get_agent_status_file(agent_id)
        
        try:
            # Update timestamp
            status['current_status']['last_update'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                json.dump(status, tmp_file, indent=2)
                tmp_file_path = tmp_file.name
            
            # Atomic move
            shutil.move(tmp_file_path, status_file)
            logger.info(f"Successfully updated status for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving status for agent {agent_id}: {e}")
            # Clean up temporary file if it exists
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            return False
    
    def update_task(self, agent_id: str, task: str, status: str = None, 
                   status_text: str = None, progress: int = None, 
                   progress_description: str = None, eta: str = None) -> bool:
        """Update agent's current task information."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot update task for agent {agent_id} - status not found")
            return False
        
        # Update task information
        current_status['current_status']['task'] = task
        if status:
            current_status['current_status']['status'] = status
        if status_text:
            current_status['current_status']['status_text'] = status_text
        if progress is not None:
            current_status['current_status']['progress'] = progress
        if progress_description:
            current_status['current_status']['progress_description'] = progress_description
        if eta:
            current_status['current_status']['eta'] = eta
        
        return self.save_agent_status(agent_id, current_status)
    
    def add_activity(self, agent_id: str, activity: str, activity_type: str = "completed") -> bool:
        """Add an activity to the agent's activity list."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot add activity for agent {agent_id} - status not found")
            return False
        
        if activity_type not in current_status['activities']:
            current_status['activities'][activity_type] = []
        
        if activity not in current_status['activities'][activity_type]:
            current_status['activities'][activity_type].append(activity)
        
        return self.save_agent_status(agent_id, current_status)
    
    def move_activity(self, agent_id: str, activity: str, from_type: str, to_type: str) -> bool:
        """Move an activity from one category to another."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot move activity for agent {agent_id} - status not found")
            return False
        
        # Remove from source
        if from_type in current_status['activities']:
            if activity in current_status['activities'][from_type]:
                current_status['activities'][from_type].remove(activity)
        
        # Add to destination
        if to_type not in current_status['activities']:
            current_status['activities'][to_type] = []
        
        if activity not in current_status['activities'][to_type]:
            current_status['activities'][to_type].append(activity)
        
        return self.save_agent_status(agent_id, current_status)
    
    def add_blocker(self, agent_id: str, blocker: str) -> bool:
        """Add a blocker to the agent's current blockers."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot add blocker for agent {agent_id} - status not found")
            return False
        
        if 'current' not in current_status['blockers']:
            current_status['blockers']['current'] = []
        
        if blocker not in current_status['blockers']['current']:
            current_status['blockers']['current'].append(blocker)
        
        return self.save_agent_status(agent_id, current_status)
    
    def resolve_blocker(self, agent_id: str, blocker: str) -> bool:
        """Move a blocker from current to resolved."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot resolve blocker for agent {agent_id} - status not found")
            return False
        
        # Remove from current
        if 'current' in current_status['blockers']:
            if blocker in current_status['blockers']['current']:
                current_status['blockers']['current'].remove(blocker)
        
        # Add to resolved
        if 'resolved' not in current_status['blockers']:
            current_status['blockers']['resolved'] = []
        
        if blocker not in current_status['blockers']['resolved']:
            current_status['blockers']['resolved'].append(blocker)
        
        return self.save_agent_status(agent_id, current_status)
    
    def add_decision(self, agent_id: str, decision: str) -> bool:
        """Add a decision to the agent's decisions."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot add decision for agent {agent_id} - status not found")
            return False
        
        if 'decisions' not in current_status:
            current_status['decisions'] = []
        
        if decision not in current_status['decisions']:
            current_status['decisions'].append(decision)
        
        return self.save_agent_status(agent_id, current_status)
    
    def add_communication_note(self, agent_id: str, note: str) -> bool:
        """Add a communication note."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot add communication note for agent {agent_id} - status not found")
            return False
        
        if 'notes' not in current_status['communication']:
            current_status['communication']['notes'] = []
        
        if note not in current_status['communication']['notes']:
            current_status['communication']['notes'].append(note)
        
        return self.save_agent_status(agent_id, current_status)
    
    def update_metrics(self, agent_id: str, tasks_completed: int = None, 
                      tasks_total: int = None, completion_percentage: int = None) -> bool:
        """Update agent metrics."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            logger.error(f"Cannot update metrics for agent {agent_id} - status not found")
            return False
        
        if 'metrics' not in current_status:
            current_status['metrics'] = {}
        
        if tasks_completed is not None:
            current_status['metrics']['tasks_completed'] = tasks_completed
        if tasks_total is not None:
            current_status['metrics']['tasks_total'] = tasks_total
        if completion_percentage is not None:
            current_status['metrics']['completion_percentage'] = completion_percentage
        
        return self.save_agent_status(agent_id, current_status)
    
    def show_status(self, agent_id: str) -> bool:
        """Display current agent status."""
        current_status = self.load_agent_status(agent_id)
        if not current_status:
            print(f"No status found for agent {agent_id}")
            return False
        
        info = current_status.get('agent_info', {})
        status = current_status.get('current_status', {})
        
        print(f"\n{info.get('color', '⚪')} Agent {info.get('name', agent_id.title())} ({info.get('role', 'Unknown')})")
        print(f"Current Task: {status.get('task', 'Unknown')}")
        print(f"Status: {status.get('status', '❓')} {status.get('status_text', 'Unknown')}")
        print(f"Progress: {status.get('progress', 0)}% ({status.get('progress_description', 'No description')})")
        print(f"ETA: {status.get('eta', 'Unknown')}")
        print(f"Last Update: {status.get('last_update', 'Never')}")
        
        # Show current blockers
        blockers = current_status.get('blockers', {}).get('current', [])
        if blockers:
            print(f"Current Blockers:")
            for blocker in blockers:
                print(f"  - {blocker}")
        
        print()
        return True

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Agent Status Update Utility")
    parser.add_argument("agent_id", help="Agent ID (from current theme configuration)")
    parser.add_argument("--agent-dir", default="agent_status", help="Agent status directory")
    
    # Task updates
    parser.add_argument("--task", help="Update current task")
    parser.add_argument("--status", help="Update status (🟢, 🟡, 🔴, 🔵)")
    parser.add_argument("--status-text", help="Update status text")
    parser.add_argument("--progress", type=int, help="Update progress percentage")
    parser.add_argument("--progress-description", help="Update progress description")
    parser.add_argument("--eta", help="Update ETA")
    
    # Activity updates
    parser.add_argument("--add-activity", help="Add activity")
    parser.add_argument("--activity-type", default="completed", choices=["completed", "in_progress", "pending"])
    parser.add_argument("--move-activity", help="Move activity to different category")
    parser.add_argument("--from-type", default="pending", choices=["completed", "in_progress", "pending"])
    parser.add_argument("--to-type", default="completed", choices=["completed", "in_progress", "pending"])
    
    # Blocker updates
    parser.add_argument("--add-blocker", help="Add blocker")
    parser.add_argument("--resolve-blocker", help="Resolve blocker")
    
    # Other updates
    parser.add_argument("--add-decision", help="Add decision")
    parser.add_argument("--add-note", help="Add communication note")
    
    # Metrics
    parser.add_argument("--tasks-completed", type=int, help="Update tasks completed")
    parser.add_argument("--tasks-total", type=int, help="Update total tasks")
    parser.add_argument("--completion-percentage", type=int, help="Update completion percentage")
    
    # Actions
    parser.add_argument("--show", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    updater = AgentStatusUpdater(args.agent_dir)
    
    # Validate agent ID
    if args.agent_id not in updater.agents:
        print(f"Invalid agent ID: {args.agent_id}")
        print(f"Valid agent IDs: {', '.join(updater.agents)}")
        exit(1)
    
    # Show status
    if args.show:
        updater.show_status(args.agent_id)
        return
    
    # Update task
    if any([args.task, args.status, args.status_text, args.progress, args.progress_description, args.eta]):
        success = updater.update_task(
            args.agent_id, 
            args.task or updater.load_agent_status(args.agent_id)['current_status']['task'],
            args.status, 
            args.status_text, 
            args.progress, 
            args.progress_description, 
            args.eta
        )
        if success:
            print(f"Updated task information for agent {args.agent_id}")
        else:
            print(f"Failed to update task for agent {args.agent_id}")
    
    # Add activity
    if args.add_activity:
        success = updater.add_activity(args.agent_id, args.add_activity, args.activity_type)
        if success:
            print(f"Added activity for agent {args.agent_id}")
        else:
            print(f"Failed to add activity for agent {args.agent_id}")
    
    # Move activity
    if args.move_activity:
        success = updater.move_activity(args.agent_id, args.move_activity, args.from_type, args.to_type)
        if success:
            print(f"Moved activity for agent {args.agent_id}")
        else:
            print(f"Failed to move activity for agent {args.agent_id}")
    
    # Add blocker
    if args.add_blocker:
        success = updater.add_blocker(args.agent_id, args.add_blocker)
        if success:
            print(f"Added blocker for agent {args.agent_id}")
        else:
            print(f"Failed to add blocker for agent {args.agent_id}")
    
    # Resolve blocker
    if args.resolve_blocker:
        success = updater.resolve_blocker(args.agent_id, args.resolve_blocker)
        if success:
            print(f"Resolved blocker for agent {args.agent_id}")
        else:
            print(f"Failed to resolve blocker for agent {args.agent_id}")
    
    # Add decision
    if args.add_decision:
        success = updater.add_decision(args.agent_id, args.add_decision)
        if success:
            print(f"Added decision for agent {args.agent_id}")
        else:
            print(f"Failed to add decision for agent {args.agent_id}")
    
    # Add communication note
    if args.add_note:
        success = updater.add_communication_note(args.agent_id, args.add_note)
        if success:
            print(f"Added communication note for agent {args.agent_id}")
        else:
            print(f"Failed to add communication note for agent {args.agent_id}")
    
    # Update metrics
    if any([args.tasks_completed, args.tasks_total, args.completion_percentage]):
        success = updater.update_metrics(args.agent_id, args.tasks_completed, args.tasks_total, args.completion_percentage)
        if success:
            print(f"Updated metrics for agent {args.agent_id}")
        else:
            print(f"Failed to update metrics for agent {args.agent_id}")

if __name__ == "__main__":
    main()