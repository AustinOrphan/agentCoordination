#!/usr/bin/env python3
"""
Enhanced Status Aggregator with Real-Time File Watching and Change Queue
Monitors agent status files and maintains real-time coordination view
"""

import json
import os
import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from queue import Queue, Empty
from threading import Thread, Lock, Event
import signal

# Try to import watchdog, provide fallback if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Install with: pip install watchdog")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChangeQueue:
    """Thread-safe queue for managing file change notifications"""
    def __init__(self):
        self.queue = Queue()
        self.processing_lock = Lock()
        self.processed_changes = set()
        
    def add_change(self, file_path: str, timestamp: float):
        """Add a change notification to the queue"""
        change_id = f"{file_path}:{timestamp}"
        with self.processing_lock:
            if change_id not in self.processed_changes:
                self.queue.put((file_path, timestamp))
                self.processed_changes.add(change_id)
                logger.debug(f"Queued change: {file_path}")
    
    def get_next_change(self, timeout=1.0):
        """Get the next change from the queue"""
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None
    
    def pending_count(self):
        """Get count of pending changes"""
        return self.queue.qsize()

class AgentFileHandler(FileSystemEventHandler):
    """Handles file system events for agent status files"""
    def __init__(self, change_queue: ChangeQueue, agent_files: Set[str]):
        self.change_queue = change_queue
        self.agent_files = agent_files
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path in self.agent_files:
            timestamp = time.time()
            self.change_queue.add_change(event.src_path, timestamp)
            logger.info(f"Detected change in: {os.path.basename(event.src_path)}")

class EnhancedStatusAggregator:
    """Enhanced aggregator with real-time monitoring and change queue"""
    
    def __init__(self, agent_dir: str, output_dir: str, config_file: str = "runtime/agent_config.json"):
        self.agent_dir = Path(agent_dir)
        self.output_dir = Path(output_dir)
        self.config_file = config_file
        self.change_queue = ChangeQueue()
        self.agents = self._load_agents()
        self.agent_emojis = self._load_agent_emojis()
        self.theme_emoji = self._load_theme_emoji()
        self.agent_files = {
            str(self.agent_dir / f"{agent}_status.json") 
            for agent in self.agents
        }
        self.last_aggregation = {}
        self.aggregation_lock = Lock()
        self.display_lock = Lock()
        self.stop_event = Event()
        self.observer = None
    
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
    
    def _load_agent_emojis(self) -> Dict[str, str]:
        """Load agent emojis from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    current_theme = config.get('current_theme', 'greek_letters')
                    theme_data = config.get('themes', {}).get(current_theme, {})
                    agent_emojis = theme_data.get('agent_emojis', [])
                    
                    # Create mapping
                    emoji_map = {}
                    for i, agent in enumerate(self.agents):
                        if i < len(agent_emojis):
                            emoji_map[agent] = agent_emojis[i]
                        else:
                            emoji_map[agent] = theme_data.get('emoji', '🤖')
                    return emoji_map
        except Exception as e:
            logger.warning(f"Could not load agent emojis: {e}")
        
        # Return default mapping
        return {agent: '🤖' for agent in self.agents}
    
    def _load_theme_emoji(self) -> str:
        """Load theme emoji from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    current_theme = config.get('current_theme', 'greek_letters')
                    theme_data = config.get('themes', {}).get(current_theme, {})
                    return theme_data.get('emoji', '🤖')
        except Exception as e:
            logger.warning(f"Could not load theme emoji: {e}")
        return '🤖'
        
    def load_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Load status for a specific agent"""
        status_file = self.agent_dir / f"{agent_id}_status.json"
        
        if not status_file.exists():
            logger.warning(f"Status file not found for agent {agent_id}: {status_file}")
            return None
            
        try:
            with open(status_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for agent {agent_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading status for agent {agent_id}: {e}")
            return None
    
    def load_all_agent_statuses(self) -> Dict[str, Dict]:
        """Load status for all agents"""
        statuses = {}
        for agent_id in self.agents:
            status = self.load_agent_status(agent_id)
            if status:
                statuses[agent_id] = status
        
        logger.info(f"Loaded statuses for {len(statuses)} agents")
        return statuses
    
    def generate_master_coordination_json(self, statuses: Dict[str, Dict]) -> Dict:
        """Generate master coordination data in JSON format"""
        # Use timezone-aware datetime
        timestamp = datetime.now(timezone.utc).isoformat()
        
        master_data = {
            "metadata": {
                "generated_at": timestamp,
                "total_agents": len(self.agents),
                "active_agents": len(statuses),
                "aggregator_version": "2.0"
            },
            "agents": statuses,
            "summary": {
                "completed_agents": [],
                "in_progress_agents": [],
                "blocked_agents": [],
                "starting_agents": []
            }
        }
        
        # Categorize agents by status
        for agent_id, status in statuses.items():
            current_status = status.get("current_status", {})
            status_emoji = current_status.get("status", "")
            
            if status_emoji == "🟢":
                master_data["summary"]["completed_agents"].append(agent_id)
            elif status_emoji == "🟡":
                master_data["summary"]["in_progress_agents"].append(agent_id)
            elif status_emoji == "🔴":
                master_data["summary"]["blocked_agents"].append(agent_id)
            elif status_emoji == "🔵":
                master_data["summary"]["starting_agents"].append(agent_id)
        
        return master_data
    
    def save_master_files(self, master_data: Dict) -> bool:
        """Save master coordination files"""
        try:
            # Save JSON
            json_path = self.output_dir / "AGENT_COORDINATION_MASTER.json"
            with open(json_path, 'w') as f:
                json.dump(master_data, f, indent=2)
            logger.info(f"Saved master coordination JSON to {json_path}")
            
            # Generate and save markdown
            markdown_content = self.generate_markdown_report(master_data)
            md_path = self.output_dir / "AGENT_COORDINATION_GENERATED.md"
            with open(md_path, 'w') as f:
                f.write(markdown_content)
            logger.info(f"Saved master coordination markdown to {md_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving master files: {e}")
            return False
    
    def generate_markdown_report(self, master_data: Dict) -> str:
        """Generate human-readable markdown report"""
        # Use timezone-aware datetime
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        md = f"""# Agent Coordination Status (Auto-Generated)

