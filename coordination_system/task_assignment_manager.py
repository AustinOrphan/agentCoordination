#!/usr/bin/env python3
"""
Task Assignment Manager
Automatically assigns tasks to agents based on roles, availability, and priorities.
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task lifecycle states"""
    PENDING = "pending"           # Task created, not assigned yet
    ASSIGNED = "assigned"         # Assigned to agent but not started
    IN_PROGRESS = "in_progress"   # Agent actively working on task
    COMPLETED = "completed"       # Task finished successfully
    FAILED = "failed"            # Task failed or cancelled
    BLOCKED = "blocked"          # Task blocked by dependencies
    REASSIGNED = "reassigned"    # Task reassigned to different agent

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"   # Must be done immediately
    HIGH = "high"          # Important, should be done soon  
    NORMAL = "normal"      # Standard priority
    LOW = "low"           # Can be delayed

class TaskType(Enum):
    """Types of tasks that can be assigned"""
    DEVELOPMENT = "development"       # Code implementation
    TESTING = "testing"              # Test creation/execution
    DOCUMENTATION = "documentation"   # Writing docs
    DEPLOYMENT = "deployment"        # DevOps tasks
    SECURITY = "security"           # Security-related tasks
    DESIGN = "design"               # UI/UX design
    RESEARCH = "research"           # Investigation/analysis
    BUGFIX = "bugfix"               # Bug fixing
    REFACTOR = "refactor"           # Code refactoring
    INTEGRATION = "integration"     # System integration

