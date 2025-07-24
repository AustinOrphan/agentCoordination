#!/usr/bin/env python3
"""
Project-Aware Agent Lifecycle Manager
Manages agent lifecycles with project context and global task pool integration.
"""

import json
import os
import time
import subprocess
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from enum import Enum
import signal
import psutil

from agent_communication import (
    Message, MessageType, Priority, AgentStatus
)
from project_agent_communication import (
    ProjectCommunicationChannel, ProjectCentralDispatcher, ProjectMessage
)
from task_communicator import TaskCommunicator
from project_manager import ProjectManager, Project, ProjectStatus
from global_task_pool import GlobalTaskPoolManager, PoolMode
from task_assignment_manager import TaskStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectAgentProcess:
    """Represents a running agent process with project context"""
    
    def __init__(self, agent_id: str, project_id: str, pid: Optional[int] = None):
        self.agent_id = agent_id
        self.project_id = project_id
        self.pid = pid
        self.start_time = datetime.now()
        self.status = AgentStatus.STOPPED
        self.current_task_id = None
    
    def is_running(self) -> bool:
        """Check if process is still running"""
        if self.pid is None:
            return False
        
        try:
            process = psutil.Process(self.pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

class ProjectLifecycleManager:
    """Project-aware lifecycle manager with global task pool integration"""
    
    def __init__(self, project_manager: ProjectManager, 
                 project_id: Optional[str] = None,
                 pool_mode: PoolMode = PoolMode.GLOBAL_PRIORITY):
        self.project_manager = project_manager
        self.project_id = project_id
        self.project = None
        if project_id:
            self.project = project_manager.get_project(project_id)
        
        # Initialize global task pool
        self.global_pool = GlobalTaskPoolManager(project_manager, pool_mode)
        
        # Track processes across all projects
        self.processes: Dict[str, ProjectAgentProcess] = {}
        self.last_start_time: Dict[str, datetime] = {}
        
        # Project-specific directories
        if self.project:
            self.project_workspace = Path(f"projects/{project_id}")
            self.status_dir = self.project_workspace / "agent_status"
            self.communication_dir = self.project_workspace / "agent_communication"
            self.task_dir = self.project_workspace / "task_assignments"
        else:
            # Global mode - use main directories
            self.status_dir = Path("agent_status")
            self.communication_dir = Path("agent_communication")
            self.task_dir = Path("task_assignments")
        
        # Initialize project-aware dispatcher
        self.dispatcher = ProjectCentralDispatcher(
            self.project_manager,
            str(self.project_manager.base_dir),
            "agent_config.json"
        )
        
        # Monitoring configuration
        self.heartbeat_timeout = 60  # seconds
        self.check_interval = 10     # seconds
        self.startup_delay = 5       # seconds between agent starts
        self.task_check_interval = 30  # seconds
        self.last_task_check = datetime.now()
        
        # Agent management
        self.agent_blockers: Dict[str, Set[str]] = {}
        self.agent_projects: Dict[str, str] = {}  # agent_id -> project_id
        self.project_agents: Dict[str, Set[str]] = {}  # project_id -> agent_ids
        
    def _get_available_agents(self) -> List[str]:
        """Get list of available agents based on pool mode"""
        if self.global_pool.pool_mode == PoolMode.GLOBAL_PRIORITY:
            # In global mode, get all agents from all active projects
            all_agents = []
            for project in self.project_manager.list_projects(ProjectStatus.ACTIVE):
                # Get agents for this project
                config_file = self.project_manager.get_project_workspace(project.project_id) / "config.json"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    theme = config.get('theme', 'ocean_creatures')
                    agent_count = project.agent_count
                    
                    # Load theme agents
                    main_config = Path("agent_config.json")
                    if main_config.exists():
                        with open(main_config, 'r') as f:
                            main_cfg = json.load(f)
                        if theme in main_cfg.get('themes', {}):
                            agents = main_cfg['themes'][theme]['agents'][:agent_count]
                            for i, agent in enumerate(agents):
                                agent_id = f"{project.project_id}_agent_{i+1}"
                                all_agents.append(agent_id)
                                self.agent_projects[agent_id] = project.project_id
                                
                                if project.project_id not in self.project_agents:
                                    self.project_agents[project.project_id] = set()
                                self.project_agents[project.project_id].add(agent_id)
            
            return all_agents
            
        elif self.project and self.global_pool.pool_mode == PoolMode.PROJECT_DEDICATED:
            # In dedicated mode, only use agents from specific project
            agents = []
            project_id = self.project.project_id
            for i in range(self.project.agent_count):
                agent_id = f"{project_id}_agent_{i+1}"
                agents.append(agent_id)
                self.agent_projects[agent_id] = project_id
                
                if project_id not in self.project_agents:
                    self.project_agents[project_id] = set()
                self.project_agents[project_id].add(agent_id)
            
            return agents
        
        return []
    
    def _load_project_agent_status(self, agent_id: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Load status from project-specific agent status file"""
        workspace = self.project_manager.get_project_workspace(project_id)
        if not workspace:
            return None
            
        status_file = workspace / "agent_status" / f"{agent_id}_status.json"
        try:
            if status_file.exists():
                with open(status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading status for {agent_id} in project {project_id}: {e}")
        return None
    
    def _update_blockers_from_status(self):
        """Update blocker information from agent status files across projects"""
        for agent_id in self._get_available_agents():
            project_id = self.agent_projects.get(agent_id)
            if not project_id:
                continue
                
            status = self._load_project_agent_status(agent_id, project_id)
            if not status:
                continue
            
            # Clear existing blockers
            if agent_id not in self.agent_blockers:
                self.agent_blockers[agent_id] = set()
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
    
    def _is_agent_blocked(self, agent_id: str) -> bool:
        """Check if agent has any active blockers"""
        return len(self.agent_blockers.get(agent_id, set())) > 0
    
    def _should_start_agent(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if an agent should be started and for which project
        Returns: (should_start, project_id)
        """
        # Check if agent is already running
        if agent_id in self.processes and self.processes[agent_id].is_running():
            return False, None
        
        # Check if agent is blocked
        if self._is_agent_blocked(agent_id):
            return False, None
        
        # In global priority mode, check global task assignments
        if self.global_pool.pool_mode == PoolMode.GLOBAL_PRIORITY:
            # Check if this agent has been assigned tasks from global pool
            assignments_file = Path("coordination_system/global_assignments.json")
            if assignments_file.exists():
                try:
                    with open(assignments_file, 'r') as f:
                        data = json.load(f)
                    
                    active_assignments = data.get('active_assignments', [])
                    for assignment in active_assignments:
                        if assignment.get('agent_id') == agent_id:
                            return True, assignment.get('project_id')
                except Exception as e:
                    logger.error(f"Error checking global assignments: {e}")
        
        # In dedicated mode, check project-specific tasks
        elif self.project:
            project_id = self.agent_projects.get(agent_id)
            if project_id:
                # Check if there are pending tasks in this project
                workspace = self.project_manager.get_project_workspace(project_id)
                if workspace:
                    task_file = workspace / "task_assignments" / "task_queue.json"
                    if task_file.exists():
                        try:
                            with open(task_file, 'r') as f:
                                task_data = json.load(f)
                            
                            pending_tasks = [
                                t for t in task_data.get('tasks', [])
                                if t.get('status') in ['pending', 'assigned']
                            ]
                            
                            if pending_tasks:
                                return True, project_id
                        except Exception:
                            pass
        
        return False, None
    
    def start_agent(self, agent_id: str, project_id: str) -> bool:
        """Start an agent process with project context"""
        # Check if agent is already running
        if agent_id in self.processes:
            if self.processes[agent_id].is_running():
                logger.info(f"Agent {agent_id} is already running (PID: {self.processes[agent_id].pid})")
                return True
            else:
                # Process exists but not running - clean it up
                logger.info(f"Cleaning up dead process for agent {agent_id}")
                del self.processes[agent_id]
        
        # Check cooldown period
        cooldown_seconds = 30
        if agent_id in self.last_start_time:
            time_since_last_start = (datetime.now() - self.last_start_time[agent_id]).total_seconds()
            if time_since_last_start < cooldown_seconds:
                logger.info(f"Agent {agent_id} in cooldown period ({time_since_last_start:.1f}s)")
                return False
        
        # Get project workspace
        workspace = self.project_manager.get_project_workspace(project_id)
        if not workspace:
            logger.error(f"Project workspace not found for {project_id}")
            return False
        
        # Check if startup script exists
        startup_script = workspace / f"start_agent_{agent_id}.sh"
        if not startup_script.exists():
            # Try main directory
            startup_script = Path(f"./start_agent_{agent_id}.sh")
            if not startup_script.exists():
                logger.error(f"Startup script not found: {startup_script}")
                return False
        
        try:
            # Create project-specific communication channel
            channel = ProjectCommunicationChannel(
                agent_id=agent_id,
                project_id=project_id,
                base_dir=str(self.project_manager.base_dir)
            )
            channel.update_lifecycle(AgentStatus.STARTING)
            
            start_msg = ProjectMessage(
                from_id="project_lifecycle_manager",
                to_id=agent_id,
                msg_type=MessageType.LIFECYCLE_CONTROL,
                payload={
                    "action": "start",
                    "reason": "Task assignment from global pool",
                    "scheduled_time": datetime.now().isoformat()
                },
                project_id=project_id
            )
            channel.send_message(start_msg)
            
            # Set environment variables for project context
            env = os.environ.copy()
            env['PROJECT_ID'] = project_id
            env['PROJECT_WORKSPACE'] = str(workspace)
            env['AGENT_ID'] = agent_id
            
            # Start the agent process
            logger.info(f"Starting agent {agent_id} for project {project_id}")
            process = subprocess.Popen(
                [str(startup_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
                env=env,
                cwd=str(workspace)  # Run in project workspace
            )
            
            self.processes[agent_id] = ProjectAgentProcess(agent_id, project_id, process.pid)
            self.last_start_time[agent_id] = datetime.now()
            
            # Update lifecycle status
            channel.update_lifecycle(AgentStatus.RUNNING)
            
            logger.info(f"Agent {agent_id} started with PID {process.pid} for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return False
    
    def stop_agent(self, agent_id: str, reason: str = "Task completed") -> bool:
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
            # Get project workspace
            project_id = agent_process.project_id
            workspace = self.project_manager.get_project_workspace(project_id)
            if not workspace:
                workspace = Path(".")
            
            # Send lifecycle control message
            channel = ProjectCommunicationChannel(
                agent_id=agent_id,
                project_id=project_id,
                base_dir=str(self.project_manager.base_dir)
            )
            
            stop_msg = ProjectMessage(
                from_id="project_lifecycle_manager",
                to_id=agent_id,
                msg_type=MessageType.LIFECYCLE_CONTROL,
                payload={
                    "action": "stop",
                    "reason": reason,
                    "scheduled_time": datetime.now().isoformat()
                },
                project_id=project_id
            )
            channel.send_message(stop_msg)
            
            # Update lifecycle status
            channel.update_lifecycle(AgentStatus.STOPPING, {"reason": reason})
            
            # Give agent time to shutdown gracefully
            time.sleep(2)
            
            # Terminate the process
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
    
    def process_global_task_assignments(self):
        """Process task assignments from global pool"""
        try:
            # Get new assignments from global pool
            logger.info("Processing global task assignments...")
            assignments = self.global_pool.assign_next_tasks()
            
            if assignments:
                logger.info(f"Made {len(assignments)} global task assignments")
                
                # Start agents for their assigned tasks
                for assignment in assignments:
                    agent_id = assignment['agent_id']
                    project_id = assignment['project_id']
                    
                    # Check if agent needs to be started
                    if agent_id not in self.processes or not self.processes[agent_id].is_running():
                        logger.info(f"Starting {agent_id} for task in project {project_id}")
                        self.start_agent(agent_id, project_id)
                        time.sleep(self.startup_delay)
                    
                    # Update agent's current task
                    if agent_id in self.processes:
                        self.processes[agent_id].current_task_id = assignment['task_id']
            
        except Exception as e:
            logger.error(f"Error processing global task assignments: {e}")
    
    def check_heartbeats(self):
        """Check agent heartbeats across all projects"""
        current_time = datetime.now()
        
        for agent_id, process in list(self.processes.items()):
            if not process.is_running():
                continue
            
            # Get project workspace
            workspace = self.project_manager.get_project_workspace(process.project_id)
            if not workspace:
                continue
            
            # Check heartbeat file
            heartbeat_file = workspace / "agent_communication" / agent_id / "status" / "heartbeat.json"
            if heartbeat_file.exists():
                try:
                    with open(heartbeat_file, 'r') as f:
                        heartbeat = json.load(f)
                    
                    last_activity_str = heartbeat.get("payload", {}).get("last_activity", "")
                    if not last_activity_str:
                        continue
                    
                    last_activity = datetime.fromisoformat(
                        last_activity_str.replace("Z", "+00:00")
                    )
                    
                    # Check if heartbeat is stale
                    if (current_time - last_activity.replace(tzinfo=None)).seconds > self.heartbeat_timeout:
                        logger.warning(f"Agent {agent_id} heartbeat timeout")
                        self.stop_agent(agent_id, "Heartbeat timeout")
                        
                except Exception as e:
                    logger.error(f"Error checking heartbeat for {agent_id}: {e}")
    
    def manage_lifecycle(self):
        """Main lifecycle management loop iteration with project awareness"""
        # Update blocker information
        self._update_blockers_from_status()
        
        # Route any pending messages
        if self.project:
            self.dispatcher.route_messages()
        
        # Check heartbeats
        self.check_heartbeats()
        
        # Process global task assignments periodically
        current_time = datetime.now()
        if (current_time - self.last_task_check).seconds >= self.task_check_interval:
            if self.global_pool.pool_mode == PoolMode.GLOBAL_PRIORITY:
                self.process_global_task_assignments()
            self.last_task_check = current_time
        
        # Manage each agent
        for agent_id in self._get_available_agents():
            is_running = agent_id in self.processes and self.processes[agent_id].is_running()
            is_blocked = self._is_agent_blocked(agent_id)
            should_start, target_project = self._should_start_agent(agent_id)
            
            if is_running and is_blocked:
                # Stop blocked agents
                logger.info(f"Agent {agent_id} is blocked, stopping...")
                self.stop_agent(agent_id, f"Blocked: {list(self.agent_blockers[agent_id])}")
                
            elif not is_running and should_start and target_project:
                # Start agents that should be working
                logger.info(f"Agent {agent_id} should start for project {target_project}...")
                self.start_agent(agent_id, target_project)
                time.sleep(self.startup_delay)  # Stagger agent starts
            
            elif not is_running and is_blocked:
                logger.debug(f"Agent {agent_id} blocked, not starting: {self.agent_blockers[agent_id]}")
    
    def run(self):
        """Run the project-aware lifecycle manager"""
        logger.info("Starting Project-Aware Agent Lifecycle Manager")
        logger.info(f"Pool mode: {self.global_pool.pool_mode.value}")
        if self.project:
            logger.info(f"Managing project: {self.project.name} ({self.project.project_id})")
        else:
            logger.info("Managing all projects in global mode")
        
        try:
            while True:
                self.manage_lifecycle()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Project Lifecycle Manager")
            
            # Stop all running agents
            for agent_id in list(self.processes.keys()):
                self.stop_agent(agent_id, "Lifecycle manager shutdown")
            
            logger.info("Project Lifecycle Manager stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project-Aware Agent Lifecycle Manager')
    parser.add_argument('--project', help='Project ID to manage (omit for global mode)')
    parser.add_argument('--pool-mode', choices=['global_priority', 'project_dedicated', 'hybrid'],
                       default='global_priority', help='Agent pool assignment mode')
    parser.add_argument('--create-tasks', action='store_true',
                       help='Create sample tasks before starting')
    
    args = parser.parse_args()
    
    # Initialize project manager
    project_manager = ProjectManager()
    
    # Determine pool mode
    pool_mode = PoolMode(args.pool_mode)
    
    # Create lifecycle manager
    manager = ProjectLifecycleManager(
        project_manager=project_manager,
        project_id=args.project,
        pool_mode=pool_mode
    )
    
    if args.create_tasks and args.project:
        logger.info(f"Creating sample tasks for project {args.project}...")
        # Implementation would create project-specific tasks
        logger.info("Sample task creation not yet implemented")
    
    manager.run()

if __name__ == '__main__':
    main()