**Generated:** {timestamp}  
**Active Agents:** {master_data['metadata']['active_agents']}/{master_data['metadata']['total_agents']}  
**Aggregator Version:** {master_data['metadata']['aggregator_version']}

## 📊 Summary

- 🟢 **Completed:** {len(master_data['summary']['completed_agents'])} agents
- 🟡 **In Progress:** {len(master_data['summary']['in_progress_agents'])} agents
- 🔴 **Blocked:** {len(master_data['summary']['blocked_agents'])} agents
- 🔵 **Starting:** {len(master_data['summary']['starting_agents'])} agents

## 👥 Agent Details

"""
        
        for agent_id, status in master_data['agents'].items():
            info = status.get('agent_info', {})
            current = status.get('current_status', {})
            
            agent_emoji = self.agent_emojis.get(agent_id, self.theme_emoji)
            md += f"""### {agent_emoji} **Agent {info.get('name', agent_id)}** ({info.get('role', 'Unknown Role')})

**Current Task:** {current.get('task', 'No task assigned')}  
**Status:** {current.get('status', '')} {current.get('status_text', 'Unknown')}  
**Progress:** {current.get('progress', 0)}% - {current.get('progress_description', 'No description')}  
**Last Update:** {current.get('last_update', 'Never')}  

"""
            
            # Add blockers if any
            blockers_data = status.get('blockers', {})
            if isinstance(blockers_data, list):
                # Handle legacy format where blockers was a list
                blockers = blockers_data
            else:
                # Handle new format where blockers is a dict with 'current' key
                blockers = blockers_data.get('current', [])
            if blockers:
                md += "**Current Blockers:**\n"
                for blocker in blockers:
                    md += f"- {blocker}\n"
                md += "\n"
            
            # Add recent activities
            activities = status.get('activities', {})
            in_progress = activities.get('in_progress', [])
            if in_progress:
                md += "**In Progress:**\n"
                for activity in in_progress[:3]:  # Show top 3
                    md += f"- {activity}\n"
                md += "\n"
            
            md += "---\n\n"
        
        return md
    
    def aggregate_and_save(self) -> bool:
        """Perform aggregation and save results"""
        with self.aggregation_lock:
            statuses = self.load_all_agent_statuses()
            if not statuses:
                logger.warning("No agent statuses loaded")
                return False
            
            master_data = self.generate_master_coordination_json(statuses)
            success = self.save_master_files(master_data)
            
            if success:
                self.last_aggregation = master_data
            
            return success
    
    def process_change_queue(self):
        """Process changes from the queue"""
        while not self.stop_event.is_set():
            change = self.change_queue.get_next_change()
            if change:
                file_path, timestamp = change
                agent_name = os.path.basename(file_path).replace('_status.json', '')
                logger.info(f"Processing change for agent: {agent_name}")
                
                # Aggregate with a small delay to catch rapid changes
                time.sleep(0.5)
                self.aggregate_and_save()
                
                # Clear any duplicate changes that arrived during processing
                while self.change_queue.get_next_change(timeout=0.1):
                    pass
    
    def display_real_time_status(self):
        """Display real-time status with updates"""
        last_display_data = None
        
        while not self.stop_event.is_set():
            with self.display_lock:
                current_data = self.last_aggregation.copy() if self.last_aggregation else None
                
                if current_data and current_data != last_display_data:
                    self.clear_screen()
                    self.print_status_dashboard(current_data)
                    last_display_data = current_data
                    
                    # Show pending changes
                    pending = self.change_queue.pending_count()
                    if pending > 0:
                        print(f"\n⏳ Processing {pending} pending changes...")
            
            time.sleep(1)  # Update display every second
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_status_dashboard(self, data: Dict):
        """Print formatted status dashboard"""
        if not data:
            return
            
        meta = data.get('metadata', {})
        summary = data.get('summary', {})
        
        print("╔══════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                               AGENT COORDINATION DASHBOARD                                    ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════════════════╝")
        print(f"\nLast Update: {meta.get('generated_at', 'Unknown')}")
        print(f"Active Agents: {meta.get('active_agents', 0)}/{meta.get('total_agents', 0)}")
        print(f"\n📊 Status Summary:")
        print(f"  🟢 Completed: {len(summary.get('completed_agents', []))}")
        print(f"  🟡 In Progress: {len(summary.get('in_progress_agents', []))}")
        print(f"  🔴 Blocked: {len(summary.get('blocked_agents', []))}")
        print(f"  🔵 Starting: {len(summary.get('starting_agents', []))}")
        
        print("\n👥 Agent Status:")
        print("─" * 94)
        
        for agent_id, status in data.get('agents', {}).items():
            info = status.get('agent_info', {})
            current = status.get('current_status', {})
            
            # Format agent line
            agent_emoji = self.agent_emojis.get(agent_id, self.theme_emoji)
            name_role = f"{agent_emoji} {info.get('name', agent_id)} ({info.get('role', 'Unknown')})"
            progress = f"{current.get('progress', 0)}%"
            status_icon = current.get('status', '?')
            last_update = current.get('last_update', 'Never')
            
            # Calculate time since update
            try:
                update_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M UTC")
                update_time = update_time.replace(tzinfo=timezone.utc)
                time_diff = datetime.now(timezone.utc) - update_time
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                if minutes_ago < 10:
                    freshness = "🟢"
                elif minutes_ago < 30:
                    freshness = "🟡"
                else:
                    freshness = "🔴"
                    
                time_str = f"{minutes_ago}m ago"
            except:
                freshness = "⚪"
                time_str = "Unknown"
            
            print(f"{info.get('color', '⚪')} {name_role:<30} {status_icon} {progress:>4} {freshness} {time_str:>10}")
            
            # Show current task (truncated)
            task = current.get('task', 'No task')[:50] + "..." if len(current.get('task', '')) > 50 else current.get('task', 'No task')
            print(f"   └─ {task}")
            
            # Show blockers if any
            blockers_data = status.get('blockers', {})
            if isinstance(blockers_data, list):
                # Handle legacy format where blockers was a list
                blockers = blockers_data
            else:
                # Handle new format where blockers is a dict with 'current' key
                blockers = blockers_data.get('current', [])
            if blockers:
                print(f"   └─ ⚠️  Blocked: {blockers[0][:60]}...")
        
        print("─" * 94)
        print("\nPress Ctrl+C to stop monitoring")
    
    def start_file_watcher(self):
        """Start watching agent status files for changes"""
        if not WATCHDOG_AVAILABLE:
            logger.error("Watchdog not available. Install with: pip install watchdog")
            return False
            
        try:
            event_handler = AgentFileHandler(self.change_queue, self.agent_files)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.agent_dir), recursive=False)
            self.observer.start()
            logger.info(f"Started file watcher on {self.agent_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            return False
    
    def run_with_real_time_display(self):
        """Run aggregator with real-time display and file watching"""
        # Initial aggregation
        self.aggregate_and_save()
        
        # Start file watcher
        if not self.start_file_watcher():
            logger.error("Failed to start file watcher")
            return
        
        # Start change processor thread
        processor_thread = Thread(target=self.process_change_queue, daemon=True)
        processor_thread.start()
        
        # Run display in main thread
        try:
            self.display_real_time_status()
        except KeyboardInterrupt:
            logger.info("\nStopping real-time monitoring...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop all monitoring threads"""
        self.stop_event.set()
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("Monitoring stopped")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Agent Status Aggregator')
    parser.add_argument('--agent-dir', default='../agent_status',
                        help='Directory containing agent status files')
    parser.add_argument('--output-dir', default='..',
                        help='Directory for output files')
    parser.add_argument('--config-file', default='../agent_config.json',
                        help='Agent configuration file')
    parser.add_argument('--watch', action='store_true',
                        help='Watch for changes and display real-time status')
    parser.add_argument('--once', action='store_true',
                        help='Run aggregation once and exit')
    
    args = parser.parse_args()
    
    # Create aggregator
    aggregator = EnhancedStatusAggregator(args.agent_dir, args.output_dir, args.config_file)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nGracefully shutting down...")
        aggregator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    if args.once:
        # Run once and exit
        success = aggregator.aggregate_and_save()
        sys.exit(0 if success else 1)
    elif args.watch:
        # Run with real-time display
        aggregator.run_with_real_time_display()
    else:
        # Default: run once
        success = aggregator.aggregate_and_save()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()