#!/usr/bin/env python3
"""
Agent Communication System
Implements bidirectional file-based communication between agents and central coordination.
"""

import json
import os
import time
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import fcntl
import tempfile
import shutil
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Valid message types in the system"""
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    BLOCKER_REPORT = "blocker_report"
    BLOCKER_RESOLVED = "blocker_resolved"
    INFO_REQUEST = "info_request"
    INFO_RESPONSE = "info_response"
    LIFECYCLE_CONTROL = "lifecycle_control"
    HEARTBEAT = "heartbeat"
    ACKNOWLEDGMENT = "acknowledgment"

class Priority(Enum):
    """Message priority levels"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class AgentStatus(Enum):
    """Agent lifecycle states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    WORKING = "working"
    BLOCKED = "blocked"
    STOPPING = "stopping"

class Message:
    """Represents a communication message"""
    
    def __init__(self, from_id: str, to_id: str, msg_type: MessageType, 
                 payload: Dict[str, Any], priority: Priority = Priority.NORMAL,
                 requires_ack: bool = True, correlation_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.from_id = from_id
        self.to_id = to_id
        self.type = msg_type.value
        self.priority = priority.value
        self.payload = payload
        self.requires_ack = requires_ack
        self.correlation_id = correlation_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "from": self.from_id,
            "to": self.to_id,
            "type": self.type,
            "priority": self.priority,
            "payload": self.payload,
            "requires_ack": self.requires_ack,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
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
        return msg

class CommunicationChannel:
    """Manages file-based communication for an agent"""
    
    def __init__(self, agent_id: str, base_dir: str = "agent_communication"):
        self.agent_id = agent_id
        self.base_dir = Path(base_dir)
        self.agent_dir = self.base_dir / agent_id
        
        # Create directory structure
        self.input_dir = self.agent_dir / "input"
        self.output_dir = self.agent_dir / "output"
        self.status_dir = self.agent_dir / "status"
        
        self.inbox_file = self.input_dir / "inbox.json"
        self.archive_dir = self.input_dir / "archive"
        self.outbox_file = self.output_dir / "outbox.json"
        self.sent_dir = self.output_dir / "sent"
        
        self.lifecycle_file = self.status_dir / "lifecycle.json"
        self.heartbeat_file = self.status_dir / "heartbeat.json"
        
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories"""
        for directory in [self.input_dir, self.output_dir, self.status_dir,
                         self.archive_dir, self.sent_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty inbox/outbox if they don't exist
        for file_path in [self.inbox_file, self.outbox_file]:
            if not file_path.exists():
                self._write_json_file(file_path, {"messages": []})
    
    def _acquire_lock(self, file_path: Path, timeout: float = 5.0) -> Optional[int]:
        """Acquire file lock with timeout"""
        lock_file = Path(f"{file_path}.lock")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return fd
            except FileExistsError:
                time.sleep(0.1)
        
        logger.warning(f"Failed to acquire lock for {file_path}")
        return None
    
    def _release_lock(self, fd: int, file_path: Path):
        """Release file lock"""
        lock_file = Path(f"{file_path}.lock")
        try:
            os.close(fd)
            lock_file.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
    
    def _read_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Safely read JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Safely write JSON file with atomic operation"""
        try:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                           dir=file_path.parent, delete=False) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = tmp.name
            
            # Atomic move
            shutil.move(tmp_path, file_path)
            return True
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
            return False
    
    def send_message(self, message: Message) -> bool:
        """Add message to outbox"""
        lock_fd = self._acquire_lock(self.outbox_file)
        if lock_fd is None:
            return False
        
        try:
            outbox = self._read_json_file(self.outbox_file) or {"messages": []}
            outbox["messages"].append(message.to_dict())
            success = self._write_json_file(self.outbox_file, outbox)
            
            if success:
                logger.info(f"Agent {self.agent_id} queued message {message.id} to {message.to_id}")
            
            return success
        finally:
            self._release_lock(lock_fd, self.outbox_file)
    
    def receive_messages(self) -> List[Message]:
        """Read all messages from inbox"""
        lock_fd = self._acquire_lock(self.inbox_file)
        if lock_fd is None:
            return []
        
        try:
            inbox = self._read_json_file(self.inbox_file) or {"messages": []}
            messages = [Message.from_dict(msg) for msg in inbox["messages"]]
            
            # Clear inbox after reading
            if messages:
                self._write_json_file(self.inbox_file, {"messages": []})
                
                # Archive messages
                archive_file = self.archive_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self._write_json_file(archive_file, {"messages": inbox["messages"]})
                
                logger.info(f"Agent {self.agent_id} received {len(messages)} messages")
            
            return messages
        finally:
            self._release_lock(lock_fd, self.inbox_file)
    
    def update_lifecycle(self, status: AgentStatus, details: Optional[Dict[str, Any]] = None):
        """Update agent lifecycle status"""
        lifecycle_data = {
            "agent_id": self.agent_id,
            "status": status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        
        self._write_json_file(self.lifecycle_file, lifecycle_data)
        logger.info(f"Agent {self.agent_id} lifecycle status: {status.value}")
    
    def send_heartbeat(self, status: AgentStatus, current_task: Optional[str] = None,
                      metrics: Optional[Dict[str, Any]] = None):
        """Send heartbeat signal"""
        heartbeat = Message(
            from_id=self.agent_id,
            to_id="central",
            msg_type=MessageType.HEARTBEAT,
            payload={
                "status": status.value,
                "current_task": current_task,
                "cpu_usage": metrics.get("cpu_usage", 0) if metrics else 0,
                "memory_usage": metrics.get("memory_usage", 0) if metrics else 0,
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            requires_ack=False
        )
        
        # Also update local heartbeat file for quick status checks
        self._write_json_file(self.heartbeat_file, heartbeat.to_dict())
        
        return self.send_message(heartbeat)
    
    def acknowledge_message(self, original_message: Message):
        """Send acknowledgment for a message"""
        ack = Message(
            from_id=self.agent_id,
            to_id=original_message.from_id,
            msg_type=MessageType.ACKNOWLEDGMENT,
            payload={"acknowledged_id": original_message.id},
            requires_ack=False,
            correlation_id=original_message.id
        )
        return self.send_message(ack)

class CentralDispatcher:
    """Central message routing and agent lifecycle management"""
    
    def __init__(self, base_dir: str = "agent_communication", 
                 config_file: str = "agent_config.json"):
        self.base_dir = Path(base_dir)
        self.config_file = config_file
        self.agents = self._load_agents()
        self.channels = {}
        
        # Initialize channels for all agents
        for agent in self.agents:
            self.channels[agent] = CommunicationChannel(agent, str(self.base_dir))
    
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
                    logger.info(f"Loaded {len(agents)} agents from theme '{current_theme}'")
                    return agents
        except Exception as e:
            logger.warning(f"Error loading agent config: {e}, using defaults")
        
        return ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
    
    def route_messages(self):
        """Route messages from agent outboxes to recipient inboxes"""
        routed_count = 0
        
        for agent_id, channel in self.channels.items():
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
                    message = Message.from_dict(msg_data)
                    
                    # Route to recipient
                    if message.to_id == "central":
                        # Handle central messages
                        self._handle_central_message(message)
                        processed_messages.append(msg_data)
                    elif message.to_id in self.channels:
                        # Route to another agent
                        recipient_channel = self.channels[message.to_id]
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
    
    def _deliver_message(self, channel: CommunicationChannel, message: Message) -> bool:
        """Deliver message to agent's inbox"""
        lock_fd = channel._acquire_lock(channel.inbox_file)
        if lock_fd is None:
            return False
        
        try:
            inbox = channel._read_json_file(channel.inbox_file) or {"messages": []}
            inbox["messages"].append(message.to_dict())
            success = channel._write_json_file(channel.inbox_file, inbox)
            
            if success:
                logger.info(f"Delivered message {message.id} to {message.to_id}")
            
            return success
        finally:
            channel._release_lock(lock_fd, channel.inbox_file)
    
    def _handle_central_message(self, message: Message):
        """Handle messages addressed to central system"""
        if message.type == MessageType.HEARTBEAT.value:
            # Update agent tracking
            logger.debug(f"Heartbeat from {message.from_id}")
        elif message.type == MessageType.STATUS_UPDATE.value:
            # Update coordination tracking
            logger.info(f"Status update from {message.from_id}: {message.payload}")
        elif message.type == MessageType.BLOCKER_REPORT.value:
            # Track blocker
            logger.warning(f"Blocker reported by {message.from_id}: {message.payload}")
        # Add more central message handling as needed
    
    def get_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all agents"""
        statuses = {}
        
        for agent_id, channel in self.channels.items():
            # Read lifecycle status
            lifecycle = channel._read_json_file(channel.lifecycle_file)
            
            # Read last heartbeat
            heartbeat = channel._read_json_file(channel.heartbeat_file)
            
            statuses[agent_id] = {
                "lifecycle": lifecycle,
                "heartbeat": heartbeat,
                "last_seen": heartbeat["timestamp"] if heartbeat else None
            }
        
        return statuses