@dataclass
class Task:
    """Represents a task that can be assigned to agents"""
    task_id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    created_at: str
    estimated_hours: float
    tags: List[str]
    dependencies: List[str]  # Task IDs this task depends on
    assigned_agent: Optional[str] = None
    assigned_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    deadline: Optional[str] = None
    progress: int = 0
    blocker_reason: Optional[str] = None
    reassignment_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class AgentCapability:
    """Represents an agent's capabilities and current state"""
    
    def __init__(self, agent_id: str, role: str, theme: str):
        self.agent_id = agent_id
        self.role = role
        self.theme = theme
        self.skills = self._get_role_skills(role)
        self.current_load = 0.0  # 0.0 to 1.0, where 1.0 is fully loaded
        self.active_tasks: List[str] = []
        self.completed_tasks: List[str] = []
        self.performance_score = 1.0  # Performance multiplier
        self.is_available = True
        self.last_assignment = None
        
    def _get_role_skills(self, role: str) -> Dict[TaskType, float]:
        """Map agent roles to task type competencies (0.0 to 1.0)"""
        role_skills = {
            "Critical Path Lead": {
                TaskType.DEVELOPMENT: 0.9,
                TaskType.INTEGRATION: 0.9,
                TaskType.RESEARCH: 0.8,
                TaskType.REFACTOR: 0.8,
                TaskType.BUGFIX: 0.7,
                TaskType.TESTING: 0.6,
                TaskType.DEPLOYMENT: 0.5,
                TaskType.SECURITY: 0.5,
                TaskType.DESIGN: 0.4,
                TaskType.DOCUMENTATION: 0.6
            },
            "Migration Specialist": {
                TaskType.DEVELOPMENT: 0.8,
                TaskType.INTEGRATION: 0.9,
                TaskType.REFACTOR: 0.9,
                TaskType.DEPLOYMENT: 0.7,
                TaskType.BUGFIX: 0.8,
                TaskType.TESTING: 0.7,
                TaskType.RESEARCH: 0.6,
                TaskType.SECURITY: 0.6,
                TaskType.DESIGN: 0.3,
                TaskType.DOCUMENTATION: 0.5
            },
            "Dashboard Developer": {
                TaskType.DEVELOPMENT: 0.9,
                TaskType.DESIGN: 0.8,
                TaskType.TESTING: 0.7,
                TaskType.INTEGRATION: 0.7,
                TaskType.BUGFIX: 0.8,
                TaskType.DOCUMENTATION: 0.6,
                TaskType.REFACTOR: 0.6,
                TaskType.RESEARCH: 0.5,
                TaskType.DEPLOYMENT: 0.4,
                TaskType.SECURITY: 0.4
            },
            "DevOps Engineer": {
                TaskType.DEPLOYMENT: 0.9,
                TaskType.SECURITY: 0.8,
                TaskType.INTEGRATION: 0.8,
                TaskType.TESTING: 0.7,
                TaskType.DEVELOPMENT: 0.6,
                TaskType.BUGFIX: 0.7,
                TaskType.RESEARCH: 0.6,
                TaskType.DOCUMENTATION: 0.6,
                TaskType.REFACTOR: 0.5,
                TaskType.DESIGN: 0.3
            },
            "Security Engineer": {
                TaskType.SECURITY: 0.9,
                TaskType.TESTING: 0.8,
                TaskType.RESEARCH: 0.8,
                TaskType.BUGFIX: 0.7,
                TaskType.DEVELOPMENT: 0.6,
                TaskType.DEPLOYMENT: 0.7,
                TaskType.INTEGRATION: 0.6,
                TaskType.DOCUMENTATION: 0.7,
                TaskType.REFACTOR: 0.5,
                TaskType.DESIGN: 0.3
            },
            "UX Engineer": {
                TaskType.DESIGN: 0.9,
                TaskType.DEVELOPMENT: 0.7,
                TaskType.TESTING: 0.6,
                TaskType.RESEARCH: 0.8,
                TaskType.DOCUMENTATION: 0.7,
                TaskType.INTEGRATION: 0.5,
                TaskType.BUGFIX: 0.6,
                TaskType.REFACTOR: 0.4,
                TaskType.DEPLOYMENT: 0.3,
                TaskType.SECURITY: 0.3
            }
        }
        
        return role_skills.get(role, {task_type: 0.5 for task_type in TaskType})
    
    def get_competency(self, task_type: TaskType) -> float:
        """Get agent's competency for a specific task type"""
        return self.skills.get(task_type, 0.5)
    
    def can_accept_task(self, task: Task) -> bool:
        """Check if agent can accept a new task"""
        if not self.is_available:
            return False
        
        # Check load capacity (assume max 3 concurrent tasks or load < 0.8)
        if len(self.active_tasks) >= 3 or self.current_load >= 0.8:
            return False
        
        # Check minimum competency threshold
        if self.get_competency(task.task_type) < 0.3:
            return False
        
        return True
    
    def calculate_assignment_score(self, task: Task) -> float:
        """Calculate a score for how well this agent fits the task"""
        if not self.can_accept_task(task):
            return 0.0
        
        # Base score from competency
        competency = self.get_competency(task.task_type)
        
        # Priority bonus (critical tasks get priority)
        priority_bonus = {
            TaskPriority.CRITICAL: 0.3,
            TaskPriority.HIGH: 0.2,
            TaskPriority.NORMAL: 0.0,
            TaskPriority.LOW: -0.1
        }.get(task.priority, 0.0)
        
        # Load penalty (less loaded agents preferred)
        load_penalty = self.current_load * 0.2
        
        # Performance bonus
        performance_bonus = (self.performance_score - 1.0) * 0.1
        
        # Avoid reassignment penalty
        reassignment_penalty = task.reassignment_count * 0.1
        
        score = competency + priority_bonus - load_penalty + performance_bonus - reassignment_penalty
        
        return max(0.0, min(1.0, score))

