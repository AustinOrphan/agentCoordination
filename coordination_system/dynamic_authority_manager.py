#!/usr/bin/env python3
"""
Dynamic Authority Manager

Implements flexible, task-based authority assignment that scales from 1 to 24+ agents
without relying on fixed positions or roles.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthorityType(Enum):
    """Types of authority that can be granted."""
    PROJECT = "project"          # Project-wide authority
    DOMAIN = "domain"           # Domain-specific (backend, frontend, etc.)
    EMERGENCY = "emergency"     # Emergency response authority
    COLLABORATIVE = "collaborative"  # Shared decision authority
    TASK = "task"              # Task-specific authority

class DomainType(Enum):
    """Domain specializations."""
    BACKEND = "backend"
    FRONTEND = "frontend"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    DATA = "data"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    ARCHITECTURE = "architecture"
    GENERAL = "general"

class DynamicAuthorityManager:
    """Manages dynamic authority assignment based on tasks and availability."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.authority_pool_file = self.project_root / "authority_pool.json"
        self.agent_workload_file = self.project_root / "agent_workloads.json"
        self.authority_history_file = self.project_root / "authority_history.json"
        
        # Initialize data structures
        self.authority_pool = self._load_authority_pool()
        self.agent_workloads = self._load_agent_workloads()
        self.authority_history = self._load_authority_history()
        
        # Configuration
        self.config = {
            "max_workload": 90,          # Max workload before declining new authority
            "optimal_workload": 70,      # Target workload for load balancing
            "min_backup_agents": 2,      # Minimum backup agents to maintain
            "authority_timeout_hours": {
                "project": 168,          # 1 week
                "domain": 24,           # 1 day  
                "task": 8,              # 8 hours
                "emergency": 2,         # 2 hours
                "collaborative": 4      # 4 hours
            }
        }
    
    def _load_authority_pool(self) -> Dict:
        """Load current authority assignments."""
        if self.authority_pool_file.exists():
            with open(self.authority_pool_file, 'r') as f:
                return json.load(f)
        return {"assignments": [], "available": [], "requests": []}
    
    def _save_authority_pool(self):
        """Save authority pool to file."""
        with open(self.authority_pool_file, 'w') as f:
            json.dump(self.authority_pool, f, indent=2)
    
    def _load_agent_workloads(self) -> Dict:
        """Load agent workload information."""
        if self.agent_workload_file.exists():
            with open(self.agent_workload_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_agent_workloads(self):
        """Save agent workloads."""
        with open(self.agent_workload_file, 'w') as f:
            json.dump(self.agent_workloads, f, indent=2)
    
    def _load_authority_history(self) -> List:
        """Load authority assignment history."""
        if self.authority_history_file.exists():
            with open(self.authority_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_authority_history(self):
        """Save authority history."""
        with open(self.authority_history_file, 'w') as f:
            json.dump(self.authority_history, f, indent=2)
    
    def get_active_agents(self) -> List[str]:
        """Get list of currently active agents."""
        # Check agent status files
        status_dir = self.project_root / "agent_status"
        active_agents = []
        
        if status_dir.exists():
            for status_file in status_dir.glob("*_status.json"):
                try:
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                    
                    # Check if agent is active (updated within last hour)
                    last_update = status.get('last_update', '')
                    if last_update:
                        update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        if datetime.now(update_time.tzinfo) - update_time < timedelta(hours=1):
                            agent_name = status_file.stem.replace('_status', '')
                            active_agents.append(agent_name)
                except Exception as e:
                    logger.error(f"Error reading status file {status_file}: {e}")
        
        return active_agents
    
    def assign_authority(self, task_description: str, task_type: str = None, 
                        preferred_agent: str = None) -> Dict:
        """Assign authority for a task to the best available agent."""
        # Determine authority type and domain
        authority_type, domain = self._analyze_task(task_description, task_type)
        
        # Find best agent
        if preferred_agent and self._can_accept_authority(preferred_agent, authority_type):
            selected_agent = preferred_agent
        else:
            selected_agent = self._find_best_agent(domain, authority_type)
        
        if not selected_agent:
            # No agent available - queue the request
            request = {
                "id": f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "task": task_description,
                "authority_type": authority_type.value,
                "domain": domain.value,
                "requested_at": datetime.now().isoformat(),
                "status": "queued"
            }
            self.authority_pool["requests"].append(request)
            self._save_authority_pool()
            logger.warning(f"No agent available for task, queued request {request['id']}")
            return request
        
        # Create authority assignment
        assignment = {
            "id": f"AUTH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "agent": selected_agent,
            "authority_type": authority_type.value,
            "domain": domain.value,
            "task": task_description,
            "granted_at": datetime.now().isoformat(),
            "expires_at": self._calculate_expiry(authority_type),
            "status": "active"
        }
        
        # Update records
        self.authority_pool["assignments"].append(assignment)
        self._update_agent_workload(selected_agent, 20)  # Add 20% workload
        self._record_history(assignment)
        
        # Save changes
        self._save_authority_pool()
        self._save_agent_workloads()
        
        logger.info(f"Assigned {authority_type.value} authority to {selected_agent} for: {task_description}")
        return assignment
    
    def _analyze_task(self, task_description: str, task_type: str = None) -> Tuple[AuthorityType, DomainType]:
        """Analyze task to determine authority type and domain."""
        task_lower = task_description.lower()
        
        # Determine authority type
        if any(word in task_lower for word in ['project', 'initiative', 'epic', 'milestone']):
            authority_type = AuthorityType.PROJECT
        elif any(word in task_lower for word in ['emergency', 'critical', 'urgent', 'outage']):
            authority_type = AuthorityType.EMERGENCY
        elif any(word in task_lower for word in ['review', 'decision', 'approve']):
            authority_type = AuthorityType.COLLABORATIVE
        else:
            authority_type = AuthorityType.TASK
        
        # Determine domain
        if any(word in task_lower for word in ['api', 'backend', 'database', 'server']):
            domain = DomainType.BACKEND
        elif any(word in task_lower for word in ['ui', 'frontend', 'react', 'interface']):
            domain = DomainType.FRONTEND
        elif any(word in task_lower for word in ['deploy', 'infrastructure', 'ci/cd', 'docker']):
            domain = DomainType.INFRASTRUCTURE
        elif any(word in task_lower for word in ['security', 'vulnerability', 'auth']):
            domain = DomainType.SECURITY
        elif any(word in task_lower for word in ['data', 'migration', 'etl', 'analytics']):
            domain = DomainType.DATA
        elif any(word in task_lower for word in ['performance', 'optimization', 'speed']):
            domain = DomainType.PERFORMANCE
        elif any(word in task_lower for word in ['test', 'quality', 'qa', 'bug']):
            domain = DomainType.QUALITY
        elif any(word in task_lower for word in ['architecture', 'design', 'pattern']):
            domain = DomainType.ARCHITECTURE
        else:
            domain = DomainType.GENERAL
        
        return authority_type, domain
    
    def _find_best_agent(self, domain: DomainType, authority_type: AuthorityType) -> Optional[str]:
        """Find the best available agent for the given domain and authority type."""
        active_agents = self.get_active_agents()
        
        if not active_agents:
            return None
        
        # If only one agent, they get everything
        if len(active_agents) == 1:
            return active_agents[0]
        
        # Score agents based on multiple factors
        agent_scores = {}
        
        for agent in active_agents:
            score = 0
            workload = self.agent_workloads.get(agent, {}).get('current', 0)
            
            # Factor 1: Workload (lower is better)
            if workload < self.config['optimal_workload']:
                score += (100 - workload)
            else:
                score += max(0, 100 - workload) / 2
            
            # Factor 2: Domain experience
            history_score = self._get_domain_experience_score(agent, domain)
            score += history_score * 2
            
            # Factor 3: Current domain match
            current_domains = self._get_agent_current_domains(agent)
            if domain in current_domains:
                score += 50  # Prefer agents already working in domain
            
            # Factor 4: Authority type experience
            auth_history_score = self._get_authority_experience_score(agent, authority_type)
            score += auth_history_score
            
            # Factor 5: Not overloaded
            if workload >= self.config['max_workload']:
                score = 0  # Cannot accept new authority
            
            agent_scores[agent] = score
        
        # Find best scoring agent
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1])
            if best_agent[1] > 0:
                return best_agent[0]
        
        return None
    
    def _get_domain_experience_score(self, agent: str, domain: DomainType) -> int:
        """Calculate agent's experience score in a domain."""
        score = 0
        for record in self.authority_history:
            if record.get('agent') == agent and record.get('domain') == domain.value:
                # More recent experience counts more
                days_ago = (datetime.now() - datetime.fromisoformat(record['granted_at'])).days
                if days_ago < 7:
                    score += 10
                elif days_ago < 30:
                    score += 5
                else:
                    score += 1
        return min(score, 50)  # Cap at 50
    
    def _get_authority_experience_score(self, agent: str, authority_type: AuthorityType) -> int:
        """Calculate agent's experience score with authority type."""
        score = 0
        for record in self.authority_history:
            if record.get('agent') == agent and record.get('authority_type') == authority_type.value:
                score += 5
        return min(score, 25)  # Cap at 25
    
    def _get_agent_current_domains(self, agent: str) -> Set[DomainType]:
        """Get domains agent is currently working in."""
        domains = set()
        for assignment in self.authority_pool.get('assignments', []):
            if assignment.get('agent') == agent and assignment.get('status') == 'active':
                try:
                    domains.add(DomainType(assignment.get('domain')))
                except ValueError:
                    pass
        return domains
    
    def _can_accept_authority(self, agent: str, authority_type: AuthorityType) -> bool:
        """Check if agent can accept new authority."""
        workload = self.agent_workloads.get(agent, {}).get('current', 0)
        
        # Check workload limits
        if workload >= self.config['max_workload']:
            return False
        
        # Emergency authority can always be accepted if under max
        if authority_type == AuthorityType.EMERGENCY:
            return True
        
        # Check if accepting would exceed optimal workload significantly
        projected_workload = workload + 20
        if projected_workload > self.config['optimal_workload'] + 20:
            # Only accept if no better alternative
            return len([a for a in self.get_active_agents() 
                       if self.agent_workloads.get(a, {}).get('current', 0) < workload]) == 0
        
        return True
    
    def _calculate_expiry(self, authority_type: AuthorityType) -> str:
        """Calculate when authority expires."""
        hours = self.config['authority_timeout_hours'].get(authority_type.value, 24)
        expiry = datetime.now() + timedelta(hours=hours)
        return expiry.isoformat()
    
    def _update_agent_workload(self, agent: str, change: int):
        """Update agent's workload."""
        if agent not in self.agent_workloads:
            self.agent_workloads[agent] = {
                'current': 0,
                'history': [],
                'last_updated': datetime.now().isoformat()
            }
        
        old_workload = self.agent_workloads[agent]['current']
        new_workload = max(0, min(100, old_workload + change))
        
        self.agent_workloads[agent]['current'] = new_workload
        self.agent_workloads[agent]['last_updated'] = datetime.now().isoformat()
        self.agent_workloads[agent]['history'].append({
            'timestamp': datetime.now().isoformat(),
            'from': old_workload,
            'to': new_workload,
            'change': change
        })
        
        # Keep only last 100 history entries
        if len(self.agent_workloads[agent]['history']) > 100:
            self.agent_workloads[agent]['history'] = self.agent_workloads[agent]['history'][-100:]
        
        self._save_agent_workloads()
    
    def _record_history(self, assignment: Dict):
        """Record authority assignment in history."""
        self.authority_history.append(assignment.copy())
        
        # Keep only last 1000 records
        if len(self.authority_history) > 1000:
            self.authority_history = self.authority_history[-1000:]
        
        self._save_authority_history()
    
    def release_authority(self, authority_id: str, agent: str):
        """Release authority when task is complete."""
        for i, assignment in enumerate(self.authority_pool.get('assignments', [])):
            if assignment.get('id') == authority_id and assignment.get('agent') == agent:
                # Mark as released
                assignment['status'] = 'released'
                assignment['released_at'] = datetime.now().isoformat()
                
                # Update workload
                self._update_agent_workload(agent, -20)
                
                # Check for queued requests that can now be fulfilled
                self._process_queued_requests()
                
                self._save_authority_pool()
                logger.info(f"Released authority {authority_id} from {agent}")
                return True
        
        return False
    
    def _process_queued_requests(self):
        """Process any queued authority requests."""
        if not self.authority_pool.get('requests'):
            return
        
        processed = []
        for request in self.authority_pool['requests']:
            if request.get('status') == 'queued':
                # Try to assign
                result = self.assign_authority(
                    request['task'],
                    request.get('authority_type')
                )
                
                if 'agent' in result:
                    request['status'] = 'fulfilled'
                    request['fulfilled_at'] = datetime.now().isoformat()
                    request['assigned_to'] = result['agent']
                    processed.append(request['id'])
        
        if processed:
            logger.info(f"Processed {len(processed)} queued requests")
    
    def get_agent_authorities(self, agent: str) -> List[Dict]:
        """Get all active authorities for an agent."""
        authorities = []
        for assignment in self.authority_pool.get('assignments', []):
            if assignment.get('agent') == agent and assignment.get('status') == 'active':
                # Check if expired
                if datetime.fromisoformat(assignment['expires_at']) < datetime.now():
                    assignment['status'] = 'expired'
                else:
                    authorities.append(assignment)
        
        return authorities
    
    def get_authority_holders(self, domain: DomainType = None, 
                            authority_type: AuthorityType = None) -> List[Dict]:
        """Find who currently holds specific authorities."""
        holders = []
        
        for assignment in self.authority_pool.get('assignments', []):
            if assignment.get('status') != 'active':
                continue
            
            # Check if expired
            if datetime.fromisoformat(assignment['expires_at']) < datetime.now():
                continue
            
            # Filter by criteria
            if domain and assignment.get('domain') != domain.value:
                continue
            
            if authority_type and assignment.get('authority_type') != authority_type.value:
                continue
            
            holders.append({
                'agent': assignment['agent'],
                'authority_id': assignment['id'],
                'domain': assignment['domain'],
                'authority_type': assignment['authority_type'],
                'task': assignment['task']
            })
        
        return holders
    
    def rebalance_authorities(self):
        """Rebalance authorities across active agents for optimal load distribution."""
        active_agents = self.get_active_agents()
        
        if len(active_agents) <= 1:
            return  # Nothing to balance
        
        # Calculate target workload
        total_authorities = len([a for a in self.authority_pool.get('assignments', []) 
                               if a.get('status') == 'active'])
        target_per_agent = total_authorities / len(active_agents)
        
        logger.info(f"Rebalancing {total_authorities} authorities across {len(active_agents)} agents")
        
        # Identify overloaded and underloaded agents
        overloaded = []
        underloaded = []
        
        for agent in active_agents:
            current_authorities = len(self.get_agent_authorities(agent))
            if current_authorities > target_per_agent + 1:
                overloaded.append((agent, current_authorities))
            elif current_authorities < target_per_agent - 1:
                underloaded.append((agent, current_authorities))
        
        # Transfer authorities from overloaded to underloaded
        transfers = 0
        for over_agent, over_count in overloaded:
            for under_agent, under_count in underloaded:
                if over_count <= target_per_agent:
                    break
                
                # Find transferable authorities (not PROJECT type)
                authorities = self.get_agent_authorities(over_agent)
                for auth in authorities:
                    if auth['authority_type'] != AuthorityType.PROJECT.value:
                        # Transfer
                        auth['agent'] = under_agent
                        auth['transferred_at'] = datetime.now().isoformat()
                        auth['transferred_from'] = over_agent
                        
                        self._update_agent_workload(over_agent, -20)
                        self._update_agent_workload(under_agent, 20)
                        
                        transfers += 1
                        over_count -= 1
                        under_count += 1
                        
                        if over_count <= target_per_agent:
                            break
        
        if transfers > 0:
            self._save_authority_pool()
            logger.info(f"Rebalanced {transfers} authorities")
    
    def generate_agent_prompt_data(self, agent: str) -> Dict:
        """Generate data for agent prompt template."""
        active_agents = self.get_active_agents()
        authorities = self.get_agent_authorities(agent)
        workload = self.agent_workloads.get(agent, {}).get('current', 0)
        
        # Format current authorities
        auth_text = ""
        if not authorities:
            auth_text = "- No specific authorities currently assigned\n"
            if len(active_agents) == 1:
                auth_text += "- As the only active agent, you have implicit authority for all decisions\n"
        else:
            for auth in authorities:
                auth_text += f"- {auth['authority_type'].upper()}: {auth['task']} (expires {auth['expires_at']})\n"
        
        # Determine current primary domain
        domains = self._get_agent_current_domains(agent)
        primary_domain = list(domains)[0].value if domains else "general"
        
        return {
            "AGENT_NAME": agent.title(),
            "AGENT_ID": agent,
            "ACTIVE_AGENT_COUNT": len(active_agents),
            "CURRENT_TASK": authorities[0]['task'] if authorities else "Awaiting assignment",
            "CURRENT_AUTHORITIES": auth_text,
            "ACTIVE_AGENT_LIST": ", ".join(active_agents),
            "WORKLOAD_PERCENTAGE": workload,
            "BACKUP_AVAILABILITY": "Yes" if workload < 80 else "No",
            "CURRENT_DOMAIN": primary_domain,
            "TIMESTAMP": datetime.now().strftime("%Y%m%d"),
            "COUNTER": len(self.authority_history) + 1
        }


def main():
    """Example usage and testing."""
    manager = DynamicAuthorityManager()
    
    # Test with different scenarios
    print("=== Dynamic Authority Manager Test ===\n")
    
    # Scenario 1: Single agent
    print("Scenario 1: Single agent system")
    manager.agent_workloads = {"alpha": {"current": 40}}
    assignment1 = manager.assign_authority("Implement new API endpoints for user management")
    print(f"Assigned to: {assignment1.get('agent', 'None')}")
    print(f"Authority type: {assignment1.get('authority_type')}")
    print(f"Domain: {assignment1.get('domain')}\n")
    
    # Scenario 2: Multiple agents with different workloads
    print("Scenario 2: Multiple agents")
    manager.agent_workloads = {
        "alpha": {"current": 70},
        "beta": {"current": 30},
        "gamma": {"current": 85}
    }
    assignment2 = manager.assign_authority("Fix critical security vulnerability in auth system")
    print(f"Assigned to: {assignment2.get('agent', 'None')}")
    print(f"Authority type: {assignment2.get('authority_type')}")
    
    # Show workload after assignment
    print("\nWorkloads after assignment:")
    for agent, data in manager.agent_workloads.items():
        print(f"  {agent}: {data['current']}%")

if __name__ == "__main__":
    main()