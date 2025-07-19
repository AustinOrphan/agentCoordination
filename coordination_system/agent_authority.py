#!/usr/bin/env python3
"""
Agent Authority Management System

Tracks and enforces authority levels, delegation chains, and emergency activations
for the multi-agent coordination system.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthorityLevel(Enum):
    """Authority levels for different decision types."""
    STRATEGIC = "strategic"      # > 7 days
    ROUTINE = "routine"          # 1-7 days
    EMERGENCY = "emergency"      # < 24 hours
    DOMAIN = "domain"           # Immediate domain-specific

class AuthoritySource(Enum):
    """Source of authority for a decision."""
    PRIMARY = "primary"
    BACKUP_1 = "backup-1"
    BACKUP_2 = "backup-2"
    EMERGENCY = "emergency"
    VOTE = "vote"

class AuthorityManager:
    """Manages agent authorities and delegation chains."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.authority_file = os.path.join(project_root, "authority_role_mappings.json")
        self.decision_log = os.path.join(project_root, "DECISION_LOG.json")
        self.agent_config_file = os.path.join(project_root, "agent_config.json")
        self.status_dir = os.path.join(project_root, "agent_status")
        
        # Load configurations
        self.authority_mappings = self._load_authority_mappings()
        self.agent_config = self._load_agent_config()
        self.decision_history = self._load_decision_log()
        
        # Timeout thresholds (in hours)
        self.timeouts = {
            AuthorityLevel.STRATEGIC: {"primary": 24, "backup": 48, "emergency": 72},
            AuthorityLevel.ROUTINE: {"primary": 8, "backup": 16, "emergency": 24},
            AuthorityLevel.EMERGENCY: {"primary": 2, "backup": 4, "emergency": 6},
            AuthorityLevel.DOMAIN: {"primary": 0.5, "backup": 1, "emergency": 2}
        }
    
    def _load_authority_mappings(self) -> Dict:
        """Load authority role mappings."""
        if os.path.exists(self.authority_file):
            with open(self.authority_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_agent_config(self) -> Dict:
        """Load agent configuration."""
        if os.path.exists(self.agent_config_file):
            with open(self.agent_config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_decision_log(self) -> List[Dict]:
        """Load decision history."""
        if os.path.exists(self.decision_log):
            with open(self.decision_log, 'r') as f:
                return json.load(f)
        return []
    
    def _save_decision_log(self):
        """Save decision history."""
        with open(self.decision_log, 'w') as f:
            json.dump(self.decision_history, f, indent=2)
    
    def get_agent_position(self, agent_name: str) -> int:
        """Get the position (1-6) of an agent based on their order."""
        current_theme = self.agent_config['current_theme']
        agent_count = self.agent_config['agent_count']
        theme_agents = self.agent_config['themes'][current_theme]['agents'][:agent_count]
        
        try:
            index = theme_agents.index(agent_name)
            return (index % 6) + 1  # Positions 1-6 cycle
        except ValueError:
            logger.error(f"Agent {agent_name} not found in current theme")
            return 0
    
    def get_agent_authority(self, agent_name: str) -> Dict:
        """Get the authority information for an agent."""
        position = self.get_agent_position(agent_name)
        if position == 0:
            return {}
        
        return self.authority_mappings.get('role_authorities', {}).get(str(position), {})
    
    def get_primary_authority_for_decision(self, decision_type: str) -> Optional[str]:
        """Get the primary authority holder for a decision type."""
        chains = self.authority_mappings.get('decision_chains', {})
        chain = chains.get(decision_type, [])
        
        if not chain:
            return None
        
        # Map position number to actual agent name
        if chain[0].isdigit():
            position = int(chain[0])
            return self.get_agent_by_position(position)
        
        return chain[0]
    
    def get_agent_by_position(self, position: int) -> Optional[str]:
        """Get agent name by their position number."""
        current_theme = self.agent_config['current_theme']
        agent_count = self.agent_config['agent_count']
        theme_agents = self.agent_config['themes'][current_theme]['agents'][:agent_count]
        
        if 1 <= position <= len(theme_agents):
            return theme_agents[position - 1]
        return None
    
    def get_backup_chain(self, decision_type: str) -> List[str]:
        """Get the backup authority chain for a decision type."""
        chains = self.authority_mappings.get('decision_chains', {})
        chain = chains.get(decision_type, [])
        
        # Convert position numbers to agent names
        backup_chain = []
        for authority in chain[1:]:  # Skip primary
            if authority.isdigit():
                agent = self.get_agent_by_position(int(authority))
                if agent:
                    backup_chain.append(agent)
            else:
                backup_chain.append(authority)
        
        return backup_chain
    
    def check_agent_availability(self, agent_name: str) -> bool:
        """Check if an agent is currently available."""
        status_file = os.path.join(self.status_dir, f"{agent_name}_status.json")
        
        if not os.path.exists(status_file):
            return False
        
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            # Check if agent is active and not blocked
            if status.get('status') != 'active':
                return False
            
            if status.get('blockers'):
                return False
            
            # Check last update time
            last_update = datetime.fromisoformat(status.get('last_updated', ''))
            if datetime.now() - last_update > timedelta(hours=1):
                return False  # Agent hasn't updated in over an hour
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking availability for {agent_name}: {e}")
            return False
    
    def find_available_authority(self, decision_type: str, authority_level: AuthorityLevel) -> Tuple[Optional[str], AuthoritySource]:
        """Find the first available authority for a decision."""
        # Get primary authority
        primary = self.get_primary_authority_for_decision(decision_type)
        if primary and self.check_agent_availability(primary):
            return primary, AuthoritySource.PRIMARY
        
        # Check backup chain
        backup_chain = self.get_backup_chain(decision_type)
        for i, backup in enumerate(backup_chain):
            if backup == "majority_vote":
                return self.conduct_vote(decision_type), AuthoritySource.VOTE
            elif backup == "any_available":
                # Find any available agent
                for agent in self.get_all_agents():
                    if self.check_agent_availability(agent):
                        return agent, AuthoritySource.EMERGENCY
            elif self.check_agent_availability(backup):
                return backup, AuthoritySource(f"backup-{i+1}")
        
        return None, AuthoritySource.EMERGENCY
    
    def get_all_agents(self) -> List[str]:
        """Get all agents in the current configuration."""
        current_theme = self.agent_config['current_theme']
        agent_count = self.agent_config['agent_count']
        return self.agent_config['themes'][current_theme]['agents'][:agent_count]
    
    def conduct_vote(self, decision_type: str) -> Optional[str]:
        """Conduct a majority vote among available agents."""
        # This would be implemented to actually conduct a vote
        # For now, return the first available agent with highest authority
        for agent in self.get_all_agents():
            if self.check_agent_availability(agent):
                return agent
        return None
    
    def record_decision(self, decision_id: str, decision_maker: str, 
                       authority_level: AuthorityLevel, authority_source: AuthoritySource,
                       title: str, decision: str, rationale: str):
        """Record a decision with authority tracking."""
        decision_record = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "decision_maker": decision_maker,
            "authority_level": authority_level.value,
            "authority_source": authority_source.value,
            "title": title,
            "decision": decision,
            "rationale": rationale,
            "position": self.get_agent_position(decision_maker),
            "role": self.get_agent_authority(decision_maker).get('role', 'Unknown')
        }
        
        self.decision_history.append(decision_record)
        self._save_decision_log()
        
        logger.info(f"Decision {decision_id} recorded by {decision_maker} using {authority_source.value} authority")
        return decision_record
    
    def check_timeout_activation(self, decision_id: str, authority_level: AuthorityLevel) -> Optional[str]:
        """Check if backup authority should be activated due to timeout."""
        # Find the decision request
        for decision in self.decision_history:
            if decision['decision_id'] == decision_id and decision.get('status') == 'pending':
                request_time = datetime.fromisoformat(decision['timestamp'])
                elapsed_hours = (datetime.now() - request_time).total_seconds() / 3600
                
                timeouts = self.timeouts[authority_level]
                
                if elapsed_hours > timeouts['emergency']:
                    return "emergency"
                elif elapsed_hours > timeouts['backup']:
                    return "backup"
                elif elapsed_hours > timeouts['primary']:
                    return "primary_timeout"
        
        return None
    
    def activate_backup_authority(self, decision_id: str, decision_type: str, 
                                 authority_level: AuthorityLevel) -> Tuple[Optional[str], AuthoritySource]:
        """Activate backup authority for a timed-out decision."""
        timeout_stage = self.check_timeout_activation(decision_id, authority_level)
        
        if not timeout_stage:
            return None, AuthoritySource.PRIMARY
        
        # Find next available authority
        agent, source = self.find_available_authority(decision_type, authority_level)
        
        if agent:
            # Record the activation
            activation_record = {
                "type": "authority_activation",
                "decision_id": decision_id,
                "timestamp": datetime.now().isoformat(),
                "activated_agent": agent,
                "authority_source": source.value,
                "timeout_stage": timeout_stage,
                "reason": f"Primary authority timeout after {timeout_stage}"
            }
            
            self.decision_history.append(activation_record)
            self._save_decision_log()
            
            logger.info(f"Backup authority activated: {agent} with {source.value} for decision {decision_id}")
        
        return agent, source
    
    def get_agent_decisions(self, agent_name: str) -> List[Dict]:
        """Get all decisions made by a specific agent."""
        return [d for d in self.decision_history 
                if d.get('decision_maker') == agent_name or d.get('activated_agent') == agent_name]
    
    def get_pending_decisions(self) -> List[Dict]:
        """Get all decisions awaiting authority."""
        return [d for d in self.decision_history if d.get('status') == 'pending']
    
    def update_agent_authority_status(self, agent_name: str):
        """Update an agent's status file with their authority information."""
        status_file = os.path.join(self.status_dir, f"{agent_name}_status.json")
        
        # Load existing status
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status = json.load(f)
        else:
            status = {}
        
        # Add authority information
        position = self.get_agent_position(agent_name)
        authority = self.get_agent_authority(agent_name)
        
        status['authority'] = {
            "position": position,
            "role": authority.get('role', 'Unknown'),
            "primary_authorities": authority.get('primary_authorities', []),
            "domain_authority": authority.get('domain_authority', ''),
            "emergency_authority": authority.get('emergency_authority', ''),
            "backup_responsibilities": authority.get('backup_responsibilities', []),
            "pending_decisions": [d['decision_id'] for d in self.get_pending_decisions() 
                                if self.is_agent_authority_for_decision(agent_name, d)],
            "decision_count": len(self.get_agent_decisions(agent_name))
        }
        
        # Save updated status
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def is_agent_authority_for_decision(self, agent_name: str, decision: Dict) -> bool:
        """Check if an agent has authority for a pending decision."""
        decision_type = decision.get('decision_type', 'technical')
        authority_level = AuthorityLevel(decision.get('authority_level', 'routine'))
        
        # Check if agent is in the authority chain
        primary = self.get_primary_authority_for_decision(decision_type)
        if primary == agent_name:
            return True
        
        backup_chain = self.get_backup_chain(decision_type)
        return agent_name in backup_chain


def main():
    """Example usage and testing."""
    manager = AuthorityManager()
    
    # Test getting agent authorities
    print("Testing Agent Authorities:")
    for agent in manager.get_all_agents():
        position = manager.get_agent_position(agent)
        authority = manager.get_agent_authority(agent)
        print(f"\n{agent} (Position {position}):")
        print(f"  Role: {authority.get('role', 'Unknown')}")
        print(f"  Primary: {authority.get('primary_authorities', [])[:1]}")
    
    # Test finding available authority
    print("\n\nTesting Authority Finding:")
    agent, source = manager.find_available_authority("strategic", AuthorityLevel.STRATEGIC)
    print(f"Available authority for strategic decision: {agent} ({source.value})")
    
    # Record a test decision
    print("\n\nRecording Test Decision:")
    decision = manager.record_decision(
        decision_id="DEC-2025-001",
        decision_maker="shark",
        authority_level=AuthorityLevel.ROUTINE,
        authority_source=AuthoritySource.PRIMARY,
        title="Test Architecture Decision",
        decision="Implement microservices pattern",
        rationale="Better scalability and maintainability"
    )
    print(f"Decision recorded: {decision['decision_id']}")

if __name__ == "__main__":
    main()