class TaskAssignmentManager:
    """Manages automatic task assignment to agents"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.config_file = config_file
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, AgentCapability] = {}
        self.task_queue: List[str] = []  # Task IDs in priority order
        self.assignment_history: List[Dict] = []
        
        # Storage paths
        self.tasks_file = Path("coordination_system/task_queue.json")
        self.assignments_file = Path("coordination_system/task_assignments.json")
        self.history_file = Path("coordination_system/assignment_history.json")
        
        # Initialize
        self._load_agents()
        self._load_tasks()
        self._load_assignment_history()
        
    def _load_agents(self):
        """Load agent capabilities from configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            current_theme = config.get('current_theme', 'ocean_creatures')
            agent_count = config.get('agent_count', 6)
            theme_data = config.get('themes', {}).get(current_theme, {})
            agents = theme_data.get('agents', [])[:agent_count]
            
            # Standard role mapping (cycles through 6 roles)
            roles = [
                "Critical Path Lead",
                "Migration Specialist", 
                "Dashboard Developer",
                "DevOps Engineer",
                "Security Engineer",
                "UX Engineer"
            ]
            
            for i, agent_id in enumerate(agents):
                role = roles[i % len(roles)]
                self.agents[agent_id] = AgentCapability(agent_id, role, current_theme)
                
            logger.info(f"Loaded {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading agents: {e}")
            # Fallback to default agents
            default_agents = ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]
            roles = ["Critical Path Lead", "Migration Specialist", "Dashboard Developer", 
                    "DevOps Engineer", "Security Engineer", "UX Engineer"]
            
            for i, agent_id in enumerate(default_agents):
                role = roles[i % len(roles)]
                self.agents[agent_id] = AgentCapability(agent_id, role, "ocean_creatures")
    
    def _load_tasks(self):
        """Load existing tasks from storage"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                
                for task_data in data.get('tasks', []):
                    # Convert string values back to enums
                    if 'task_type' in task_data:
                        task_data['task_type'] = TaskType(task_data['task_type'])
                    if 'priority' in task_data:
                        task_data['priority'] = TaskPriority(task_data['priority'])
                    if 'status' in task_data:
                        task_data['status'] = TaskStatus(task_data['status'])
                    
                    task = Task(**task_data)
                    self.tasks[task.task_id] = task
                    
                self.task_queue = data.get('queue', [])
                logger.info(f"Loaded {len(self.tasks)} tasks from storage")
                
            except Exception as e:
                logger.error(f"Error loading tasks: {e}")
    
    def _load_assignment_history(self):
        """Load assignment history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.assignment_history = json.load(f)
                logger.info(f"Loaded {len(self.assignment_history)} assignment records")
            except Exception as e:
                logger.error(f"Error loading assignment history: {e}")
    
    def _save_tasks(self):
        """Save tasks to storage"""
        try:
            self.tasks_file.parent.mkdir(exist_ok=True)
            
            # Convert tasks to serializable format
            serializable_tasks = []
            for task in self.tasks.values():
                task_dict = asdict(task)
                # Convert enums to strings
                task_dict['task_type'] = task.task_type.value
                task_dict['priority'] = task.priority.value
                task_dict['status'] = task.status.value
                serializable_tasks.append(task_dict)
            
            data = {
                'tasks': serializable_tasks,
                'queue': self.task_queue,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def _save_assignment_history(self):
        """Save assignment history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.assignment_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving assignment history: {e}")
    
    def create_task(self, title: str, description: str, task_type: TaskType, 
                   priority: TaskPriority = TaskPriority.NORMAL, 
                   estimated_hours: float = 1.0, tags: List[str] = None,
                   dependencies: List[str] = None, deadline: str = None) -> str:
        """Create a new task and add it to the queue"""
        
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc).isoformat(),
            estimated_hours=estimated_hours,
            tags=tags or [],
            dependencies=dependencies or [],
            deadline=deadline
        )
        
        self.tasks[task_id] = task
        self._add_to_queue(task_id)
        self._save_tasks()
        
        logger.info(f"Created task {task_id}: {title} ({task_type.value}, {priority.value})")
        return task_id
    
    def _add_to_queue(self, task_id: str):
        """Add task to queue in priority order"""
        task = self.tasks[task_id]
        
        # Find insertion point based on priority
        priority_order = [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]
        task_priority_index = priority_order.index(task.priority)
        
        insertion_index = len(self.task_queue)
        for i, queued_task_id in enumerate(self.task_queue):
            queued_task = self.tasks[queued_task_id]
            queued_priority_index = priority_order.index(queued_task.priority)
            
            if task_priority_index < queued_priority_index:
                insertion_index = i
                break
        
        self.task_queue.insert(insertion_index, task_id)
    
    def assign_next_tasks(self) -> List[Dict]:
        """Assign tasks from queue to available agents"""
        assignments = []
        
        # Update agent availability from status files
        self._update_agent_availability()
        
        # Process queue in priority order
        remaining_queue = []
        
        for task_id in self.task_queue:
            if task_id not in self.tasks:
                continue  # Skip removed tasks
                
            task = self.tasks[task_id]
            
            # Skip tasks that are already assigned or completed
            if task.status not in [TaskStatus.PENDING, TaskStatus.BLOCKED]:
                continue
            
            # Check if dependencies are met
            if not self._are_dependencies_met(task):
                task.status = TaskStatus.BLOCKED
                task.blocker_reason = "Waiting for dependencies"
                remaining_queue.append(task_id)
                continue
            
            # Find best agent for this task
            best_agent = self._find_best_agent(task)
            
            if best_agent:
                # Assign task
                assignment = self._assign_task(task, best_agent)
                assignments.append(assignment)
                logger.info(f"Assigned {task_id} to {best_agent.agent_id}")
            else:
                # No available agent, keep in queue
                remaining_queue.append(task_id)
        
        self.task_queue = remaining_queue
        self._save_tasks()
        
        return assignments
    
    def _update_agent_availability(self):
        """Update agent availability from status files"""
        for agent_id, agent in self.agents.items():
            status_file = Path(f"agent_status/{agent_id}_status.json")
            
            if status_file.exists():
                try:
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                    
                    # Check if agent is available
                    current_status = status.get('current_status', {})
                    agent_status = current_status.get('status', '🔵')
                    
                    # Agent is available if status is blue (waiting) or green (completed)
                    agent.is_available = agent_status in ['🔵', '🟢']
                    
                    # Update current load based on progress
                    progress = current_status.get('progress', 0)
                    if progress > 0 and progress < 100:
                        agent.current_load = 0.7  # Working on something
                    elif progress >= 100:
                        agent.current_load = 0.0  # Completed, ready for new task
                    else:
                        agent.current_load = 0.0  # Not working on anything
                        
                except Exception as e:
                    logger.error(f"Error reading status for {agent_id}: {e}")
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_task_id in task.dependencies:
            if dep_task_id in self.tasks:
                dep_task = self.tasks[dep_task_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            else:
                # Dependency task doesn't exist - assume it's met
                continue
        return True
    
    def _find_best_agent(self, task: Task) -> Optional[AgentCapability]:
        """Find the best available agent for a task"""
        available_agents = [agent for agent in self.agents.values() if agent.can_accept_task(task)]
        
        if not available_agents:
            return None
        
        # Score each agent and pick the best
        best_agent = None
        best_score = 0.0
        
        for agent in available_agents:
            score = agent.calculate_assignment_score(task)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent if best_score > 0.3 else None  # Minimum score threshold
    
    def _assign_task(self, task: Task, agent: AgentCapability) -> Dict:
        """Assign a task to an agent"""
        # Update task
        task.status = TaskStatus.ASSIGNED
        task.assigned_agent = agent.agent_id
        task.assigned_at = datetime.now(timezone.utc).isoformat()
        
        # Update agent
        agent.active_tasks.append(task.task_id)
        agent.last_assignment = datetime.now(timezone.utc).isoformat()
        
        # Create assignment record
        assignment = {
            'task_id': task.task_id,
            'agent_id': agent.agent_id,
            'assigned_at': task.assigned_at,
            'task_title': task.title,
            'task_type': task.task_type.value,
            'priority': task.priority.value,
            'estimated_hours': task.estimated_hours,
            'assignment_score': agent.calculate_assignment_score(task)
        }
        
        self.assignment_history.append(assignment)
        self._save_assignment_history()
        
        return assignment
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          progress: int = None, blocker_reason: str = None) -> bool:
        """Update task status and progress"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        old_status = task.status
        task.status = status
        
        if progress is not None:
            task.progress = progress
        
        if blocker_reason:
            task.blocker_reason = blocker_reason
        
        # Update timestamps
        now = datetime.now(timezone.utc).isoformat()
        
        if status == TaskStatus.IN_PROGRESS and old_status == TaskStatus.ASSIGNED:
            task.started_at = now
        elif status == TaskStatus.COMPLETED:
            task.completed_at = now
            # Remove from agent's active tasks
            if task.assigned_agent and task.assigned_agent in self.agents:
                agent = self.agents[task.assigned_agent]
                if task_id in agent.active_tasks:
                    agent.active_tasks.remove(task_id)
                agent.completed_tasks.append(task_id)
        
        self._save_tasks()
        logger.info(f"Updated task {task_id} status: {old_status.value} → {status.value}")
        
        return True
    
    def get_task_queue_status(self) -> Dict:
        """Get current status of task queue and assignments"""
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        assigned_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.ASSIGNED])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        blocked_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        
        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'assigned_tasks': assigned_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'blocked_tasks': blocked_tasks,
            'queue_length': len(self.task_queue),
            'available_agents': len([a for a in self.agents.values() if a.is_available]),
            'busy_agents': len([a for a in self.agents.values() if not a.is_available])
        }
    
    def get_agent_workloads(self) -> Dict:
        """Get current workload for each agent"""
        workloads = {}
        
        for agent_id, agent in self.agents.items():
            active_task_details = []
            for task_id in agent.active_tasks:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    active_task_details.append({
                        'task_id': task_id,
                        'title': task.title,
                        'type': task.task_type.value,
                        'priority': task.priority.value,
                        'progress': task.progress
                    })
            
            workloads[agent_id] = {
                'role': agent.role,
                'is_available': agent.is_available,
                'current_load': agent.current_load,
                'active_tasks_count': len(agent.active_tasks),
                'active_tasks': active_task_details,
                'completed_tasks_count': len(agent.completed_tasks),
                'performance_score': agent.performance_score
            }
        
        return workloads

