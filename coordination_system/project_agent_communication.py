#!/usr/bin/env python3
"""
Project-Aware Agent Communication System
Implements bidirectional communication with project isolation.
"""

import json
import os
import time
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import fcntl
import tempfile
import shutil
from enum import Enum

from agent_communication import (
    Message, MessageType, Priority, AgentStatus, 
    CommunicationChannel, CentralDispatcher
)
from project_manager import ProjectManager, Project, ProjectStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectMessage(Message):
    """Extended Message with project context"""
    
    def __init__(self, from_id: str, to_id: str, msg_type: MessageType,
                 payload: Dict[str, Any], project_id: str,
                 priority: Priority = Priority.NORMAL,
                 requires_ack: bool = True, correlation_id: Optional[str] = None):
        super().__init__(from_id, to_id, msg_type, payload, priority, requires_ack, correlation_id)
        self.project_id = project_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary with project context"""
        data = super().to_dict()
        data["project_id"] = self.project_id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMessage':
        """Create message from dictionary"""
        msg = cls.__new__(cls)
        msg.id = data["id"]
        msg.timestamp = data["timestamp"]
        msg.from_id = data["from"]
        msg.to_id = data["to"]
        msg.type = data["type"]
        msg.priority = data["priority"]
        msg.payload = data["payload"]
        msg.requires_ack = data.get("requires_ack", True)
        msg.correlation_id = data.get("correlation_id")
        msg.project_id = data.get("project_id", "")
        return msg

class ProjectCommunicationChannel(CommunicationChannel):
    """Communication channel with project isolation"""
    
    def __init__(self, agent_id: str, project_id: str, base_dir: str):
        """Initialize channel within project workspace"""
        self.project_id = project_id
        # Use project-specific communication directory
        project_base = Path(base_dir) / "projects" / project_id / "agent_communication"
        super().__init__(agent_id, str(project_base))
        
        # Track which project this channel belongs to
        self.project_marker_file = self.agent_dir / "project.json"
        self._mark_project()
    
    def _mark_project(self):
        """Mark this channel as belonging to a specific project"""
        project_info = {
            "project_id": self.project_id,
            "agent_id": self.agent_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self._write_json_file(self.project_marker_file, project_info)
    
    def send_message(self, message: Message) -> bool:
        """Send message with project validation"""
        # Convert to ProjectMessage if needed
        if not isinstance(message, ProjectMessage):
            message = ProjectMessage(
                from_id=message.from_id,
                to_id=message.to_id,
                msg_type=MessageType(message.type),
                payload=message.payload,
                project_id=self.project_id,
                priority=Priority(message.priority),
                requires_ack=message.requires_ack,
                correlation_id=message.correlation_id
            )
        
        # Validate project context
        if hasattr(message, 'project_id') and message.project_id != self.project_id:
            logger.warning(f"Message project mismatch: {message.project_id} != {self.project_id}")
            return False
        
        return super().send_message(message)

class ProjectCentralDispatcher(CentralDispatcher):
    """Central dispatcher with project awareness"""
    
    def __init__(self, project_manager: ProjectManager,
                 base_dir: str = ".", 
                 config_file: str = "agent_config.json"):
        self.project_manager = project_manager
        self.base_dir = Path(base_dir)
        self.config_file = config_file
        
        # Track agents by project
        self.project_agents: Dict[str, List[str]] = {}
        self.agent_projects: Dict[str, str] = {}
        self.project_channels: Dict[str, Dict[str, ProjectCommunicationChannel]] = {}
        
        # Initialize channels for all projects
        self._initialize_project_channels()
    
    def _initialize_project_channels(self):
        """Initialize communication channels for all active projects"""
        for project in self.project_manager.list_projects(ProjectStatus.ACTIVE):
            self._initialize_project(project)
    
    def _initialize_project(self, project: Project):
        """Initialize channels for a specific project"""
        project_id = project.project_id
        workspace = self.project_manager.get_project_workspace(project_id)
        
        if not workspace:
            logger.warning(f"No workspace found for project {project_id}")
            return
        
        # Load project configuration
        config_file = workspace / "config.json"
        if not config_file.exists():
            logger.warning(f"No config found for project {project_id}")
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        theme = config.get('theme', 'ocean_creatures')
        agent_count = project.agent_count
        
        # Get agent names from main config
        main_config_path = self.base_dir / self.config_file
        if main_config_path.exists():
            with open(main_config_path, 'r') as f:
                main_config = json.load(f)
            
            if theme in main_config.get('themes', {}):
                agent_names = main_config['themes'][theme]['agents'][:agent_count]
                
                # Create project-specific agent IDs
                project_agents = []
                channels = {}
                
                for i, agent_name in enumerate(agent_names):
                    agent_id = f"{project_id}_agent_{i+1}"
                    project_agents.append(agent_id)
                    
                    # Create channel
                    channel = ProjectCommunicationChannel(
                        agent_id=agent_id,
                        project_id=project_id,
                        base_dir=str(self.base_dir)
                    )
                    channels[agent_id] = channel
                    
                    # Track associations
                    self.agent_projects[agent_id] = project_id
                
                self.project_agents[project_id] = project_agents
                self.project_channels[project_id] = channels
                
                logger.info(f"Initialized {len(project_agents)} agents for project {project.name}")
    
    def route_messages(self, cross_project_allowed: bool = False):
        """Route messages with project isolation"""
        routed_count = 0
        
        # Process messages for each project
        for project_id, channels in self.project_channels.items():
            for agent_id, channel in channels.items():
                lock_fd = channel._acquire_lock(channel.outbox_file)
                if lock_fd is None:
                    continue
                
                try:
                    outbox = channel._read_json_file(channel.outbox_file) or {"messages": []}
                    if not outbox["messages"]:
                        continue
                    
                    # Process each message
                    processed_messages = []
                    for msg_data in outbox["messages"]:
                        # Create ProjectMessage
                        message = ProjectMessage.from_dict(msg_data)
                        
                        # Validate project context
                        if not cross_project_allowed and hasattr(message, 'project_id'):
                            recipient_project = self.agent_projects.get(message.to_id)
                            if recipient_project and recipient_project != message.project_id:
                                logger.warning(
                                    f"Blocked cross-project message from {message.from_id} "
                                    f"to {message.to_id} (different projects)"
                                )
                                processed_messages.append(msg_data)
                                continue
                        
                        # Route to recipient
                        if message.to_id == "central":
                            # Handle central messages
                            self._handle_central_message(message)
                            processed_messages.append(msg_data)
                        elif message.to_id in self.agent_projects:
                            # Route to another agent in same project
                            recipient_project = self.agent_projects[message.to_id]
                            if recipient_project == project_id or cross_project_allowed:
                                recipient_channel = self.project_channels[recipient_project][message.to_id]
                                if self._deliver_message(recipient_channel, message):
                                    processed_messages.append(msg_data)
                                    routed_count += 1
                        else:
                            logger.warning(f"Unknown recipient: {message.to_id}")
                            processed_messages.append(msg_data)
                    
                    # Remove processed messages from outbox
                    remaining = [msg for msg in outbox["messages"] 
                               if msg not in processed_messages]
                    channel._write_json_file(channel.outbox_file, {"messages": remaining})
                    
                    # Archive sent messages
                    if processed_messages:
                        sent_file = channel.sent_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        channel._write_json_file(sent_file, {"messages": processed_messages})
                    
                finally:
                    channel._release_lock(lock_fd, channel.outbox_file)
        
        if routed_count > 0:
            logger.info(f"Routed {routed_count} messages")
        
        return routed_count
    
    def broadcast_to_project(self, project_id: str, message: Message):
        """Broadcast message to all agents in a project"""
        if project_id not in self.project_agents:
            logger.warning(f"Unknown project: {project_id}")
            return
        
        broadcasted = 0
        for agent_id in self.project_agents[project_id]:
            if agent_id != message.from_id:  # Don't send to sender
                channel = self.project_channels[project_id][agent_id]
                if self._deliver_message(channel, message):
                    broadcasted += 1
        
        logger.info(f"Broadcasted message to {broadcasted} agents in project {project_id}")
        return broadcasted
    
    def get_project_agent_statuses(self, project_id: str) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents in a project"""
        statuses = {}
        
        if project_id not in self.project_channels:
            return statuses
        
        for agent_id, channel in self.project_channels[project_id].items():
            # Read lifecycle status
            lifecycle = channel._read_json_file(channel.lifecycle_file)
            
            # Read last heartbeat
            heartbeat = channel._read_json_file(channel.heartbeat_file)
            
            statuses[agent_id] = {
                "project_id": project_id,
                "lifecycle": lifecycle,
                "heartbeat": heartbeat,
                "last_seen": heartbeat["timestamp"] if heartbeat else None
            }
        
        return statuses
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get status of all agents grouped by project"""
        all_statuses = {}
        
        for project_id in self.project_channels:
            all_statuses[project_id] = self.get_project_agent_statuses(project_id)
        
        return all_statuses

def main():
    """CLI interface for project communication testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Agent Communication System')
    parser.add_argument('--test-isolation', action='store_true', 
                       help='Test project isolation')
    parser.add_argument('--route', action='store_true',
                       help='Route messages')
    parser.add_argument('--status', action='store_true',
                       help='Show agent statuses')
    
    args = parser.parse_args()
    
    # Initialize project manager
    project_manager = ProjectManager()
    
    # Create dispatcher
    dispatcher = ProjectCentralDispatcher(project_manager)
    
    if args.test_isolation:
        print("Testing project isolation...")
        # Would implement test scenarios here
        print("Test not yet implemented")
    
    if args.route:
        count = dispatcher.route_messages(cross_project_allowed=False)
        print(f"Routed {count} messages")
    
    if args.status:
        statuses = dispatcher.get_all_agent_statuses()
        for project_id, agents in statuses.items():
            project = project_manager.get_project(project_id)
            if project:
                print(f"\nProject: {project.name} ({project_id})")
                for agent_id, status in agents.items():
                    lifecycle = status.get('lifecycle', {}).get('status', 'unknown')
                    print(f"  {agent_id}: {lifecycle}")

if __name__ == '__main__':
    main()