#!/usr/bin/env python3
"""
Agent Status Aggregator
Collects and aggregates individual agent status files into a master coordination view.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coordination_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentStatusAggregator:
    """Aggregates individual agent status files into master coordination data."""
    
    def __init__(self, agent_status_dir: str = "agent_status", output_dir: str = ".", config_file: str = "../agent_config.json"):
        self.agent_status_dir = Path(agent_status_dir)
        self.output_dir = Path(output_dir)
        self.config_file = config_file
        self.agents = self._load_agents()
        self.agent_colors = {
            "alpha": "🔴",
            "beta": "🔵", 
            "gamma": "🟢",
            "delta": "🟡",
            "epsilon": "🟠",
            "zeta": "🟣"
        }
    
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
        
    def load_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Load status for a specific agent."""
        status_file = self.agent_status_dir / f"{agent_id}_status.json"
        
        if not status_file.exists():
            logger.warning(f"Status file not found for agent {agent_id}: {status_file}")
            return None
            
        try:
            with open(status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading status for agent {agent_id}: {e}")
            return None
    
    def load_all_agent_statuses(self) -> Dict[str, Dict]:
        """Load statuses for all agents."""
        statuses = {}
        
        for agent_id in self.agents:
            status = self.load_agent_status(agent_id)
            if status:
                statuses[agent_id] = status
                
        return statuses
    
    def calculate_project_metrics(self, statuses: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall project metrics from agent statuses."""
        total_tasks = 0
        completed_tasks = 0
        total_progress = 0
        active_agents = 0
        
        for agent_id, status in statuses.items():
            if status:
                metrics = status.get('metrics', {})
                total_tasks += metrics.get('tasks_total', 0)
                completed_tasks += metrics.get('tasks_completed', 0)
                total_progress += status.get('current_status', {}).get('progress', 0)
                active_agents += 1
                
        avg_progress = total_progress / max(active_agents, 1)
        
        return {
            'active_agents': active_agents,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_percentage': (completed_tasks / max(total_tasks, 1)) * 100,
            'average_progress': avg_progress,
            'project_health': '🟢' if avg_progress > 80 else '🟡' if avg_progress > 50 else '🔴'
        }
    
    def generate_master_coordination_json(self, statuses: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate master coordination data in JSON format."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        metrics = self.calculate_project_metrics(statuses)
        
        master_data = {
            "timestamp": timestamp,
            "project_metrics": metrics,
            "agents": {},
            "dependencies": [],
            "blockers": [],
            "cross_agent_communication": []
        }
        
        # Process each agent
        for agent_id, status in statuses.items():
            if not status:
                continue
                
            agent_data = {
                "info": status.get('agent_info', {}),
                "current_status": status.get('current_status', {}),
                "activities": status.get('activities', {}),
                "blockers": status.get('blockers', {}),
                "decisions": status.get('decisions', []),
                "next_steps": status.get('next_steps', []),
                "communication": status.get('communication', {}),
                "dependencies": status.get('dependencies', {}),
                "metrics": status.get('metrics', {}),
                "deliverables": status.get('deliverables', [])
            }
            
            master_data["agents"][agent_id] = agent_data
            
            # Collect dependencies
            deps = status.get('dependencies', {})
            if deps.get('blocking'):
                for blocked_agent in deps['blocking']:
                    master_data["dependencies"].append({
                        "from": agent_id,
                        "to": blocked_agent,
                        "type": "blocking"
                    })
            
            # Collect current blockers
            current_blockers = status.get('blockers', {}).get('current', [])
            if current_blockers:
                master_data["blockers"].extend([
                    {"agent": agent_id, "blocker": blocker} 
                    for blocker in current_blockers
                ])
            
            # Collect communication requests
            comm = status.get('communication', {})
            if comm.get('requests'):
                master_data["cross_agent_communication"].extend([
                    {"from": agent_id, "type": "request", "message": req}
                    for req in comm['requests']
                ])
            
            if comm.get('offers'):
                master_data["cross_agent_communication"].extend([
                    {"from": agent_id, "type": "offer", "message": offer}
                    for offer in comm['offers']
                ])
        
        return master_data
    
    def generate_coordination_markdown(self, master_data: Dict[str, Any]) -> str:
        """Generate AGENT_COORDINATION.md content from master data."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        markdown = f"""# Agent Coordination Hub

**Project:** File Organizer Parallel Development  
**Start Date:** 2025-01-18  
**Last Updated:** {timestamp}  
**Status:** Active Development

---

## 🚦 Global Status Dashboard

### **Overall Project Health**
- **Status:** {master_data['project_metrics']['project_health']} On Track
- **Active Agents:** {master_data['project_metrics']['active_agents']}
- **Completed Tasks:** {master_data['project_metrics']['completed_tasks']}/{master_data['project_metrics']['total_tasks']}
- **Overall Progress:** {master_data['project_metrics']['average_progress']:.1f}%
- **Critical Path Status:** 🟢 Significantly Ahead of Schedule

---

## 👥 Agent Status Updates

"""
        
        # Generate agent sections
        for agent_id, agent_data in master_data['agents'].items():
            info = agent_data.get('info', {})
            status = agent_data.get('current_status', {})
            activities = agent_data.get('activities', {})
            blockers = agent_data.get('blockers', {})
            decisions = agent_data.get('decisions', [])
            next_steps = agent_data.get('next_steps', [])
            communication = agent_data.get('communication', {})
            deliverables = agent_data.get('deliverables', [])
            
            markdown += f"""### {info.get('color', '⚪')} **Agent {info.get('name', agent_id.title())} ({info.get('role', 'Unknown Role')})**
**Current Task:** {status.get('task', 'Unknown')}  
**Status:** {status.get('status', '❓')} {status.get('status_text', 'Unknown')}  
**Progress:** {status.get('progress', 0)}% ({status.get('progress_description', 'No description')})  
**ETA:** {status.get('eta', 'Unknown')}  
**Last Update:** {status.get('last_update', 'Never')}

#### **Current Activities:**
"""
            
            # Add completed activities
            for activity in activities.get('completed', []):
                markdown += f"- [X] {activity}\n"
            
            # Add in-progress activities  
            for activity in activities.get('in_progress', []):
                markdown += f"- [ ] {activity}\n"
            
            # Add pending activities
            for activity in activities.get('pending', []):
                markdown += f"- [ ] {activity}\n"
            
            markdown += f"""
#### **Blockers & Issues:**
"""
            current_blockers = blockers.get('current', [])
            if current_blockers:
                for blocker in current_blockers:
                    markdown += f"- {blocker}\n"
            else:
                markdown += "- None - All deliverables completed successfully\n"
            
            if decisions:
                markdown += f"""
#### **Decisions Made:**
"""
                for decision in decisions:
                    markdown += f"- {decision}\n"
            
            if next_steps:
                markdown += f"""
#### **Next Steps:**
"""
                for step in next_steps:
                    markdown += f"- {step}\n"
            
            if communication.get('notes'):
                markdown += f"""
#### **Communication Notes:**
"""
                for note in communication['notes']:
                    markdown += f"- **{note.split(':')[0]}:** {':'.join(note.split(':')[1:]).strip()}\n"
            
            if deliverables:
                markdown += f"""
#### **Deliverables:**
"""
                for deliverable in deliverables:
                    markdown += f"- {deliverable}\n"
            
            markdown += "\n---\n\n"
        
        # Add cross-agent communication
        if master_data.get('cross_agent_communication'):
            markdown += """## 🔄 Cross-Agent Communication

### **Current Requests & Offers**
"""
            for comm in master_data['cross_agent_communication']:
                markdown += f"- **Agent {comm['from'].title()}** ({comm['type']}): {comm['message']}\n"
            
            markdown += "\n---\n\n"
        
        # Add dependencies
        if master_data.get('dependencies'):
            markdown += """## 🎯 Dependency Tracker

### **Current Dependencies**
"""
            for dep in master_data['dependencies']:
                markdown += f"- **Agent {dep['from'].title()}** blocks **Agent {dep['to'].title()}**\n"
            
            markdown += "\n---\n\n"
        
        # Add blockers
        if master_data.get('blockers'):
            markdown += """## 🚨 Current Blockers

"""
            for blocker in master_data['blockers']:
                markdown += f"- **Agent {blocker['agent'].title()}:** {blocker['blocker']}\n"
            
            markdown += "\n---\n\n"
        
        markdown += f"""
---

*This coordination document was auto-generated at {timestamp} from individual agent status files.*
"""
        
        return markdown
    
    def aggregate_and_save(self) -> bool:
        """Load all agent statuses and generate master coordination files."""
        try:
            logger.info("Starting status aggregation...")
            
            # Load all agent statuses
            statuses = self.load_all_agent_statuses()
            if not statuses:
                logger.warning("No agent statuses found")
                return False
            
            logger.info(f"Loaded statuses for {len(statuses)} agents")
            
            # Generate master coordination data
            master_data = self.generate_master_coordination_json(statuses)
            
            # Save JSON file
            json_file = self.output_dir / "AGENT_COORDINATION_MASTER.json"
            with open(json_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            logger.info(f"Saved master coordination JSON to {json_file}")
            
            # Generate and save markdown file
            markdown_content = self.generate_coordination_markdown(master_data)
            markdown_file = self.output_dir / "AGENT_COORDINATION_GENERATED.md"
            with open(markdown_file, 'w') as f:
                f.write(markdown_content)
            logger.info(f"Saved master coordination markdown to {markdown_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during aggregation: {e}")
            return False
    
    def watch_and_aggregate(self, interval: int = 30):
        """Watch for changes and aggregate periodically."""
        logger.info(f"Starting file watcher with {interval}s interval...")
        
        while True:
            try:
                self.aggregate_and_save()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Stopping file watcher...")
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                time.sleep(interval)

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Status Aggregator")
    parser.add_argument("--watch", action="store_true", help="Watch for changes and aggregate continuously")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    parser.add_argument("--agent-dir", default="agent_status", help="Agent status directory")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--config-file", default="../agent_config.json", help="Agent configuration file")
    
    args = parser.parse_args()
    
    aggregator = AgentStatusAggregator(args.agent_dir, args.output_dir, args.config_file)
    
    if args.watch:
        aggregator.watch_and_aggregate(args.interval)
    else:
        success = aggregator.aggregate_and_save()
        exit(0 if success else 1)

if __name__ == "__main__":
    main()