def main():
    """CLI interface for task assignment manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Assignment Manager')
    parser.add_argument('--assign', action='store_true', help='Process task assignments')
    parser.add_argument('--status', action='store_true', help='Show queue status')
    parser.add_argument('--workloads', action='store_true', help='Show agent workloads')
    parser.add_argument('--create-sample-tasks', action='store_true', help='Create sample tasks for testing')
    
    args = parser.parse_args()
    
    manager = TaskAssignmentManager()
    
    if args.create_sample_tasks:
        # Create some sample tasks for testing
        tasks = [
            ("Implement user authentication", "Create login/logout functionality", TaskType.DEVELOPMENT, TaskPriority.HIGH),
            ("Write API documentation", "Document all REST endpoints", TaskType.DOCUMENTATION, TaskPriority.NORMAL),
            ("Setup CI/CD pipeline", "Configure automated deployment", TaskType.DEPLOYMENT, TaskPriority.HIGH),
            ("Security audit", "Review codebase for vulnerabilities", TaskType.SECURITY, TaskPriority.CRITICAL),
            ("Design user dashboard", "Create mockups for dashboard UI", TaskType.DESIGN, TaskPriority.NORMAL),
            ("Fix login bug", "Resolve issue with session timeout", TaskType.BUGFIX, TaskPriority.HIGH),
            ("Performance testing", "Load test the API endpoints", TaskType.TESTING, TaskPriority.NORMAL),
            ("Database migration", "Migrate from SQLite to PostgreSQL", TaskType.INTEGRATION, TaskPriority.HIGH)
        ]
        
        for title, desc, task_type, priority in tasks:
            task_id = manager.create_task(title, desc, task_type, priority)
            print(f"Created task: {task_id}")
    
    if args.assign:
        assignments = manager.assign_next_tasks()
        print(f"Made {len(assignments)} task assignments:")
        for assignment in assignments:
            print(f"  - {assignment['task_title']} → {assignment['agent_id']}")
    
    if args.status:
        status = manager.get_task_queue_status()
        print("Task Queue Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    if args.workloads:
        workloads = manager.get_agent_workloads()
        print("Agent Workloads:")
        for agent_id, workload in workloads.items():
            print(f"  {agent_id} ({workload['role']}):")
            print(f"    Available: {workload['is_available']}")
            print(f"    Load: {workload['current_load']:.1f}")
            print(f"    Active tasks: {workload['active_tasks_count']}")

if __name__ == '__main__':
    main()