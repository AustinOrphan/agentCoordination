#!/usr/bin/env python3
"""
Conflict Resolution System
Handles disputes and deadlocks in multi-agent coordination
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Types of conflicts that can occur."""
    RESOURCE_CONTENTION = "resource_contention"      # Multiple agents want same resource
    AUTHORITY_DISPUTE = "authority_dispute"          # Disagreement over who has authority
    TASK_OVERLAP = "task_overlap"                    # Agents working on overlapping tasks
    PRIORITY_CONFLICT = "priority_conflict"          # Disagreement over task priorities
    DEADLINE_CONFLICT = "deadline_conflict"          # Conflicting timeline requirements
    EXPERTISE_DISPUTE = "expertise_dispute"          # Disagreement over technical decisions
    PROCESS_VIOLATION = "process_violation"          # Agent violating established processes
    VOTING_DEADLOCK = "voting_deadlock"             # Voting system unable to reach decision

class ConflictSeverity(Enum):
    """Severity levels for conflicts."""
    LOW = "low"                    # Minor disagreement, can wait
    MEDIUM = "medium"              # Moderate impact, needs attention
    HIGH = "high"                  # Significant impact, urgent resolution
    CRITICAL = "critical"          # System blocking, immediate resolution

class ResolutionStrategy(Enum):
    """Available resolution strategies."""
    AUTOMATED = "automated"        # System resolves automatically
    MEDIATION = "mediation"        # Neutral agent mediates
    ESCALATION = "escalation"      # Escalate to higher authority
    VOTING = "voting"              # Democratic resolution
    EXPERT_DECISION = "expert"     # Domain expert decides
    ROUND_ROBIN = "round_robin"    # Fair rotation of resources
    PRIORITY_BASED = "priority"    # Highest priority agent wins

@dataclass
class ConflictParty:
    """Party involved in a conflict."""
    agent_id: str
    position: str
    justification: str
    priority_level: int
    authority_level: str
    expertise_domains: List[str]

@dataclass
class Conflict:
    """Conflict record."""
    conflict_id: str
    type: str
    severity: str
    title: str
    description: str
    parties: List[Dict]  # ConflictParty objects as dicts
    reported_by: str
    reported_at: str
    resolution_deadline: Optional[str]
    status: str  # "open", "in_progress", "resolved", "escalated"
    assigned_mediator: Optional[str]
    resolution_strategy: Optional[str]
    resolution_details: Optional[Dict]
    resolution_timestamp: Optional[str]
    escalation_history: List[Dict]
    metadata: Dict

