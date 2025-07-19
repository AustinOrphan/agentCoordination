#!/usr/bin/env python3
"""
Agent Lifecycle Manager
Monitors agent status and automatically starts/stops agents based on blockers and dependencies.
"""

import json
import os
import time
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import signal
import psutil

from agent_communication import (
    CommunicationChannel, CentralDispatcher, Message, 
    MessageType, Priority, AgentStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentProcess:
    """Represents a running agent process"""
    
    def __init__(self, agent_id: str, pid: Optional[int] = None):
        self.agent_id = agent_id
        self.pid = pid
        self.start_time = datetime.now()
        self.status = AgentStatus.STOPPED
    
    def is_running(self) -> bool:
        """Check if process is still running"""
        if self.pid is None:
            return False
        
        try:
            process = psutil.Process(self.pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

class LifecycleManager:
    """Manages agent lifecycle based on blockers and dependencies"""
    
    def __init__(self, config_file: str = "agent_config.json", 
                 status_dir: str = "agent_status",
                 communication_dir: str = "agent_communication"):
        self.config_file = config_file
        self.status_dir = Path(status_dir)
        self.communication_dir = Path(communication_dir)
        self.agents = self._load_agents()
        self.processes: Dict[str, AgentProcess] = {}
        self.dispatcher = CentralDispatcher(str(self.communication_dir), config_file)
        
        # Monitoring configuration
        self.heartbeat_timeout = 60  # seconds
        self.check_interval = 10     # seconds
        self.startup_delay = 5       # seconds between agent starts
        
        # Track agent blockers
        self.agent_blockers: Dict[str, Set[str]] = {agent: set() for agent in self.agents}
        self.agent_dependencies: Dict[str, Set[str]] = {agent: set() for agent in self.agents}
        
    def _load_agents(self) -> List[str]:
        """Load agent list from configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                current_theme = config.get('current_theme', 'greek_letters')
                agent_count = config.get('agent_count', 6)
                
                if current_theme in config.get('themes', {}):
                    agents = config['themes'][current_theme]['agents'][:agent_count]
                    return agents
        except Exception as e:
            logger.warning(f"Error loading agent config: {e}")
        
        return ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
    
    def _load_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load status from agent's status file"""
        status_file = self.status_dir / f"{agent_id}_status.json"
        try:
            if status_file.exists():
                with open(status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading status for {agent_id}: {e}")
        return None
    
    def _update_blockers_from_status(self):
        """Update blocker information from agent status files"""
        for agent_id in self.agents:
            status = self._load_agent_status(agent_id)
            if not status:
                continue
            
            # Clear existing blockers
            self.agent_blockers[agent_id].clear()
            
            # Check for blockers in status file
            if "blockers" in status:
                current_blockers = status.get("blockers", [])
                if isinstance(current_blockers, dict):
                    current_blockers = current_blockers.get("current", [])
                
                for blocker in current_blockers:
                    if isinstance(blocker, str):
                        self.agent_blockers[agent_id].add(blocker)
                    elif isinstance(blocker, dict):
                        blocker_text = blocker.get("description", blocker.get("blocker", ""))
                        self.agent_blockers[agent_id].add(blocker_text)
            
            # Check for dependencies
            if "dependencies" in status:
                deps = status.get("dependencies", [])
                self.agent_dependencies[agent_id] = set(deps)
    
    def _is_agent_blocked(self, agent_id: str) -> bool:
        """Check if agent has any active blockers"""
        return len(self.agent_blockers.get(agent_id, set())) > 0
    
    def _are_dependencies_met(self, agent_id: str) -> bool:
        """Check if all agent dependencies are satisfied"""
        deps = self.agent_dependencies.get(agent_id, set())
        if not deps:
            return True
        
        # Check if dependency agents are running and not blocked
        for dep in deps:
            if ":" in dep:
                # Format: "agent:task" - check if specific task is completed
                dep_agent, dep_task = dep.split(":", 1)
                if not self._is_task_completed(dep_agent, dep_task):
                    return False
            else:
                # Just agent name - check if agent is running
                if dep not in self.processes or not self.processes[dep].is_running():
                    return False
        
        return True
    
    def _is_task_completed(self, agent_id: str, task_name: str) -> bool:
        """Check if a specific task is completed by an agent"""
        status = self._load_agent_status(agent_id)
        if not status:
            return False
        
        # Check in completed activities
        activities = status.get("activities", {})
        completed = activities.get("completed", [])
        
        return any(task_name.lower() in str(activity).lower() for activity in completed)
    
    def start_agent(self, agent_id: str) -> bool:
        """Start an agent process"""
        if agent_id in self.processes and self.processes[agent_id].is_running():
            logger.info(f"Agent {agent_id} is already running")
            return True
        
        # Check if startup script exists
        startup_script = f"./start_agent_{agent_id}.sh"
        if not os.path.exists(startup_script):
            logger.error(f"Startup script not found: {startup_script}")
            return False
        
        try:
            # Send lifecycle control message
            channel = CommunicationChannel(agent_id, str(self.communication_dir))
            channel.update_lifecycle(AgentStatus.STARTING)
            
            start_msg = Message(
                from_id="lifecycle_manager",
                to_id=agent_id,
                msg_type=MessageType.LIFECYCLE_CONTROL,
                payload={
                    "action": "start",
                    "reason": "Dependencies met, no blockers",
                    "scheduled_time": datetime.now().isoformat()
                }
            )
            channel.send_message(start_msg)
            
            # Start the agent process
            logger.info(f"Starting agent {agent_id}")
            process = subprocess.Popen(
                [startup_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            self.processes[agent_id] = AgentProcess(agent_id, process.pid)
            
            # Update lifecycle status
            channel.update_lifecycle(AgentStatus.RUNNING)
            
            logger.info(f"Agent {agent_id} started with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return False
    
    def stop_agent(self, agent_id: str, reason: str = "Blocked") -> bool:
        """Stop an agent process"""
        if agent_id not in self.processes:
            logger.info(f"Agent {agent_id} is not running")
            return True
        
        agent_process = self.processes[agent_id]
        if not agent_process.is_running():
            logger.info(f"Agent {agent_id} process already stopped")
            del self.processes[agent_id]
            return True
        
        try:
            # Send lifecycle control message
            channel = CommunicationChannel(agent_id, str(self.communication_dir))
            
            stop_msg = Message(
                from_id="lifecycle_manager",
                to_id=agent_id,
                msg_type=MessageType.LIFECYCLE_CONTROL,
                payload={
                    "action": "stop",
                    "reason": reason,
                    "scheduled_time": datetime.now().isoformat()
                }
            )
            channel.send_message(stop_msg)
            
            # Update lifecycle status
            channel.update_lifecycle(AgentStatus.STOPPING, {"reason": reason})
            
            # Give agent time to shutdown gracefully
            time.sleep(2)
            
            # Terminate the process group
            if agent_process.pid:
                try:
                    os.killpg(os.getpgid(agent_process.pid), signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to agent {agent_id} (PID {agent_process.pid})")
                    
                    # Wait for graceful shutdown
                    time.sleep(3)
                    
                    # Force kill if still running
                    if agent_process.is_running():
                        os.killpg(os.getpgid(agent_process.pid), signal.SIGKILL)
                        logger.warning(f"Force killed agent {agent_id}")
                except ProcessLookupError:
                    pass
            
            # Update lifecycle status
            channel.update_lifecycle(AgentStatus.STOPPED, {"reason": reason})
            
            del self.processes[agent_id]
            logger.info(f"Agent {agent_id} stopped: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    def check_heartbeats(self):
        """Check agent heartbeats and restart unresponsive agents"""
        current_time = datetime.now()
        
        for agent_id in self.agents:
            if agent_id not in self.processes:
                continue
            
            # Check heartbeat file
            heartbeat_file = self.communication_dir / agent_id / "status" / "heartbeat.json"
            if heartbeat_file.exists():
                try:
                    with open(heartbeat_file, 'r') as f:
                        heartbeat = json.load(f)
                    
                    last_activity = datetime.fromisoformat(
                        heartbeat.get("payload", {}).get("last_activity", "")
                            .replace("Z", "+00:00")
                    )
                    
                    # Check if heartbeat is stale
                    if (current_time - last_activity.replace(tzinfo=None)).seconds > self.heartbeat_timeout:
                        logger.warning(f"Agent {agent_id} heartbeat timeout")
                        self.stop_agent(agent_id, "Heartbeat timeout")
                        
                except Exception as e:
                    logger.error(f"Error checking heartbeat for {agent_id}: {e}")
    
    def manage_lifecycle(self):
        """Main lifecycle management loop iteration"""
        # Update blocker information
        self._update_blockers_from_status()
        
        # Route any pending messages
        self.dispatcher.route_messages()
        
        # Check heartbeats
        self.check_heartbeats()
        
        # Manage each agent
        for agent_id in self.agents:
            is_running = agent_id in self.processes and self.processes[agent_id].is_running()
            is_blocked = self._is_agent_blocked(agent_id)
            deps_met = self._are_dependencies_met(agent_id)
            
            if is_running and is_blocked:
                # Stop blocked agents
                logger.info(f"Agent {agent_id} is blocked, stopping...")
                self.stop_agent(agent_id, f"Blocked: {list(self.agent_blockers[agent_id])}")
                
            elif not is_running and not is_blocked and deps_met:
                # Start unblocked agents with met dependencies
                logger.info(f"Agent {agent_id} is unblocked with dependencies met, starting...")
                self.start_agent(agent_id)
                time.sleep(self.startup_delay)  # Stagger agent starts
            
            elif not is_running and not deps_met:
                logger.debug(f"Agent {agent_id} waiting for dependencies: {self.agent_dependencies[agent_id]}")
    
    def run(self):
        """Run the lifecycle manager"""
        logger.info("Starting Agent Lifecycle Manager")
        logger.info(f"Managing agents: {self.agents}")
        
        try:
            while True:
                self.manage_lifecycle()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Lifecycle Manager")
            
            # Stop all running agents
            for agent_id in list(self.processes.keys()):
                self.stop_agent(agent_id, "Lifecycle manager shutdown")
            
            logger.info("Lifecycle Manager stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Lifecycle Manager')
    parser.add_argument('--config-file', default='agent_config.json',
                       help='Agent configuration file')
    parser.add_argument('--status-dir', default='agent_status',
                       help='Agent status directory')
    parser.add_argument('--communication-dir', default='agent_communication',
                       help='Agent communication directory')
    parser.add_argument('--check-interval', type=int, default=10,
                       help='Check interval in seconds')
    parser.add_argument('--heartbeat-timeout', type=int, default=60,
                       help='Heartbeat timeout in seconds')
    
    args = parser.parse_args()
    
    manager = LifecycleManager(
        config_file=args.config_file,
        status_dir=args.status_dir,
        communication_dir=args.communication_dir
    )
    
    manager.check_interval = args.check_interval
    manager.heartbeat_timeout = args.heartbeat_timeout
    
    manager.run()

if __name__ == '__main__':
    main()