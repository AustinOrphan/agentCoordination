#!/usr/bin/env python3
"""
Emergency Protocol Framework
Handles critical system situations requiring immediate coordinated response
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmergencyLevel(Enum):
    """Emergency severity levels."""
    LOW = "low"              # Minor issues, planned response
    MEDIUM = "medium"        # Significant issues requiring coordination
    HIGH = "high"            # Critical issues requiring immediate action
    CRITICAL = "critical"    # System-threatening issues, all-hands response

class EmergencyType(Enum):
    """Types of emergencies."""
    SECURITY_BREACH = "security_breach"
    DATA_CORRUPTION = "data_corruption"
    SYSTEM_OUTAGE = "system_outage"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DEPLOYMENT_FAILURE = "deployment_failure"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    CODE_REGRESSION = "code_regression"
    DEPENDENCY_FAILURE = "dependency_failure"

class EmergencyProtocolFramework:
    """Manages emergency response protocols and coordination."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.emergency_log_file = self.project_root / "EMERGENCY_LOG.json"
        self.protocol_definitions_file = self.project_root / "EMERGENCY_PROTOCOLS.json"
        self.active_emergencies_file = self.project_root / "ACTIVE_EMERGENCIES.json"
        
        # Import authority manager
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError as e:
            logger.warning(f"Authority manager not available: {e}")
            self.authority_manager = None
        
        self.initialize_protocols()
    
    def initialize_protocols(self):
        """Initialize emergency protocol definitions."""
        default_protocols = {
            "protocols": {
                "security_breach": {
                    "name": "Security Breach Response",
                    "severity_levels": {
                        "low": {
                            "response_time_minutes": 60,
                            "required_roles": ["security"],
                            "escalation_threshold_minutes": 120,
                            "actions": [
                                "Identify breach scope",
                                "Assess data exposure risk",
                                "Document incident details",
                                "Implement containment measures"
                            ]
                        },
                        "high": {
                            "response_time_minutes": 15,
                            "required_roles": ["security", "infrastructure", "backend"],
                            "escalation_threshold_minutes": 30,
                            "actions": [
                                "IMMEDIATE: Isolate affected systems",
                                "IMMEDIATE: Revoke potentially compromised credentials",
                                "Alert all stakeholders",
                                "Begin forensic analysis",
                                "Prepare public communication"
                            ]
                        },
                        "critical": {
                            "response_time_minutes": 5,
                            "required_roles": ["all_available"],
                            "escalation_threshold_minutes": 10,
                            "actions": [
                                "IMMEDIATE: Activate incident command",
                                "IMMEDIATE: Isolate all systems",
                                "IMMEDIATE: Contact external security team",
                                "IMMEDIATE: Prepare emergency shutdown procedures",
                                "Coordinate with legal and compliance teams"
                            ]
                        }
                    }
                },
                "system_outage": {
                    "name": "System Outage Response",
                    "severity_levels": {
                        "medium": {
                            "response_time_minutes": 30,
                            "required_roles": ["infrastructure", "backend"],
                            "escalation_threshold_minutes": 60,
                            "actions": [
                                "Assess outage scope",
                                "Check monitoring systems",
                                "Review recent deployments",
                                "Begin service restoration"
                            ]
                        },
                        "critical": {
                            "response_time_minutes": 10,
                            "required_roles": ["infrastructure", "backend", "frontend"],
                            "escalation_threshold_minutes": 20,
                            "actions": [
                                "IMMEDIATE: Activate war room",
                                "IMMEDIATE: Check all critical services",
                                "IMMEDIATE: Begin rollback procedures",
                                "Update status page",
                                "Coordinate customer communication"
                            ]
                        }
                    }
                },
                "data_corruption": {
                    "name": "Data Corruption Response",
                    "severity_levels": {
                        "high": {
                            "response_time_minutes": 15,
                            "required_roles": ["data", "backend", "infrastructure"],
                            "escalation_threshold_minutes": 30,
                            "actions": [
                                "IMMEDIATE: Stop all data writes",
                                "IMMEDIATE: Identify corruption scope",
                                "Begin backup restoration assessment",
                                "Notify affected users",
                                "Document corruption patterns"
                            ]
                        },
                        "critical": {
                            "response_time_minutes": 5,
                            "required_roles": ["all_available"],
                            "escalation_threshold_minutes": 15,
                            "actions": [
                                "IMMEDIATE: Stop all database operations",
                                "IMMEDIATE: Activate data recovery team",
                                "IMMEDIATE: Begin emergency backup procedures",
                                "Contact data recovery specialists",
                                "Prepare for extended downtime"
                            ]
                        }
                    }
                }
            },
            "escalation_matrix": {
                "low": "medium",
                "medium": "high", 
                "high": "critical",
                "critical": "external_support"
            },
            "notification_channels": {
                "internal": ["email", "slack", "status_update"],
                "external": ["status_page", "social_media", "customer_email"],
                "emergency": ["sms", "phone_call", "pager"]
            }
        }
        
        if not self.protocol_definitions_file.exists():
            with open(self.protocol_definitions_file, 'w') as f:
                json.dump(default_protocols, f, indent=2)
            logger.info("Created default emergency protocols")
    
    def declare_emergency(
        self, 
        emergency_type: EmergencyType, 
        level: EmergencyLevel,
        description: str,
        reporter_agent: str,
        additional_context: Optional[Dict] = None
    ) -> str:
        """Declare an emergency and activate response protocols."""
        
        emergency_id = f"EMG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        emergency_record = {
            "id": emergency_id,
            "type": emergency_type.value,
            "level": level.value,
            "description": description,
            "reporter_agent": reporter_agent,
            "declared_at": datetime.now().isoformat(),
            "status": "active",
            "additional_context": additional_context or {},
            "response_log": [],
            "assigned_agents": [],
            "escalations": []
        }
        
        logger.critical(f"🚨 EMERGENCY DECLARED: {emergency_id}")
        logger.critical(f"Type: {emergency_type.value}, Level: {level.value}")
        logger.critical(f"Description: {description}")
        
        # Save to active emergencies
        self._save_active_emergency(emergency_record)
        
        # Activate response protocol
        self._activate_response_protocol(emergency_record)
        
        # Log the emergency
        self._log_emergency_event(emergency_record, "declared")
        
        return emergency_id
    
    def _activate_response_protocol(self, emergency_record: Dict):
        """Activate the appropriate response protocol for the emergency."""
        
        with open(self.protocol_definitions_file, 'r') as f:
            protocols = json.load(f)
        
        emergency_type = emergency_record["type"]
        emergency_level = emergency_record["level"]
        
        if emergency_type in protocols["protocols"]:
            protocol = protocols["protocols"][emergency_type]
            
            if emergency_level in protocol["severity_levels"]:
                level_config = protocol["severity_levels"][emergency_level]
                
                logger.info(f"Activating protocol: {protocol['name']} (Level: {emergency_level})")
                
                # Assign required agents
                self._assign_emergency_response_team(emergency_record, level_config)
                
                # Set response timeline
                response_time = level_config["response_time_minutes"]
                escalation_time = level_config["escalation_threshold_minutes"]
                
                emergency_record["response_deadline"] = (
                    datetime.now() + timedelta(minutes=response_time)
                ).isoformat()
                emergency_record["escalation_deadline"] = (
                    datetime.now() + timedelta(minutes=escalation_time)
                ).isoformat()
                
                # Execute immediate actions
                self._execute_immediate_actions(emergency_record, level_config["actions"])
                
                logger.info(f"Protocol activated. Response required within {response_time} minutes")
                
            else:
                logger.warning(f"No protocol defined for {emergency_type} at level {emergency_level}")
        else:
            logger.warning(f"No protocol defined for emergency type: {emergency_type}")
    
    def _assign_emergency_response_team(self, emergency_record: Dict, level_config: Dict):
        """Assign appropriate agents to emergency response."""
        
        required_roles = level_config.get("required_roles", [])
        
        if "all_available" in required_roles:
            # Critical emergency - assign all available agents
            if self.authority_manager:
                active_agents = self.authority_manager.get_active_agents()
                emergency_record["assigned_agents"] = active_agents
                logger.critical(f"ALL HANDS: Assigned {len(active_agents)} agents to emergency")
            else:
                emergency_record["assigned_agents"] = ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]
                logger.critical("ALL HANDS: Assigned all configured agents")
        else:
            # Assign based on required roles
            assigned_agents = []
            
            if self.authority_manager:
                # Use authority manager to find suitable agents
                for role in required_roles:
                    # Map roles to domains
                    domain_mapping = {
                        "security": "security",
                        "infrastructure": "infrastructure", 
                        "backend": "backend",
                        "frontend": "frontend",
                        "data": "data",
                        "quality": "quality"
                    }
                    
                    if role in domain_mapping:
                        # Try to assign emergency authority for this domain
                        try:
                            result = self.authority_manager.assign_authority(
                                f"Emergency response: {emergency_record['description']}",
                                task_type="emergency"
                            )
                            if result.get('agent'):
                                assigned_agents.append(result['agent'])
                        except Exception as e:
                            logger.warning(f"Could not assign emergency authority for {role}: {e}")
            
            # Fallback to basic assignment
            if not assigned_agents:
                role_agent_mapping = {
                    "security": "shark",
                    "infrastructure": "whale", 
                    "backend": "octopus",
                    "frontend": "dolphin",
                    "data": "jellyfish",
                    "quality": "seahorse"
                }
                assigned_agents = [role_agent_mapping.get(role, "shark") for role in required_roles]
            
            emergency_record["assigned_agents"] = list(set(assigned_agents))  # Remove duplicates
            logger.info(f"Assigned emergency response team: {', '.join(emergency_record['assigned_agents'])}")
    
    def _execute_immediate_actions(self, emergency_record: Dict, actions: List[str]):
        """Execute immediate response actions."""
        
        immediate_actions = [action for action in actions if action.startswith("IMMEDIATE:")]
        
        for action in immediate_actions:
            action_clean = action.replace("IMMEDIATE: ", "")
            
            action_record = {
                "timestamp": datetime.now().isoformat(),
                "action": action_clean,
                "status": "executed",
                "executed_by": "emergency_framework"
            }
            
            emergency_record["response_log"].append(action_record)
            logger.critical(f"IMMEDIATE ACTION: {action_clean}")
            
            # Simulate action execution
            time.sleep(0.1)  # Small delay to simulate action
    
    def update_emergency_status(
        self, 
        emergency_id: str, 
        agent_id: str, 
        status_update: str,
        progress_percentage: Optional[int] = None
    ):
        """Update emergency response status."""
        
        active_emergencies = self._load_active_emergencies()
        
        if emergency_id in active_emergencies:
            emergency = active_emergencies[emergency_id]
            
            status_record = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_id,
                "update": status_update,
                "progress": progress_percentage
            }
            
            emergency["response_log"].append(status_record)
            
            # Save updated emergency
            self._save_active_emergency(emergency)
            
            logger.info(f"Emergency {emergency_id} status update from {agent_id}: {status_update}")
            
            # Check if emergency should be escalated
            self._check_escalation_triggers(emergency)
        else:
            logger.warning(f"Emergency {emergency_id} not found in active emergencies")
    
    def resolve_emergency(self, emergency_id: str, resolution_summary: str, resolved_by: str):
        """Resolve an emergency and clean up resources."""
        
        active_emergencies = self._load_active_emergencies()
        
        if emergency_id in active_emergencies:
            emergency = active_emergencies[emergency_id]
            
            emergency["status"] = "resolved"
            emergency["resolved_at"] = datetime.now().isoformat()
            emergency["resolved_by"] = resolved_by
            emergency["resolution_summary"] = resolution_summary
            
            # Calculate response time
            declared_time = datetime.fromisoformat(emergency["declared_at"])
            resolved_time = datetime.now()
            response_duration = (resolved_time - declared_time).total_seconds() / 60
            emergency["response_duration_minutes"] = response_duration
            
            # Log final resolution
            self._log_emergency_event(emergency, "resolved")
            
            # Release emergency authorities
            self._release_emergency_authorities(emergency)
            
            # Remove from active emergencies
            del active_emergencies[emergency_id]
            self._save_all_active_emergencies(active_emergencies)
            
            logger.info(f"✅ Emergency {emergency_id} resolved after {response_duration:.1f} minutes")
            logger.info(f"Resolution: {resolution_summary}")
            
        else:
            logger.warning(f"Emergency {emergency_id} not found")
    
    def _check_escalation_triggers(self, emergency: Dict):
        """Check if emergency needs to be escalated."""
        
        if "escalation_deadline" in emergency:
            escalation_time = datetime.fromisoformat(emergency["escalation_deadline"])
            
            if datetime.now() > escalation_time and emergency["status"] == "active":
                # Escalate emergency
                current_level = emergency["level"]
                
                with open(self.protocol_definitions_file, 'r') as f:
                    protocols = json.load(f)
                
                escalation_matrix = protocols.get("escalation_matrix", {})
                next_level = escalation_matrix.get(current_level)
                
                if next_level and next_level != "external_support":
                    logger.warning(f"🔥 ESCALATING Emergency {emergency['id']} from {current_level} to {next_level}")
                    
                    emergency["level"] = next_level
                    emergency["escalations"].append({
                        "from_level": current_level,
                        "to_level": next_level,
                        "escalated_at": datetime.now().isoformat(),
                        "reason": "escalation_deadline_exceeded"
                    })
                    
                    # Re-activate protocol with new level
                    self._activate_response_protocol(emergency)
                    
                elif next_level == "external_support":
                    logger.critical(f"🆘 Emergency {emergency['id']} requires EXTERNAL SUPPORT")
    
    def _release_emergency_authorities(self, emergency: Dict):
        """Release emergency authorities granted during the incident."""
        
        if self.authority_manager and emergency.get("assigned_agents"):
            for agent in emergency["assigned_agents"]:
                try:
                    # Get current authorities for the agent
                    authorities = self.authority_manager.get_agent_authorities(agent)
                    emergency_authorities = [a for a in authorities if a.get('authority_type') == 'emergency']
                    
                    for auth in emergency_authorities:
                        if emergency["description"] in auth.get("task", ""):
                            self.authority_manager.release_authority(auth["id"], agent)
                            logger.info(f"Released emergency authority from {agent}")
                except Exception as e:
                    logger.warning(f"Could not release emergency authority from {agent}: {e}")
    
    def _load_active_emergencies(self) -> Dict:
        """Load active emergencies from file."""
        if self.active_emergencies_file.exists():
            with open(self.active_emergencies_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_active_emergency(self, emergency: Dict):
        """Save a single emergency to active emergencies."""
        active_emergencies = self._load_active_emergencies()
        active_emergencies[emergency["id"]] = emergency
        self._save_all_active_emergencies(active_emergencies)
    
    def _save_all_active_emergencies(self, emergencies: Dict):
        """Save all active emergencies to file."""
        with open(self.active_emergencies_file, 'w') as f:
            json.dump(emergencies, f, indent=2)
    
    def _log_emergency_event(self, emergency: Dict, event_type: str):
        """Log emergency event to permanent log."""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "emergency_id": emergency["id"],
            "event_type": event_type,
            "emergency_data": emergency.copy()
        }
        
        # Load existing log
        emergency_log = []
        if self.emergency_log_file.exists():
            with open(self.emergency_log_file, 'r') as f:
                emergency_log = json.load(f)
        
        emergency_log.append(log_entry)
        
        # Save updated log
        with open(self.emergency_log_file, 'w') as f:
            json.dump(emergency_log, f, indent=2)
    
    def get_active_emergencies(self) -> Dict:
        """Get all currently active emergencies."""
        return self._load_active_emergencies()
    
    def get_emergency_status(self, emergency_id: str) -> Optional[Dict]:
        """Get status of a specific emergency."""
        active_emergencies = self._load_active_emergencies()
        return active_emergencies.get(emergency_id)