class ConflictResolutionSystem:
    """Manages conflict detection, mediation, and resolution."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.conflicts_db_file = self.project_root / "conflict_database.json"
        self.resolution_history_file = self.project_root / "conflict_resolutions.json"
        self.mediation_rules_file = self.project_root / "mediation_rules.json"
        
        # Load databases
        self.conflicts_db = self._load_conflicts_db()
        self.resolution_history = self._load_resolution_history()
        self.mediation_rules = self._load_mediation_rules()
        
        # Import related systems
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError:
            self.authority_manager = None
            logger.warning("Authority manager not available")
        
        try:
            from domain_specific_agent_roles import DomainSpecificRoleManager
            self.role_manager = DomainSpecificRoleManager(project_root)
        except ImportError:
            self.role_manager = None
            logger.warning("Role manager not available")
        
        try:
            from coordination_sync_protocol import CoordinationSyncProtocol
            self.voting_system = CoordinationSyncProtocol(project_root)
        except (ImportError, SyntaxError):
            self.voting_system = None
            logger.warning("Voting system not available due to import/syntax issues")
        
        self._initialize_mediation_rules()
        
        logger.info("⚖️ Conflict resolution system initialized")
    
    def _load_conflicts_db(self) -> Dict:
        """Load conflicts database."""
        if self.conflicts_db_file.exists():
            with open(self.conflicts_db_file, 'r') as f:
                return json.load(f)
        return {"conflicts": {}, "version": "1.0"}
    
    def _save_conflicts_db(self):
        """Save conflicts database."""
        with open(self.conflicts_db_file, 'w') as f:
            json.dump(self.conflicts_db, f, indent=2)
    
    def _load_resolution_history(self) -> List:
        """Load resolution history."""
        if self.resolution_history_file.exists():
            with open(self.resolution_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_resolution_history(self):
        """Save resolution history."""
        with open(self.resolution_history_file, 'w') as f:
            json.dump(self.resolution_history, f, indent=2)
    
    def _load_mediation_rules(self) -> Dict:
        """Load mediation rules."""
        if self.mediation_rules_file.exists():
            with open(self.mediation_rules_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_mediation_rules(self):
        """Save mediation rules."""
        with open(self.mediation_rules_file, 'w') as f:
            json.dump(self.mediation_rules, f, indent=2)
    
    def _initialize_mediation_rules(self):
        """Initialize default mediation rules."""
        
        if not self.mediation_rules:
            self.mediation_rules = {
                "conflict_type_strategies": {
                    ConflictType.RESOURCE_CONTENTION.value: [
                        ResolutionStrategy.ROUND_ROBIN.value,
                        ResolutionStrategy.PRIORITY_BASED.value,
                        ResolutionStrategy.MEDIATION.value
                    ],
                    ConflictType.AUTHORITY_DISPUTE.value: [
                        ResolutionStrategy.ESCALATION.value,
                        ResolutionStrategy.EXPERT_DECISION.value
                    ],
                    ConflictType.TASK_OVERLAP.value: [
                        ResolutionStrategy.AUTOMATED.value,
                        ResolutionStrategy.MEDIATION.value
                    ],
                    ConflictType.PRIORITY_CONFLICT.value: [
                        ResolutionStrategy.PRIORITY_BASED.value,
                        ResolutionStrategy.VOTING.value
                    ],
                    ConflictType.EXPERTISE_DISPUTE.value: [
                        ResolutionStrategy.EXPERT_DECISION.value,
                        ResolutionStrategy.VOTING.value
                    ],
                    ConflictType.VOTING_DEADLOCK.value: [
                        ResolutionStrategy.ESCALATION.value,
                        ResolutionStrategy.EXPERT_DECISION.value
                    ]
                },
                "severity_timeouts": {
                    ConflictSeverity.LOW.value: 24,      # 24 hours
                    ConflictSeverity.MEDIUM.value: 8,    # 8 hours
                    ConflictSeverity.HIGH.value: 2,      # 2 hours
                    ConflictSeverity.CRITICAL.value: 0.5 # 30 minutes
                },
                "escalation_thresholds": {
                    "failed_resolutions": 2,
                    "time_exceeded_hours": 48,
                    "party_count_threshold": 4
                }
            }
            self._save_mediation_rules()
            logger.info("Initialized default mediation rules")
    
    def report_conflict(self, 
                       conflict_type: ConflictType,
                       severity: ConflictSeverity,
                       title: str,
                       description: str,
                       parties: List[ConflictParty],
                       reporter_id: str,
                       metadata: Optional[Dict] = None) -> str:
        """Report a new conflict."""
        
        conflict_id = f"CONF-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{reporter_id}"
        
        # Calculate resolution deadline
        timeout_hours = self.mediation_rules["severity_timeouts"][severity.value]
        deadline = (datetime.now() + timedelta(hours=timeout_hours)).isoformat()
        
        conflict = Conflict(
            conflict_id=conflict_id,
            type=conflict_type.value,
            severity=severity.value,
            title=title,
            description=description,
            parties=[asdict(party) for party in parties],
            reported_by=reporter_id,
            reported_at=datetime.now().isoformat(),
            resolution_deadline=deadline,
            status="open",
            assigned_mediator=None,
            resolution_strategy=None,
            resolution_details=None,
            resolution_timestamp=None,
            escalation_history=[],
            metadata=metadata or {}
        )
        
        self.conflicts_db["conflicts"][conflict_id] = asdict(conflict)
        self._save_conflicts_db()
        
        logger.warning(f"⚖️ Conflict reported: {conflict_id} - {title}")
        logger.warning(f"   Type: {conflict_type.value}, Severity: {severity.value}")
        logger.warning(f"   Parties: {[p.agent_id for p in parties]}")
        logger.warning(f"   Resolution deadline: {deadline}")
        
        # Automatically attempt resolution
        self._attempt_automatic_resolution(conflict_id)
        
        return conflict_id
    
    def _attempt_automatic_resolution(self, conflict_id: str):
        """Attempt to resolve conflict automatically."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        conflict_type = conflict["type"]
        
        # Get resolution strategies for this conflict type
        strategies = self.mediation_rules["conflict_type_strategies"].get(
            conflict_type, [ResolutionStrategy.MEDIATION.value]
        )
        
        for strategy in strategies:
            if strategy == ResolutionStrategy.AUTOMATED.value:
                if self._try_automated_resolution(conflict_id):
                    return True
            elif strategy == ResolutionStrategy.ROUND_ROBIN.value:
                if self._try_round_robin_resolution(conflict_id):
                    return True
            elif strategy == ResolutionStrategy.PRIORITY_BASED.value:
                if self._try_priority_based_resolution(conflict_id):
                    return True
        
        # If automatic resolution fails, assign mediator
        self._assign_mediator(conflict_id)
        return False
    
    def _try_automated_resolution(self, conflict_id: str) -> bool:
        """Try automated resolution for simple conflicts."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        
        if conflict["type"] == ConflictType.TASK_OVERLAP.value:
            # For task overlap, assign tasks based on expertise
            parties = conflict["parties"]
            
            if len(parties) == 2:
                # Simple case: assign to agent with better expertise
                best_agent = self._select_agent_by_expertise(parties, conflict.get("metadata", {}).get("domain"))
                
                if best_agent:
                    resolution = {
                        "strategy": ResolutionStrategy.AUTOMATED.value,
                        "outcome": f"Task assigned to {best_agent} based on expertise",
                        "winner": best_agent,
                        "reasoning": "Automated assignment based on domain expertise"
                    }
                    
                    self._resolve_conflict(conflict_id, resolution)
                    return True
        
        return False
    
    def _try_round_robin_resolution(self, conflict_id: str) -> bool:
        """Try round-robin resolution for resource conflicts."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        
        if conflict["type"] == ConflictType.RESOURCE_CONTENTION.value:
            parties = conflict["parties"]
            
            # Check recent resource assignments to determine fairness
            recent_assignments = self._get_recent_resource_assignments()
            
            # Find agent who has had resource least recently
            least_recent_agent = None
            oldest_time = datetime.now()
            
            for party_dict in parties:
                agent_id = party_dict["agent_id"]
                last_assignment = recent_assignments.get(agent_id)
                
                if not last_assignment:
                    least_recent_agent = agent_id
                    break
                
                assignment_time = datetime.fromisoformat(last_assignment)
                if assignment_time < oldest_time:
                    oldest_time = assignment_time
                    least_recent_agent = agent_id
            
            if least_recent_agent:
                resolution = {
                    "strategy": ResolutionStrategy.ROUND_ROBIN.value,
                    "outcome": f"Resource assigned to {least_recent_agent} based on fair rotation",
                    "winner": least_recent_agent,
                    "reasoning": "Round-robin assignment for fair resource distribution"
                }
                
                self._resolve_conflict(conflict_id, resolution)
                return True
        
        return False
    
    def _try_priority_based_resolution(self, conflict_id: str) -> bool:
        """Try priority-based resolution."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        parties = conflict["parties"]
        
        # Find highest priority agent
        highest_priority = -1
        priority_agent = None
        
        for party_dict in parties:
            priority = party_dict.get("priority_level", 0)
            if priority > highest_priority:
                highest_priority = priority
                priority_agent = party_dict["agent_id"]
        
        if priority_agent and highest_priority > 0:
            resolution = {
                "strategy": ResolutionStrategy.PRIORITY_BASED.value,
                "outcome": f"Decision awarded to {priority_agent} based on priority",
                "winner": priority_agent,
                "reasoning": f"Highest priority level: {highest_priority}"
            }
            
            self._resolve_conflict(conflict_id, resolution)
            return True
        
        return False
    
    def _assign_mediator(self, conflict_id: str):
        """Assign a mediator for the conflict."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        parties = [party["agent_id"] for party in conflict["parties"]]
        
        # Find available agents who aren't involved in the conflict
        available_agents = ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]
        potential_mediators = [agent for agent in available_agents if agent not in parties]
        
        if not potential_mediators:
            # Escalate if no mediators available
            self._escalate_conflict(conflict_id, "No available mediators")
            return
        
        # Select mediator based on expertise in conflict domain
        conflict_domain = conflict.get("metadata", {}).get("domain")
        best_mediator = self._select_agent_by_expertise(
            [{"agent_id": agent} for agent in potential_mediators], 
            conflict_domain
        )
        
        if not best_mediator:
            best_mediator = potential_mediators[0]  # Fallback to first available
        
        # Update conflict with mediator
        conflict["assigned_mediator"] = best_mediator
        conflict["status"] = "in_progress"
        conflict["resolution_strategy"] = ResolutionStrategy.MEDIATION.value
        
        self.conflicts_db["conflicts"][conflict_id] = conflict
        self._save_conflicts_db()
        
        logger.info(f"⚖️ Assigned mediator {best_mediator} to conflict {conflict_id}")
    
    def _escalate_conflict(self, conflict_id: str, reason: str):
        """Escalate conflict to higher authority."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        
        escalation_record = {
            "escalated_at": datetime.now().isoformat(),
            "reason": reason,
            "escalated_by": "system",
            "previous_strategy": conflict.get("resolution_strategy")
        }
        
        conflict["escalation_history"].append(escalation_record)
        conflict["status"] = "escalated"
        conflict["resolution_strategy"] = ResolutionStrategy.ESCALATION.value
        
        self.conflicts_db["conflicts"][conflict_id] = conflict
        self._save_conflicts_db()
        
        logger.warning(f"⚖️ Escalated conflict {conflict_id}: {reason}")
    
    def _resolve_conflict(self, conflict_id: str, resolution: Dict):
        """Mark conflict as resolved."""
        
        conflict = self.conflicts_db["conflicts"][conflict_id]
        
        conflict["status"] = "resolved"
        conflict["resolution_details"] = resolution
        conflict["resolution_timestamp"] = datetime.now().isoformat()
        
        self.conflicts_db["conflicts"][conflict_id] = conflict
        self._save_conflicts_db()
        
        # Add to resolution history
        history_record = {
            "conflict_id": conflict_id,
            "conflict_type": conflict["type"],
            "resolution_strategy": resolution["strategy"],
            "outcome": resolution["outcome"],
            "resolved_at": conflict["resolution_timestamp"],
            "resolution_time_hours": self._calculate_resolution_time(conflict)
        }
        
        self.resolution_history.append(history_record)
        self._save_resolution_history()
        
        logger.info(f"✅ Resolved conflict {conflict_id}: {resolution['outcome']}")
    
    def _select_agent_by_expertise(self, parties: List[Dict], domain: Optional[str]) -> Optional[str]:
        """Select agent based on expertise in relevant domain."""
        
        if not domain or not self.role_manager:
            return None
        
        best_agent = None
        best_expertise_level = -1
        
        expertise_levels = {
            "novice": 1,
            "competent": 2,
            "proficient": 3,
            "expert": 4,
            "master": 5
        }
        
        for party in parties:
            agent_id = party["agent_id"]
            
            try:
                expertise = self.role_manager.get_agent_expertise_summary(agent_id)
                agent_expertise = expertise.get("expertise", {})
                
                if domain in agent_expertise:
                    level = agent_expertise[domain]["level"]
                    level_value = expertise_levels.get(level, 0)
                    
                    if level_value > best_expertise_level:
                        best_expertise_level = level_value
                        best_agent = agent_id
            except Exception as e:
                logger.warning(f"Could not get expertise for {agent_id}: {e}")
        
        return best_agent
    
    def _get_recent_resource_assignments(self) -> Dict[str, str]:
        """Get recent resource assignments for round-robin fairness."""
        
        # This would typically query a resource assignment database
        # For demo purposes, return empty dict
        return {}
    
    def _calculate_resolution_time(self, conflict: Dict) -> float:
        """Calculate time taken to resolve conflict in hours."""
        
        start_time = datetime.fromisoformat(conflict["reported_at"])
        end_time = datetime.fromisoformat(conflict["resolution_timestamp"])
        
        return (end_time - start_time).total_seconds() / 3600
    
    def get_active_conflicts(self) -> List[Dict]:
        """Get all active conflicts."""
        
        active_conflicts = []
        
        for conflict_id, conflict in self.conflicts_db["conflicts"].items():
            if conflict["status"] in ["open", "in_progress"]:
                # Check if deadline has passed
                deadline = datetime.fromisoformat(conflict["resolution_deadline"])
                if datetime.now() > deadline:
                    self._escalate_conflict(conflict_id, "Resolution deadline exceeded")
                else:
                    active_conflicts.append(conflict)
        
        return sorted(active_conflicts, key=lambda c: c["reported_at"])
    
    def generate_conflict_report(self) -> Dict:
        """Generate conflict resolution statistics."""
        
        all_conflicts = list(self.conflicts_db["conflicts"].values())
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_conflicts": len(all_conflicts),
            "active_conflicts": len(self.get_active_conflicts()),
            "resolved_conflicts": len([c for c in all_conflicts if c["status"] == "resolved"]),
            "escalated_conflicts": len([c for c in all_conflicts if c["status"] == "escalated"]),
            "conflict_types": {},
            "resolution_strategies": {},
            "average_resolution_time_hours": 0,
            "recommendations": []
        }
        
        # Analyze by type
        for conflict in all_conflicts:
            conflict_type = conflict["type"]
            report["conflict_types"][conflict_type] = report["conflict_types"].get(conflict_type, 0) + 1
        
        # Analyze resolution strategies
        for record in self.resolution_history:
            strategy = record["resolution_strategy"]
            report["resolution_strategies"][strategy] = report["resolution_strategies"].get(strategy, 0) + 1
        
        # Calculate average resolution time
        if self.resolution_history:
            total_time = sum(record["resolution_time_hours"] for record in self.resolution_history)
            report["average_resolution_time_hours"] = total_time / len(self.resolution_history)
        
        # Generate recommendations
        if report["escalated_conflicts"] > report["resolved_conflicts"] * 0.2:  # >20% escalation rate
            report["recommendations"].append("High escalation rate detected. Review mediation processes.")
        
        if report["average_resolution_time_hours"] > 12:  # Longer than 12 hours average
            report["recommendations"].append("Long resolution times. Consider more automated strategies.")
        
        most_common_type = max(report["conflict_types"].items(), key=lambda x: x[1])[0] if report["conflict_types"] else None
        if most_common_type:
            report["recommendations"].append(f"Most common conflict type: {most_common_type}. Consider preventive measures.")
        
        return report


def demonstrate_conflict_resolution():
    """Demonstrate the conflict resolution system."""
    
    logger.info("⚖️ Starting Conflict Resolution System Demonstration")
    
    resolver = ConflictResolutionSystem()
    
    print("\n" + "="*60)
    print("⚖️ CONFLICT RESOLUTION DEMO")
    print("="*60)
    
    # Create sample conflicts
    conflicts_to_report = [
        {
            "type": ConflictType.RESOURCE_CONTENTION,
            "severity": ConflictSeverity.MEDIUM,
            "title": "Database access conflict",
            "description": "Multiple agents need exclusive access to user database for migrations",
            "parties": [
                ConflictParty("shark", "Need immediate access for security audit", 
                            "Critical security vulnerabilities found", 9, "security", ["security", "backend"]),
                ConflictParty("whale", "Scheduled maintenance window", 
                            "Pre-planned infrastructure upgrade", 7, "infrastructure", ["infrastructure", "deployment"])
            ],
            "reporter": "shark",
            "metadata": {"resource": "user_database", "domain": "backend"}
        },
        {
            "type": ConflictType.EXPERTISE_DISPUTE,
            "severity": ConflictSeverity.HIGH,
            "title": "Frontend architecture disagreement",
            "description": "Agents disagree on React vs Vue.js for new dashboard",
            "parties": [
                ConflictParty("dolphin", "Vue.js for better performance", 
                            "Lower memory footprint and faster rendering", 6, "frontend", ["frontend", "ui"]),
                ConflictParty("jellyfish", "React for team expertise", 
                            "Team has more React experience", 8, "quality", ["quality", "frontend"])
            ],
            "reporter": "dolphin",
            "metadata": {"domain": "frontend", "decision_type": "architecture"}
        },
        {
            "type": ConflictType.PRIORITY_CONFLICT,
            "severity": ConflictSeverity.LOW,
            "title": "Feature prioritization dispute",
            "description": "Disagreement over next sprint priorities",
            "parties": [
                ConflictParty("octopus", "Analytics dashboard first", 
                            "Business metrics are critical", 5, "analytics", ["data", "analytics"]),
                ConflictParty("seahorse", "API optimization first", 
                            "Performance issues affecting users", 7, "backend", ["backend", "api"])
            ],
            "reporter": "octopus",
            "metadata": {"domain": "product", "sprint": "2025-03"}
        }
    ]
    
    print("\n📝 Reporting conflicts:")
    
    reported_conflicts = []
    for conflict_data in conflicts_to_report:
        conflict_id = resolver.report_conflict(
            conflict_data["type"],
            conflict_data["severity"],
            conflict_data["title"],
            conflict_data["description"],
            conflict_data["parties"],
            conflict_data["reporter"],
            conflict_data["metadata"]
        )
        reported_conflicts.append(conflict_id)
        print(f"   ⚖️ {conflict_data['title']} ({conflict_id})")
    
    # Check active conflicts
    print(f"\n📋 Active conflicts:")
    active_conflicts = resolver.get_active_conflicts()
    for conflict in active_conflicts:
        status_icon = {"open": "🔴", "in_progress": "🟡", "escalated": "🔥"}.get(conflict["status"], "❓")
        print(f"   {status_icon} {conflict['title']} - {conflict['status']}")
        if conflict.get("assigned_mediator"):
            print(f"      👥 Mediator: {conflict['assigned_mediator']}")
        if conflict.get("resolution_strategy"):
            print(f"      🎯 Strategy: {conflict['resolution_strategy']}")
    
    # Generate report
    print(f"\n📊 Conflict resolution report:")
    report = resolver.generate_conflict_report()
    
    print(f"   Total conflicts: {report['total_conflicts']}")
    print(f"   Active: {report['active_conflicts']}, Resolved: {report['resolved_conflicts']}")
    print(f"   Average resolution time: {report['average_resolution_time_hours']:.1f} hours")
    
    if report["conflict_types"]:
        print(f"   Most common type: {max(report['conflict_types'].items(), key=lambda x: x[1])[0]}")
    
    if report["recommendations"]:
        print(f"   Recommendations:")
        for rec in report["recommendations"]:
            print(f"      • {rec}")
    
    print(f"\n💾 Data saved to:")
    print(f"   Conflicts: {resolver.conflicts_db_file}")
    print(f"   Resolutions: {resolver.resolution_history_file}")
    print(f"   Rules: {resolver.mediation_rules_file}")
    
    logger.info("⚖️ Conflict resolution demonstration completed")


if __name__ == "__main__":
    demonstrate_conflict_resolution()