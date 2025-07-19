#!/usr/bin/env python3
"""
Authority Lifecycle Integration

Integrates authority management with the lifecycle daemon to enable automatic
backup authority activation and emergency decision handling.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Import from existing modules
from coordination_system.agent_authority import AuthorityManager, AuthorityLevel, AuthoritySource
from coordination_system.agent_communication import CommunicationChannel, Message, MessageType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthorityLifecycleManager:
    """Manages authority delegation and backup activation within the lifecycle system."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.authority_manager = AuthorityManager(project_root)
        self.pending_decisions_file = self.project_root / "PENDING_DECISIONS.json"
        self.emergency_log_file = self.project_root / "EMERGENCY_DECISIONS.md"
        
        # Track active authority delegations
        self.active_delegations = {}
        
        # Ensure files exist
        if not self.pending_decisions_file.exists():
            self._save_pending_decisions([])
        
        if not self.emergency_log_file.exists():
            self._init_emergency_log()
    
    def _save_pending_decisions(self, decisions: List[Dict]):
        """Save pending decisions to file."""
        with open(self.pending_decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)
    
    def _load_pending_decisions(self) -> List[Dict]:
        """Load pending decisions from file."""
        try:
            with open(self.pending_decisions_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _init_emergency_log(self):
        """Initialize emergency decisions log."""
        content = """# Emergency Decisions Log

This file tracks all decisions made under emergency or backup authority.

---

"""
        with open(self.emergency_log_file, 'w') as f:
            f.write(content)
    
    def request_decision(self, decision_type: str, title: str, description: str,
                        authority_level: AuthorityLevel, requester: str) -> str:
        """Request a decision that requires authority."""
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Find primary authority
        primary_authority = self.authority_manager.get_primary_authority_for_decision(decision_type)
        
        decision_request = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "title": title,
            "description": description,
            "authority_level": authority_level.value,
            "requester": requester,
            "primary_authority": primary_authority,
            "status": "pending",
            "assigned_to": primary_authority,
            "authority_source": "primary"
        }
        
        # Save to pending decisions
        pending = self._load_pending_decisions()
        pending.append(decision_request)
        self._save_pending_decisions(pending)
        
        # Send message to primary authority
        if primary_authority:
            self._notify_agent(primary_authority, decision_request, "primary")
        
        logger.info(f"Decision {decision_id} requested, assigned to {primary_authority}")
        return decision_id
    
    def _notify_agent(self, agent_name: str, decision: Dict, authority_type: str):
        """Notify an agent about a decision request."""
        try:
            channel = CommunicationChannel(agent_name)
            
            msg = Message(
                from_id="authority_manager",
                to_id=agent_name,
                msg_type=MessageType.TASK_ASSIGNMENT,
                payload={
                    "type": "decision_request",
                    "decision_id": decision["decision_id"],
                    "title": decision["title"],
                    "description": decision["description"],
                    "authority_type": authority_type,
                    "authority_level": decision["authority_level"],
                    "deadline": self._calculate_deadline(AuthorityLevel(decision["authority_level"]), authority_type)
                },
                requires_ack=True
            )
            
            channel.send_message(msg)
            logger.info(f"Notified {agent_name} about decision {decision['decision_id']} as {authority_type} authority")
            
        except Exception as e:
            logger.error(f"Failed to notify {agent_name}: {e}")
    
    def _calculate_deadline(self, authority_level: AuthorityLevel, authority_type: str) -> str:
        """Calculate deadline based on authority level and type."""
        timeouts = self.authority_manager.timeouts[authority_level]
        
        if authority_type == "primary":
            hours = timeouts["primary"]
        elif authority_type.startswith("backup"):
            hours = timeouts["backup"]
        else:
            hours = timeouts["emergency"]
        
        deadline = datetime.now() + timedelta(hours=hours)
        return deadline.isoformat()
    
    def check_timeouts(self):
        """Check for timed-out decisions and activate backup authority."""
        pending = self._load_pending_decisions()
        updated = False
        
        for decision in pending:
            if decision["status"] != "pending":
                continue
            
            # Check if current authority has timed out
            authority_level = AuthorityLevel(decision["authority_level"])
            timeout_stage = self.authority_manager.check_timeout_activation(
                decision["decision_id"], 
                authority_level
            )
            
            if timeout_stage and decision.get("assigned_to"):
                # Current authority has timed out, activate backup
                logger.warning(f"Authority timeout for decision {decision['decision_id']} - {timeout_stage}")
                
                # Find next authority in chain
                next_agent, next_source = self._find_next_authority(
                    decision["decision_type"],
                    decision.get("authority_source", "primary")
                )
                
                if next_agent and next_agent != decision.get("assigned_to"):
                    # Update decision assignment
                    decision["assigned_to"] = next_agent
                    decision["authority_source"] = next_source.value
                    decision["authority_activations"] = decision.get("authority_activations", [])
                    decision["authority_activations"].append({
                        "timestamp": datetime.now().isoformat(),
                        "from": decision.get("assigned_to"),
                        "to": next_agent,
                        "reason": f"Timeout - {timeout_stage}",
                        "source": next_source.value
                    })
                    
                    updated = True
                    
                    # Notify new authority
                    self._notify_agent(next_agent, decision, next_source.value)
                    
                    # Log emergency activation if needed
                    if next_source in [AuthoritySource.EMERGENCY, AuthoritySource.VOTE]:
                        self._log_emergency_activation(decision, next_agent, next_source)
        
        if updated:
            self._save_pending_decisions(pending)
    
    def _find_next_authority(self, decision_type: str, current_source: str) -> Tuple[Optional[str], AuthoritySource]:
        """Find the next authority in the chain."""
        # Map current source to next in chain
        if current_source == "primary":
            next_sources = [AuthoritySource.BACKUP_1, AuthoritySource.BACKUP_2, AuthoritySource.EMERGENCY]
        elif current_source == "backup-1":
            next_sources = [AuthoritySource.BACKUP_2, AuthoritySource.EMERGENCY, AuthoritySource.VOTE]
        elif current_source == "backup-2":
            next_sources = [AuthoritySource.EMERGENCY, AuthoritySource.VOTE]
        else:
            next_sources = [AuthoritySource.VOTE]
        
        # Try each source in order
        backup_chain = self.authority_manager.get_backup_chain(decision_type)
        
        for i, source in enumerate(next_sources):
            if source == AuthoritySource.VOTE:
                # Conduct vote
                agent = self.authority_manager.conduct_vote(decision_type)
                if agent:
                    return agent, source
            elif source == AuthoritySource.EMERGENCY:
                # Find any available agent
                for agent in self.authority_manager.get_all_agents():
                    if self.authority_manager.check_agent_availability(agent):
                        return agent, source
            else:
                # Check specific backup in chain
                backup_index = int(source.value.split('-')[1]) - 1
                if backup_index < len(backup_chain):
                    agent = backup_chain[backup_index]
                    if self.authority_manager.check_agent_availability(agent):
                        return agent, source
        
        return None, AuthoritySource.EMERGENCY
    
    def _log_emergency_activation(self, decision: Dict, agent: str, source: AuthoritySource):
        """Log emergency authority activation."""
        with open(self.emergency_log_file, 'a') as f:
            f.write(f"""
## Emergency Activation: {decision['decision_id']}

- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
- **Decision**: {decision['title']}
- **Activated Agent**: {agent}
- **Authority Source**: {source.value}
- **Reason**: Primary and backup authorities unavailable
- **Original Request**: {decision['timestamp']}
- **Requester**: {decision['requester']}

---

""")
    
    def record_decision_completion(self, decision_id: str, agent: str, 
                                  decision_text: str, rationale: str):
        """Record that a decision has been completed."""
        pending = self._load_pending_decisions()
        
        for decision in pending:
            if decision["decision_id"] == decision_id:
                # Update decision status
                decision["status"] = "completed"
                decision["completed_by"] = agent
                decision["completed_at"] = datetime.now().isoformat()
                decision["decision_text"] = decision_text
                decision["rationale"] = rationale
                
                # Record in authority manager
                self.authority_manager.record_decision(
                    decision_id=decision_id,
                    decision_maker=agent,
                    authority_level=AuthorityLevel(decision["authority_level"]),
                    authority_source=AuthoritySource(decision.get("authority_source", "primary")),
                    title=decision["title"],
                    decision=decision_text,
                    rationale=rationale
                )
                
                # Log if emergency/backup authority was used
                if decision.get("authority_source") not in ["primary", None]:
                    self._log_decision_completion(decision)
                
                break
        
        self._save_pending_decisions(pending)
        logger.info(f"Decision {decision_id} completed by {agent}")
    
    def _log_decision_completion(self, decision: Dict):
        """Log completion of decision made under backup authority."""
        with open(self.emergency_log_file, 'a') as f:
            f.write(f"""
### Decision Completed: {decision['decision_id']}

- **Completed By**: {decision['completed_by']}
- **Authority Used**: {decision.get('authority_source', 'unknown')}
- **Decision**: {decision.get('decision_text', 'Not recorded')}
- **Rationale**: {decision.get('rationale', 'Not recorded')}
- **Completed At**: {decision['completed_at']}

""")
    
    def get_agent_pending_decisions(self, agent_name: str) -> List[Dict]:
        """Get all pending decisions assigned to an agent."""
        pending = self._load_pending_decisions()
        return [d for d in pending 
                if d.get("assigned_to") == agent_name and d.get("status") == "pending"]
    
    def integrate_with_lifecycle(self):
        """Run as part of the lifecycle daemon loop."""
        while True:
            try:
                # Check for timeouts every minute
                self.check_timeouts()
                
                # Check for stuck decisions
                self._check_stuck_decisions()
                
                # Sleep before next check
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Authority lifecycle manager stopped")
                break
            except Exception as e:
                logger.error(f"Error in authority lifecycle loop: {e}")
                time.sleep(60)
    
    def _check_stuck_decisions(self):
        """Check for decisions that have been pending too long."""
        pending = self._load_pending_decisions()
        
        for decision in pending:
            if decision["status"] != "pending":
                continue
            
            # Check if decision has been pending for over 24 hours
            request_time = datetime.fromisoformat(decision["timestamp"])
            if datetime.now() - request_time > timedelta(hours=24):
                logger.error(f"Decision {decision['decision_id']} has been pending for over 24 hours!")
                
                # Send emergency notification
                self._send_emergency_notification(decision)
    
    def _send_emergency_notification(self, decision: Dict):
        """Send emergency notification about stuck decision."""
        # This would integrate with external notification systems
        logger.critical(f"EMERGENCY: Decision {decision['decision_id']} - {decision['title']} requires immediate attention!")


def main():
    """Run the authority lifecycle manager."""
    manager = AuthorityLifecycleManager()
    
    print("Authority Lifecycle Manager started...")
    print("Monitoring for authority timeouts and emergency activations")
    
    try:
        manager.integrate_with_lifecycle()
    except KeyboardInterrupt:
        print("\nAuthority Lifecycle Manager stopped")

if __name__ == "__main__":
    main()