def demonstrate_emergency_scenarios():
    """Demonstrate various emergency scenarios."""
    
    logger.info("🚨 Starting Emergency Protocol Framework Demonstration")
    
    framework = EmergencyProtocolFramework()
    
    # Scenario 1: Security Breach
    print("\n" + "="*60)
    print("🛡️ SCENARIO 1: SECURITY BREACH")
    print("="*60)
    
    emergency_id_1 = framework.declare_emergency(
        emergency_type=EmergencyType.SECURITY_BREACH,
        level=EmergencyLevel.HIGH,
        description="Unauthorized access detected in user authentication system",
        reporter_agent="security_monitor",
        additional_context={"affected_users": 1500, "breach_vector": "SQL injection"}
    )
    
    # Simulate response updates
    time.sleep(1)
    framework.update_emergency_status(
        emergency_id_1, 
        "shark", 
        "Isolated affected authentication endpoints",
        25
    )
    
    time.sleep(1)
    framework.update_emergency_status(
        emergency_id_1,
        "whale",
        "Deployed security patches to all servers", 
        50
    )
    
    time.sleep(1)
    framework.resolve_emergency(
        emergency_id_1,
        "Security breach contained. All affected users notified and passwords reset.",
        "shark"
    )
    
    # Scenario 2: Critical System Outage
    print("\n" + "="*60)
    print("⚡ SCENARIO 2: CRITICAL SYSTEM OUTAGE")
    print("="*60)
    
    emergency_id_2 = framework.declare_emergency(
        emergency_type=EmergencyType.SYSTEM_OUTAGE,
        level=EmergencyLevel.CRITICAL,
        description="Complete system outage affecting all services",
        reporter_agent="monitoring_system",
        additional_context={"affected_services": "all", "estimated_users_affected": 50000}
    )
    
    # Show active emergencies
    print(f"\nActive emergencies: {len(framework.get_active_emergencies())}")
    
    # Simulate partial resolution
    time.sleep(1)
    framework.update_emergency_status(
        emergency_id_2,
        "whale", 
        "Database cluster restored, services coming online",
        75
    )
    
    time.sleep(1)
    framework.resolve_emergency(
        emergency_id_2,
        "All services restored. Root cause: Database connection pool exhaustion.",
        "whale"
    )
    
    # Scenario 3: Data Corruption (Critical)
    print("\n" + "="*60)
    print("💾 SCENARIO 3: CRITICAL DATA CORRUPTION")
    print("="*60)
    
    emergency_id_3 = framework.declare_emergency(
        emergency_type=EmergencyType.DATA_CORRUPTION,
        level=EmergencyLevel.CRITICAL,
        description="Widespread data corruption detected in user profiles database",
        reporter_agent="data_integrity_monitor",
        additional_context={"corrupted_records": 25000, "corruption_type": "schema_mismatch"}
    )
    
    print(f"\nFinal active emergencies: {len(framework.get_active_emergencies())}")
    
    logger.info("🎯 Emergency Protocol Framework demonstration completed")


if __name__ == "__main__":
    demonstrate_emergency_scenarios()