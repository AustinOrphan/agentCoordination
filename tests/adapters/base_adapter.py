"""
Base Adapter Interface

Defines the common interface for coordination system adapters, allowing
tests to run against both mock and real systems with the same API.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class AdapterMode(Enum):
    """Adapter operation modes."""
    MOCK = "mock"
    REAL = "real"
    HYBRID = "hybrid"  # Mix of mock and real components


@dataclass
class AdapterConfig:
    """Base configuration for adapters."""
    mode: AdapterMode
    test_isolation: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"


class BaseCoordinationAdapter(ABC):
    """Base class for coordination system adapters."""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.active_agents: Dict[str, Any] = {}
        self.authority_state: Dict[str, Any] = {}
        self.communication_state: Dict[str, Any] = {}
        
    @abstractmethod
    def setup_test_environment(self) -> bool:
        """Setup the test environment."""
        pass
        
    @abstractmethod
    def cleanup_test_environment(self):
        """Clean up the test environment."""
        pass
        
    @abstractmethod
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent."""
        pass
        
    @abstractmethod
    def update_agent_status(self, agent_name: str, status_data: Dict[str, Any]) -> bool:
        """Update agent status."""
        pass
        
    @abstractmethod
    def request_authority(self, agent_name: str, authority_type: str, domain: str, task: str) -> bool:
        """Request authority for an agent."""
        pass
        
    @abstractmethod
    def release_authority(self, agent_name: str, authority_id: str) -> bool:
        """Release authority for an agent."""
        pass
        
    @abstractmethod
    def send_message(self, sender: str, recipient: str, message_type: str, content: Dict[str, Any]) -> bool:
        """Send a message between agents."""
        pass
        
    @abstractmethod
    def get_messages(self, agent_name: str, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """Get messages for an agent."""
        pass
        
    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        pass
        
    @abstractmethod
    def start_agent(self, agent_name: str) -> bool:
        """Start an agent."""
        pass
        
    @abstractmethod
    def stop_agent(self, agent_name: str) -> bool:
        """Stop an agent."""
        pass
        
    @abstractmethod
    def is_system_healthy(self) -> bool:
        """Check if the system is healthy."""
        pass
        
    def get_active_agents(self) -> List[str]:
        """Get list of active agent names."""
        return list(self.active_agents.keys())
        
    def get_authority_assignments(self) -> List[Dict[str, Any]]:
        """Get current authority assignments."""
        return self.authority_state.get("assignments", [])
        
    def get_pending_authority_requests(self) -> List[Dict[str, Any]]:
        """Get pending authority requests."""
        return self.authority_state.get("requests", [])
        
    def validate_system_state(self) -> Dict[str, Any]:
        """Validate current system state and return issues."""
        issues = []
        warnings = []
        
        # Check if agents are responsive
        for agent_name in self.active_agents:
            status = self.get_agent_status(agent_name)
            if not status:
                issues.append(f"Agent {agent_name} is not responsive")
            elif status.get("status") == "error":
                issues.append(f"Agent {agent_name} is in error state")
                
        # Check for authority conflicts
        authority_holders = {}
        for assignment in self.get_authority_assignments():
            auth_key = f"{assignment.get('authority_type')}:{assignment.get('domain')}"
            if auth_key in authority_holders:
                issues.append(f"Authority conflict: {auth_key} held by multiple agents")
            else:
                authority_holders[auth_key] = assignment.get("agent")
                
        # Check for stale requests
        import time
        current_time = time.time()
        for request in self.get_pending_authority_requests():
            request_time = request.get("requested_at", "")
            # Simplified check - in real implementation, parse timestamp properly
            if "2025-07-19" in str(request_time):  # Example stale check
                warnings.append(f"Potentially stale authority request: {request.get('id')}")
                
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "agent_count": len(self.active_agents),
            "authority_count": len(self.get_authority_assignments())
        }