#!/usr/bin/env python3
"""
Domain-Specific Agent Roles System
Dynamically assigns and manages specialized roles based on expertise and workload
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import logging
from enum import Enum
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpertiseLevel(Enum):
    """Expertise levels for domain knowledge."""
    NOVICE = "novice"           # Basic understanding
    COMPETENT = "competent"     # Can handle routine tasks
    PROFICIENT = "proficient"   # Can handle complex tasks
    EXPERT = "expert"           # Can mentor others and handle critical tasks
    MASTER = "master"           # Domain authority, can make architectural decisions

class DomainCategory(Enum):
    """Categories of domain expertise."""
    TECHNICAL = "technical"     # Programming, architecture, systems
    PROCESS = "process"         # DevOps, deployment, monitoring
    QUALITY = "quality"         # Testing, security, performance
    BUSINESS = "business"       # Product, UX, analytics
    SUPPORT = "support"         # Documentation, training, maintenance

@dataclass
class DomainExpertise:
    """Represents expertise in a specific domain."""
    domain: str
    category: str
    level: str
    experience_months: int
    successful_tasks: int
    mentoring_count: int
    last_updated: str
    certification_badges: List[str] = None
    
    def __post_init__(self):
        if self.certification_badges is None:
            self.certification_badges = []

@dataclass
class SpecializedRole:
    """Represents a specialized role an agent can take on."""
    role_id: str
    name: str
    description: str
    required_domains: List[str]
    minimum_expertise_level: str
    responsibilities: List[str]
    authority_grants: List[str]
    availability_requirement: float  # 0.0 to 1.0
    max_concurrent_agents: int
    rotation_interval_days: Optional[int] = None

class DomainSpecificRoleManager:
    """Manages domain-specific roles and agent assignments."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.expertise_db_file = self.project_root / "agent_domain_expertise.json"
        self.roles_db_file = self.project_root / "specialized_roles.json"
        self.assignments_db_file = self.project_root / "role_assignments.json"
        
        # Initialize databases
        self.expertise_db = self._load_expertise_db()
        self.roles_db = self._load_roles_db()
        self.assignments_db = self._load_assignments_db()
        
        # Import related systems
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError as e:
            logger.warning(f"Authority manager not available: {e}")
            self.authority_manager = None
        
        self._initialize_default_roles()
    
    def _load_expertise_db(self) -> Dict:
        """Load agent expertise database."""
        if self.expertise_db_file.exists():
            with open(self.expertise_db_file, 'r') as f:
                return json.load(f)
        return {"agents": {}, "version": "1.0"}
    
    def _save_expertise_db(self):
        """Save expertise database."""
        with open(self.expertise_db_file, 'w') as f:
            json.dump(self.expertise_db, f, indent=2)
    
    def _load_roles_db(self) -> Dict:
        """Load specialized roles database."""
        if self.roles_db_file.exists():
            with open(self.roles_db_file, 'r') as f:
                return json.load(f)
        return {"roles": {}, "version": "1.0"}
    
    def _save_roles_db(self):
        """Save roles database."""
        with open(self.roles_db_file, 'w') as f:
            json.dump(self.roles_db, f, indent=2)
    
    def _load_assignments_db(self) -> Dict:
        """Load role assignments database."""
        if self.assignments_db_file.exists():
            with open(self.assignments_db_file, 'r') as f:
                return json.load(f)
        return {"assignments": {}, "history": [], "version": "1.0"}
    
    def _save_assignments_db(self):
        """Save assignments database."""
        with open(self.assignments_db_file, 'w') as f:
            json.dump(self.assignments_db, f, indent=2)
    
    def _initialize_default_roles(self):
        """Initialize default specialized roles."""
        
        if not self.roles_db["roles"]:  # Only initialize if empty
            default_roles = {
                "security_lead": SpecializedRole(
                    role_id="security_lead",
                    name="Security Lead",
                    description="Leads security initiatives and reviews",
                    required_domains=["security", "backend"],
                    minimum_expertise_level=ExpertiseLevel.PROFICIENT.value,
                    responsibilities=[
                        "Security architecture decisions",
                        "Vulnerability assessment oversight",
                        "Security policy development",
                        "Incident response coordination"
                    ],
                    authority_grants=["security", "emergency_security"],
                    availability_requirement=0.6,
                    max_concurrent_agents=2,
                    rotation_interval_days=90
                ),
                "devops_lead": SpecializedRole(
                    role_id="devops_lead",
                    name="DevOps Lead",
                    description="Manages deployment and infrastructure",
                    required_domains=["infrastructure", "deployment"],
                    minimum_expertise_level=ExpertiseLevel.PROFICIENT.value,
                    responsibilities=[
                        "Infrastructure management",
                        "CI/CD pipeline oversight",
                        "Production deployment decisions",
                        "Monitoring and alerting setup"
                    ],
                    authority_grants=["infrastructure", "deployment"],
                    availability_requirement=0.7,
                    max_concurrent_agents=2,
                    rotation_interval_days=60
                ),
                "quality_assurance_lead": SpecializedRole(
                    role_id="qa_lead",
                    name="Quality Assurance Lead",
                    description="Oversees testing and quality standards",
                    required_domains=["quality", "testing"],
                    minimum_expertise_level=ExpertiseLevel.COMPETENT.value,
                    responsibilities=[
                        "Test strategy development",
                        "Quality gate enforcement",
                        "Performance testing oversight",
                        "Release quality certification"
                    ],
                    authority_grants=["quality", "testing"],
                    availability_requirement=0.5,
                    max_concurrent_agents=1,
                    rotation_interval_days=45
                ),
                "frontend_architect": SpecializedRole(
                    role_id="frontend_architect",
                    name="Frontend Architect",
                    description="Leads frontend architecture and UX decisions",
                    required_domains=["frontend", "ui"],
                    minimum_expertise_level=ExpertiseLevel.PROFICIENT.value,
                    responsibilities=[
                        "Frontend architecture decisions",
                        "UI/UX standards enforcement",
                        "Component library management",
                        "Performance optimization"
                    ],
                    authority_grants=["frontend", "ui"],
                    availability_requirement=0.6,
                    max_concurrent_agents=1,
                    rotation_interval_days=120
                ),
                "backend_architect": SpecializedRole(
                    role_id="backend_architect",
                    name="Backend Architect",
                    description="Leads backend architecture and API design",
                    required_domains=["backend", "api"],
                    minimum_expertise_level=ExpertiseLevel.PROFICIENT.value,
                    responsibilities=[
                        "Backend architecture decisions",
                        "API design standards",
                        "Database schema management",
                        "Microservices coordination"
                    ],
                    authority_grants=["backend", "api", "data"],
                    availability_requirement=0.7,
                    max_concurrent_agents=2,
                    rotation_interval_days=120
                ),
                "data_engineer": SpecializedRole(
                    role_id="data_engineer",
                    name="Data Engineer",
                    description="Manages data systems and analytics",
                    required_domains=["data", "analytics"],
                    minimum_expertise_level=ExpertiseLevel.COMPETENT.value,
                    responsibilities=[
                        "Data pipeline management",
                        "Analytics infrastructure",
                        "Data quality monitoring",
                        "ETL process optimization"
                    ],
                    authority_grants=["data", "analytics"],
                    availability_requirement=0.4,
                    max_concurrent_agents=1,
                    rotation_interval_days=90
                ),
                "mentor": SpecializedRole(
                    role_id="mentor",
                    name="Technical Mentor",
                    description="Provides guidance and knowledge transfer",
                    required_domains=["any_expert_level"],
                    minimum_expertise_level=ExpertiseLevel.EXPERT.value,
                    responsibilities=[
                        "Knowledge transfer sessions",
                        "Code review and guidance",
                        "Best practices evangelism",
                        "Skill development planning"
                    ],
                    authority_grants=["mentoring"],
                    availability_requirement=0.3,
                    max_concurrent_agents=3,
                    rotation_interval_days=180
                )
            }
            
            for role_id, role in default_roles.items():
                self.roles_db["roles"][role_id] = asdict(role)
            
            self._save_roles_db()
            logger.info("Initialized default specialized roles")
    
    def add_agent_expertise(
        self,
        agent_id: str,
        domain: str,
        category: DomainCategory,
        level: ExpertiseLevel,
        experience_months: int = 0,
        certifications: Optional[List[str]] = None
    ):
        """Add or update agent expertise in a domain."""
        
        if agent_id not in self.expertise_db["agents"]:
            self.expertise_db["agents"][agent_id] = {}
        
        expertise = DomainExpertise(
            domain=domain,
            category=category.value,
            level=level.value,
            experience_months=experience_months,
            successful_tasks=0,
            mentoring_count=0,
            last_updated=datetime.now().isoformat(),
            certification_badges=certifications or []
        )
        
        self.expertise_db["agents"][agent_id][domain] = asdict(expertise)
        self._save_expertise_db()
        
        logger.info(f"Added {level.value} expertise in {domain} for agent {agent_id}")
    
    def update_agent_experience(
        self,
        agent_id: str,
        domain: str,
        task_completed: bool = False,
        mentoring_session: bool = False
    ):
        """Update agent experience based on completed activities."""
        
        if (agent_id in self.expertise_db["agents"] and 
            domain in self.expertise_db["agents"][agent_id]):
            
            expertise = self.expertise_db["agents"][agent_id][domain]
            
            if task_completed:
                expertise["successful_tasks"] += 1
                
                # Check for level progression
                self._check_expertise_progression(agent_id, domain, expertise)
            
            if mentoring_session:
                expertise["mentoring_count"] += 1
            
            expertise["last_updated"] = datetime.now().isoformat()
            self._save_expertise_db()
            
            logger.info(f"Updated experience for {agent_id} in {domain}")
    
    def _check_expertise_progression(self, agent_id: str, domain: str, expertise: Dict):
        """Check if agent should be promoted to next expertise level."""
        
        current_level = ExpertiseLevel(expertise["level"])
        successful_tasks = expertise["successful_tasks"]
        experience_months = expertise["experience_months"]
        
        # Progression criteria
        promotion_criteria = {
            ExpertiseLevel.NOVICE: {"tasks": 5, "months": 2},
            ExpertiseLevel.COMPETENT: {"tasks": 15, "months": 6},
            ExpertiseLevel.PROFICIENT: {"tasks": 30, "months": 12},
            ExpertiseLevel.EXPERT: {"tasks": 50, "months": 24}
        }
        
        next_levels = {
            ExpertiseLevel.NOVICE: ExpertiseLevel.COMPETENT,
            ExpertiseLevel.COMPETENT: ExpertiseLevel.PROFICIENT,
            ExpertiseLevel.PROFICIENT: ExpertiseLevel.EXPERT,
            ExpertiseLevel.EXPERT: ExpertiseLevel.MASTER
        }
        
        if current_level in promotion_criteria:
            criteria = promotion_criteria[current_level]
            
            if (successful_tasks >= criteria["tasks"] and 
                experience_months >= criteria["months"]):
                
                new_level = next_levels[current_level]
                expertise["level"] = new_level.value
                
                # Award certification badge
                badge = f"{domain}_{new_level.value}_certified"
                if badge not in expertise["certification_badges"]:
                    expertise["certification_badges"].append(badge)
                
                logger.info(f"🎉 Agent {agent_id} promoted to {new_level.value} in {domain}")
                
                # Check if agent now qualifies for specialized roles
                self._check_role_eligibility(agent_id)
    
    def _check_role_eligibility(self, agent_id: str):
        """Check if agent now qualifies for specialized roles."""
        
        agent_expertise = self.expertise_db["agents"].get(agent_id, {})
        
        for role_id, role_data in self.roles_db["roles"].items():
            if self._agent_qualifies_for_role(agent_id, role_data):
                # Check if role needs more agents
                current_assignments = self._get_current_role_assignments(role_id)
                
                if len(current_assignments) < role_data["max_concurrent_agents"]:
                    logger.info(f"💼 Agent {agent_id} now qualifies for role: {role_data['name']}")
    
    def _agent_qualifies_for_role(self, agent_id: str, role_data: Dict) -> bool:
        """Check if agent qualifies for a specific role."""
        
        agent_expertise = self.expertise_db["agents"].get(agent_id, {})
        required_domains = role_data["required_domains"]
        min_level = ExpertiseLevel(role_data["minimum_expertise_level"])
        
        # Special case for mentor role
        if "any_expert_level" in required_domains:
            for domain, expertise in agent_expertise.items():
                if ExpertiseLevel(expertise["level"]).value in [ExpertiseLevel.EXPERT.value, ExpertiseLevel.MASTER.value]:
                    return True
            return False
        
        # Check if agent has required domains at minimum level
        for domain in required_domains:
            if domain not in agent_expertise:
                return False
            
            agent_level = ExpertiseLevel(agent_expertise[domain]["level"])
            level_hierarchy = [
                ExpertiseLevel.NOVICE,
                ExpertiseLevel.COMPETENT,
                ExpertiseLevel.PROFICIENT,
                ExpertiseLevel.EXPERT,
                ExpertiseLevel.MASTER
            ]
            
            if level_hierarchy.index(agent_level) < level_hierarchy.index(min_level):
                return False
        
        return True
    
    def assign_specialized_role(self, agent_id: str, role_id: str, duration_days: Optional[int] = None) -> bool:
        """Assign a specialized role to an agent."""
        
        if role_id not in self.roles_db["roles"]:
            logger.error(f"Role {role_id} does not exist")
            return False
        
        role_data = self.roles_db["roles"][role_id]
        
        # Check if agent qualifies
        if not self._agent_qualifies_for_role(agent_id, role_data):
            logger.warning(f"Agent {agent_id} does not qualify for role {role_id}")
            return False
        
        # Check if role has available slots
        current_assignments = self._get_current_role_assignments(role_id)
        if len(current_assignments) >= role_data["max_concurrent_agents"]:
            logger.warning(f"Role {role_id} is at maximum capacity")
            return False
        
        # Create assignment
        assignment_id = f"ROLE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{agent_id}-{role_id}"
        
        end_date = None
        if duration_days:
            end_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
        elif role_data.get("rotation_interval_days"):
            end_date = (datetime.now() + timedelta(days=role_data["rotation_interval_days"])).isoformat()
        
        assignment = {
            "assignment_id": assignment_id,
            "agent_id": agent_id,
            "role_id": role_id,
            "assigned_at": datetime.now().isoformat(),
            "assigned_until": end_date,
            "status": "active",
            "authority_grants": role_data["authority_grants"],
            "responsibilities": role_data["responsibilities"]
        }
        
        self.assignments_db["assignments"][assignment_id] = assignment
        
        # Add to history
        self.assignments_db["history"].append({
            "assignment_id": assignment_id,
            "event": "assigned",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "role_id": role_id
        })
        
        self._save_assignments_db()
        
        # Grant authorities through authority manager
        if self.authority_manager:
            for authority in role_data["authority_grants"]:
                try:
                    self.authority_manager.assign_authority(
                        f"Specialized role authority: {role_data['name']}",
                        preferred_agent=agent_id
                    )
                except Exception as e:
                    logger.warning(f"Could not grant authority {authority} to {agent_id}: {e}")
        
        logger.info(f"✅ Assigned role {role_data['name']} to agent {agent_id}")
        return True
    
    def _get_current_role_assignments(self, role_id: str) -> List[Dict]:
        """Get current active assignments for a role."""
        
        active_assignments = []
        current_time = datetime.now()
        
        for assignment_id, assignment in self.assignments_db["assignments"].items():
            if (assignment["role_id"] == role_id and 
                assignment["status"] == "active"):
                
                # Check if assignment has expired
                if assignment.get("assigned_until"):
                    end_time = datetime.fromisoformat(assignment["assigned_until"])
                    if current_time > end_time:
                        # Mark as expired
                        assignment["status"] = "expired"
                        continue
                
                active_assignments.append(assignment)
        
        return active_assignments
    
    def get_agent_roles(self, agent_id: str) -> List[Dict]:
        """Get all active roles for an agent."""
        
        agent_roles = []
        
        for assignment_id, assignment in self.assignments_db["assignments"].items():
            if (assignment["agent_id"] == agent_id and 
                assignment["status"] == "active"):
                
                # Add role details
                role_data = self.roles_db["roles"][assignment["role_id"]]
                assignment["role_details"] = role_data
                agent_roles.append(assignment)
        
        return agent_roles
    
    def get_agent_expertise_summary(self, agent_id: str) -> Dict:
        """Get expertise summary for an agent."""
        
        if agent_id not in self.expertise_db["agents"]:
            return {"agent_id": agent_id, "expertise": {}, "qualified_roles": []}
        
        agent_expertise = self.expertise_db["agents"][agent_id]
        
        # Find qualified roles
        qualified_roles = []
        for role_id, role_data in self.roles_db["roles"].items():
            if self._agent_qualifies_for_role(agent_id, role_data):
                qualified_roles.append({
                    "role_id": role_id,
                    "name": role_data["name"],
                    "available_slots": role_data["max_concurrent_agents"] - len(self._get_current_role_assignments(role_id))
                })
        
        return {
            "agent_id": agent_id,
            "expertise": agent_expertise,
            "qualified_roles": qualified_roles,
            "current_roles": self.get_agent_roles(agent_id)
        }
    
    def generate_team_expertise_report(self) -> Dict:
        """Generate team-wide expertise and role coverage report."""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "team_expertise": {},
            "role_coverage": {},
            "expertise_gaps": [],
            "recommendations": []
        }
        
        # Analyze team expertise
        all_domains = set()
        expertise_by_domain = {}
        
        for agent_id, agent_expertise in self.expertise_db["agents"].items():
            for domain, expertise in agent_expertise.items():
                all_domains.add(domain)
                
                if domain not in expertise_by_domain:
                    expertise_by_domain[domain] = []
                
                expertise_by_domain[domain].append({
                    "agent": agent_id,
                    "level": expertise["level"],
                    "tasks": expertise["successful_tasks"]
                })
        
        report["team_expertise"] = expertise_by_domain
        
        # Analyze role coverage
        for role_id, role_data in self.roles_db["roles"].items():
            current_assignments = self._get_current_role_assignments(role_id)
            qualified_agents = []
            
            for agent_id in self.expertise_db["agents"].keys():
                if self._agent_qualifies_for_role(agent_id, role_data):
                    qualified_agents.append(agent_id)
            
            report["role_coverage"][role_id] = {
                "name": role_data["name"],
                "current_agents": len(current_assignments),
                "max_agents": role_data["max_concurrent_agents"],
                "qualified_agents": len(qualified_agents),
                "coverage_percentage": (len(current_assignments) / role_data["max_concurrent_agents"]) * 100
            }
        
        # Identify gaps and recommendations
        for domain in all_domains:
            experts = [e for e in expertise_by_domain[domain] 
                      if e["level"] in ["expert", "master"]]
            
            if len(experts) < 2:
                report["expertise_gaps"].append(f"Need more {domain} experts")
                report["recommendations"].append(f"Develop {domain} expertise in team members")
        
        for role_id, coverage in report["role_coverage"].items():
            if coverage["coverage_percentage"] < 100:
                if coverage["qualified_agents"] > coverage["current_agents"]:
                    report["recommendations"].append(f"Assign more agents to {coverage['name']} role")
                else:
                    report["recommendations"].append(f"Develop expertise for {coverage['name']} role")
        
        return report


