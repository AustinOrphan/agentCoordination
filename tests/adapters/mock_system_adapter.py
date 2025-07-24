"""
Mock System Adapter

Provides a mock implementation of the coordination system for testing
without requiring the real system infrastructure.
"""

import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .base_adapter import BaseCoordinationAdapter, AdapterConfig, AdapterMode


@dataclass
class MockSystemConfig(AdapterConfig):
    """Configuration for mock system."""
    mode: AdapterMode = AdapterMode.MOCK
    simulate_delays: bool = True
    failure_rate: float = 0.0  # 0.0 = no failures, 1.0 = all operations fail
    max_agents: int = 12
    
    
class MockSystemAdapter(BaseCoordinationAdapter):
    """Mock adapter for testing without real system."""
    
    def __init__(self, config: MockSystemConfig):
        super().__init__(config)
        self.config = config
        self.temp_dir: Optional[Path] = None
        self.logger = logging.getLogger(__name__)
        
        # Mock state
        self.mock_authorities = {
            "critical_path": {"current_holder": None, "backup_holder": None},
            "migration": {"current_holder": None, "backup_holder": None},
            "dashboard": {"current_holder": None, "backup_holder": None},
            "devops": {"current_holder": None, "backup_holder": None},
            "security": {"current_holder": None, "backup_holder": None},
            "ux": {"current_holder": None, "backup_holder": None}
        }
        
        self.mock_messages: Dict[str, List[Dict[str, Any]]] = {}
        self.authority_counter = 1000
        
    def setup_test_environment(self) -> bool:
        """Setup mock test environment."""
        try:
            # Create temporary directory for mock files
            self.temp_dir = Path(tempfile.mkdtemp(prefix="mock_coordination_"))
            
            # Initialize mock agents
            self._initialize_mock_agents()
            
            # Setup mock authority state
            self.authority_state = {
                "assignments": [],
                "requests": [],
                "available": list(self.mock_authorities.keys())
            }
            
            # Initialize communication state
            for agent_name in self.active_agents:
                self.mock_messages[agent_name] = []
                
            self.logger.info(f"Mock system initialized with {len(self.active_agents)} agents")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup mock environment: {e}")
            return False
            
    def _initialize_mock_agents(self):
        """Initialize mock agents."""
        agent_names = ["dolphin", "shark", "whale", "jellyfish", "octopus", "seahorse"]
        
        for i, agent_name in enumerate(agent_names[:self.config.max_agents]):
            self.active_agents[agent_name] = {
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "last_update": datetime.now().isoformat(),
                "workload": 0,
                "expertise": self._get_mock_expertise(agent_name),
                "authorities": [],
                "blockers": []
            }
            
    def _get_mock_expertise(self, agent_name: str) -> List[str]:
        """Get mock expertise for agent."""
        expertise_map = {
            "dolphin": ["security", "backend"],
            "shark": ["backend", "performance"],
            "whale": ["architecture", "planning"],
            "jellyfish": ["frontend", "ux"],
            "octopus": ["devops", "infrastructure"],
            "seahorse": ["fullstack", "integration"]
        }
        return expertise_map.get(agent_name, ["general"])
        
    def _simulate_delay(self, operation: str = "default"):
        """Simulate realistic operation delays."""
        if not self.config.simulate_delays:
            return
            
        delays = {
            "status_read": 0.01,
            "status_write": 0.02,
            "authority_request": 0.1,
            "authority_release": 0.05,
            "message_send": 0.03,
            "message_read": 0.01,
            "agent_start": 1.0,
            "agent_stop": 0.5,
            "default": 0.01
        }
        
        delay = delays.get(operation, delays["default"])
        time.sleep(delay)
        
    def _should_simulate_failure(self) -> bool:
        """Check if operation should fail based on failure rate."""
        import random
        return random.random() < self.config.failure_rate
        
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get mock agent status."""
        self._simulate_delay("status_read")
        
        if self._should_simulate_failure():
            return None
            
        if agent_name not in self.active_agents:
            return None
            
        return self.active_agents[agent_name].copy()
        
    def update_agent_status(self, agent_name: str, status_data: Dict[str, Any]) -> bool:
        """Update mock agent status."""
        self._simulate_delay("status_write")
        
        if self._should_simulate_failure():
            return False
            
        if agent_name not in self.active_agents:
            return False
            
        self.active_agents[agent_name].update(status_data)
        self.active_agents[agent_name]["last_update"] = datetime.now().isoformat()
        return True
        
    def request_authority(self, agent_name: str, authority_type: str, domain: str, task: str) -> bool:
        """Mock authority request."""
        self._simulate_delay("authority_request")
        
        if self._should_simulate_failure():
            return False
            
        if agent_name not in self.active_agents:
            return False
            
        # Create authority assignment
        authority_id = f"AUTH-MOCK-{self.authority_counter}"
        self.authority_counter += 1
        
        assignment = {
            "id": authority_id,
            "agent": agent_name,
            "authority_type": authority_type,
            "domain": domain,
            "task": task,
            "granted_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=8)).isoformat(),
            "status": "active"
        }
        
        self.authority_state["assignments"].append(assignment)
        
        # Update agent authorities
        if authority_type not in self.active_agents[agent_name]["authorities"]:
            self.active_agents[agent_name]["authorities"].append(authority_type)
            
        return True
        
    def release_authority(self, agent_name: str, authority_id: str) -> bool:
        """Mock authority release."""
        self._simulate_delay("authority_release")
        
        if self._should_simulate_failure():
            return False
            
        # Find and update assignment
        for assignment in self.authority_state["assignments"]:
            if assignment["id"] == authority_id and assignment["agent"] == agent_name:
                assignment["status"] = "released"
                assignment["released_at"] = datetime.now().isoformat()
                
                # Remove from agent authorities
                authority_type = assignment["authority_type"]
                if authority_type in self.active_agents[agent_name]["authorities"]:
                    self.active_agents[agent_name]["authorities"].remove(authority_type)
                    
                return True
                
        return False
        
    def send_message(self, sender: str, recipient: str, message_type: str, content: Dict[str, Any]) -> bool:
        """Mock message sending."""
        self._simulate_delay("message_send")
        
        if self._should_simulate_failure():
            return False
            
        if recipient not in self.mock_messages:
            self.mock_messages[recipient] = []
            
        message = {
            "id": f"msg_mock_{int(time.time() * 1000)}",
            "sender": sender,
            "recipient": recipient,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        self.mock_messages[recipient].append(message)
        return True
        
    def get_messages(self, agent_name: str, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """Get mock messages."""
        self._simulate_delay("message_read")
        
        if self._should_simulate_failure():
            return []
            
        if agent_name not in self.mock_messages:
            return []
            
        messages = self.mock_messages[agent_name].copy()
        
        if mark_as_read:
            # Mark as processed
            for msg in self.mock_messages[agent_name]:
                msg["processed"] = True
                
        return messages
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get mock system metrics."""
        active_count = sum(1 for agent in self.active_agents.values() 
                          if agent["status"] == "active")
        
        total_workload = sum(agent.get("workload", 0) for agent in self.active_agents.values())
        avg_workload = total_workload / len(self.active_agents) if self.active_agents else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_agents": active_count,
            "total_agents": len(self.active_agents),
            "total_authorities": len(self.authority_state["assignments"]),
            "pending_requests": len(self.authority_state["requests"]),
            "system_load": avg_workload,
            "agents": {name: {
                "status": agent["status"],
                "workload": agent.get("workload", 0),
                "authorities": len(agent.get("authorities", []))
            } for name, agent in self.active_agents.items()}
        }
        
    def start_agent(self, agent_name: str) -> bool:
        """Mock agent startup."""
        self._simulate_delay("agent_start")
        
        if self._should_simulate_failure():
            return False
            
        if agent_name in self.active_agents:
            self.active_agents[agent_name]["status"] = "active"
            return True
        else:
            # Create new agent
            self.active_agents[agent_name] = {
                "status": "active",
                "current_task": None,
                "progress": 0,
                "last_update": datetime.now().isoformat(),
                "workload": 0,
                "expertise": ["general"],
                "authorities": [],
                "blockers": []
            }
            self.mock_messages[agent_name] = []
            return True
            
    def stop_agent(self, agent_name: str) -> bool:
        """Mock agent shutdown."""
        self._simulate_delay("agent_stop")
        
        if self._should_simulate_failure():
            return False
            
        if agent_name in self.active_agents:
            self.active_agents[agent_name]["status"] = "stopped"
            
            # Release all authorities
            for assignment in self.authority_state["assignments"]:
                if assignment["agent"] == agent_name and assignment["status"] == "active":
                    assignment["status"] = "released"
                    assignment["released_at"] = datetime.now().isoformat()
                    
            self.active_agents[agent_name]["authorities"] = []
            return True
            
        return False
        
    def is_system_healthy(self) -> bool:
        """Check mock system health."""
        # Simple health check for mock system
        return len(self.active_agents) > 0 and any(
            agent["status"] in ["active", "idle"] 
            for agent in self.active_agents.values()
        )
        
    def cleanup_test_environment(self):
        """Clean up mock environment."""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                
            # Clear mock state
            self.active_agents.clear()
            self.authority_state.clear()
            self.mock_messages.clear()
            
            self.logger.info("Mock system cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during mock cleanup: {e}")
            
    def add_mock_blocker(self, agent_name: str, blocker: str):
        """Add a blocker to mock agent (testing utility)."""
        if agent_name in self.active_agents:
            if "blockers" not in self.active_agents[agent_name]:
                self.active_agents[agent_name]["blockers"] = []
            self.active_agents[agent_name]["blockers"].append(blocker)
            self.active_agents[agent_name]["status"] = "blocked"
            
    def remove_mock_blocker(self, agent_name: str, blocker: str):
        """Remove a blocker from mock agent (testing utility)."""
        if agent_name in self.active_agents:
            blockers = self.active_agents[agent_name].get("blockers", [])
            if blocker in blockers:
                blockers.remove(blocker)
                if not blockers:
                    self.active_agents[agent_name]["status"] = "idle"
                    
    def simulate_authority_conflict(self, authority_type: str):
        """Simulate authority conflict for testing (testing utility)."""
        # Assign same authority to multiple agents
        agents = list(self.active_agents.keys())[:2]
        if len(agents) >= 2:
            for agent in agents:
                self.request_authority(agent, authority_type, "test", "conflict_test")
                
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Get mock-specific statistics for testing."""
        return {
            "total_operations": getattr(self, 'operation_count', 0),
            "simulated_failures": getattr(self, 'failure_count', 0),
            "temp_dir": str(self.temp_dir) if self.temp_dir else None,
            "mock_mode": True
        }