def demonstrate_domain_specific_roles():
    """Demonstrate the domain-specific roles system."""
    
    logger.info("🎭 Starting Domain-Specific Roles System Demonstration")
    
    role_manager = DomainSpecificRoleManager()
    
    # Add expertise for test agents
    test_agents = [
        ("shark", [("security", DomainCategory.QUALITY, ExpertiseLevel.EXPERT, 30),
                  ("backend", DomainCategory.TECHNICAL, ExpertiseLevel.PROFICIENT, 20)]),
        ("dolphin", [("frontend", DomainCategory.TECHNICAL, ExpertiseLevel.PROFICIENT, 18),
                    ("ui", DomainCategory.BUSINESS, ExpertiseLevel.EXPERT, 25)]),
        ("whale", [("infrastructure", DomainCategory.PROCESS, ExpertiseLevel.EXPERT, 36),
                  ("deployment", DomainCategory.PROCESS, ExpertiseLevel.PROFICIENT, 24)]),
        ("octopus", [("data", DomainCategory.TECHNICAL, ExpertiseLevel.PROFICIENT, 15),
                    ("analytics", DomainCategory.TECHNICAL, ExpertiseLevel.COMPETENT, 10)]),
        ("jellyfish", [("quality", DomainCategory.QUALITY, ExpertiseLevel.PROFICIENT, 20),
                      ("testing", DomainCategory.QUALITY, ExpertiseLevel.EXPERT, 28)]),
        ("seahorse", [("backend", DomainCategory.TECHNICAL, ExpertiseLevel.MASTER, 48),
                     ("api", DomainCategory.TECHNICAL, ExpertiseLevel.EXPERT, 40)])
    ]
    
    print("\n" + "="*60)
    print("🧠 SETTING UP AGENT EXPERTISE")
    print("="*60)
    
    for agent_id, expertise_list in test_agents:
        for domain, category, level, months in expertise_list:
            role_manager.add_agent_expertise(agent_id, domain, category, level, months)
            print(f"✅ {agent_id}: {level.value} in {domain}")
    
    # Simulate some task completions to trigger progression
    print("\n" + "="*60)
    print("📈 SIMULATING EXPERIENCE GAIN")
    print("="*60)
    
    simulation_data = [
        ("octopus", "data", 10, 2),  # 10 tasks, 2 mentoring sessions
        ("dolphin", "frontend", 8, 1),
        ("jellyfish", "quality", 15, 3),
    ]
    
    for agent, domain, tasks, mentoring in simulation_data:
        for _ in range(tasks):
            role_manager.update_agent_experience(agent, domain, task_completed=True)
        for _ in range(mentoring):
            role_manager.update_agent_experience(agent, domain, mentoring_session=True)
        print(f"📊 {agent}: +{tasks} tasks, +{mentoring} mentoring in {domain}")
    
    # Assign specialized roles
    print("\n" + "="*60)
    print("👥 ASSIGNING SPECIALIZED ROLES")
    print("="*60)
    
    role_assignments = [
        ("shark", "security_lead"),
        ("whale", "devops_lead"),
        ("jellyfish", "qa_lead"),
        ("dolphin", "frontend_architect"),
        ("seahorse", "backend_architect"),
        ("seahorse", "mentor")  # Can have multiple roles
    ]
    
    for agent, role in role_assignments:
        success = role_manager.assign_specialized_role(agent, role)
        status = "✅" if success else "❌"
        print(f"{status} {agent} → {role}")
    
    # Generate expertise summaries
    print("\n" + "="*60)
    print("📋 AGENT EXPERTISE SUMMARIES")
    print("="*60)
    
    for agent_id, _ in test_agents:
        summary = role_manager.get_agent_expertise_summary(agent_id)
        
        print(f"\n🤖 Agent {agent_id.upper()}:")
        
        # Show expertise
        for domain, expertise in summary["expertise"].items():
            level = expertise["level"]
            tasks = expertise["successful_tasks"]
            badges = len(expertise["certification_badges"])
            print(f"   🎯 {domain}: {level} ({tasks} tasks, {badges} badges)")
        
        # Show current roles
        if summary["current_roles"]:
            print(f"   👥 Active Roles:")
            for role in summary["current_roles"]:
                print(f"      • {role['role_details']['name']}")
        
        # Show qualified roles
        if summary["qualified_roles"]:
            available_roles = [r for r in summary["qualified_roles"] if r["available_slots"] > 0]
            if available_roles:
                print(f"   💼 Available Roles: {', '.join([r['name'] for r in available_roles])}")
    
    # Generate team report
    print("\n" + "="*60)
    print("📊 TEAM EXPERTISE REPORT")
    print("="*60)
    
    team_report = role_manager.generate_team_expertise_report()
    
    print(f"🎯 Domain Coverage:")
    for domain, experts in team_report["team_expertise"].items():
        expert_count = len([e for e in experts if e["level"] in ["expert", "master"]])
        total_count = len(experts)
        print(f"   {domain}: {expert_count}/{total_count} experts")
    
    print(f"\n👥 Role Coverage:")
    for role_id, coverage in team_report["role_coverage"].items():
        percentage = coverage["coverage_percentage"]
        status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
        print(f"   {status} {coverage['name']}: {coverage['current_agents']}/{coverage['max_agents']} ({percentage:.0f}%)")
    
    if team_report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in team_report["recommendations"][:3]:  # Show top 3
            print(f"   • {rec}")
    
    logger.info("🎭 Domain-Specific Roles System demonstration completed")


if __name__ == "__main__":
    demonstrate_domain_specific_roles()