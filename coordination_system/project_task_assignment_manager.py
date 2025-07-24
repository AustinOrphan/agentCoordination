#!/usr/bin/env python3
"""
Project-Aware Task Assignment Manager
Manages task assignments with project context and isolation.
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import logging
from dataclasses import dataclass, asdict

from task_assignment_manager import (
    TaskStatus, TaskPriority, TaskType, Task, AgentCapability,
    TaskAssignmentManager
)
from project_manager import ProjectManager, Project, ProjectStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProjectTask(Task):
    """Extended Task with project context"""
    project_id: str = ""
    project_name: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['task_type'] = self.task_type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectTask':
        """Create from dictionary"""
        # Convert string values back to enums
        data['task_type'] = TaskType(data['task_type'])
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)

class ProjectTaskAssignmentManager(TaskAssignmentManager):
    """Task assignment manager with project awareness"""
    
    def __init__(self, project_manager: ProjectManager, 
                 project_id: Optional[str] = None):
        self.project_manager = project_manager
        self.project_id = project_id
        self.project = None
        
        if project_id:
            self.project = project_manager.get_project(project_id)
            if not self.project:
                raise ValueError(f"Project not found: {project_id}")
        
        # Initialize base class with project-specific paths
        if self.project:
            workspace = project_manager.get_project_workspace(project_id)
            config_file = workspace / "config.json"
            task_queue_file = workspace / "task_assignments" / "task_queue.json"
            
            # Load project configuration for theme
            theme = "ocean_creatures"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                theme = config.get('theme', theme)
            
            # Initialize with project-specific files
            super().__init__(
                config_file=str(workspace.parent.parent / "agent_config.json"),
                task_queue_file=str(task_queue_file)
            )
            
            # Override theme for this project
            self.theme = theme
        else:
            # Global mode - manage all projects
            super().__init__()
        
        # Project-specific task tracking
        self.project_tasks: Dict[str, List[str]] = {}  # project_id -> task_ids
        self.task_projects: Dict[str, str] = {}  # task_id -> project_id
        
        # Load tasks from all projects if in global mode
        if not self.project:
            self._load_all_project_tasks()
    
    def _load_all_project_tasks(self):
        """Load tasks from all active projects"""
        for project in self.project_manager.list_projects(ProjectStatus.ACTIVE):
            workspace = self.project_manager.get_project_workspace(project.project_id)
            if not workspace:
                continue
            
            task_file = workspace / "task_assignments" / "task_queue.json"
            if not task_file.exists():
                continue
            
            try:
                with open(task_file, 'r') as f:
                    data = json.load(f)
                
                project_tasks = []
                for task_dict in data.get('tasks', []):
                    # Add project context
                    task_dict['project_id'] = project.project_id
                    task_dict['project_name'] = project.name
                    
                    # Create ProjectTask
                    task = ProjectTask.from_dict(task_dict)
                    self.tasks[task.task_id] = task
                    project_tasks.append(task.task_id)
                    self.task_projects[task.task_id] = project.project_id
                
                self.project_tasks[project.project_id] = project_tasks
                
                # Add to queue if pending
                for task_id in project_tasks:
                    task = self.tasks[task_id]
                    if task.status == TaskStatus.PENDING and task_id not in self.task_queue:
                        self.task_queue.append(task_id)
                
            except Exception as e:
                logger.error(f"Error loading tasks from project {project.project_id}: {e}")
    
    def create_task(self, title: str, description: str, 
                   task_type: TaskType, priority: TaskPriority,
                   project_id: Optional[str] = None, **kwargs) -> str:
        """Create a new task with project context"""
        # Use instance project if not specified
        if not project_id and self.project:
            project_id = self.project.project_id
        
        if not project_id:
            raise ValueError("Project ID required for task creation")
        
        # Get project
        project = self.project_manager.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Create task
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = ProjectTask(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc).isoformat(),
            estimated_hours=kwargs.get('estimated_hours', 1.0),
            tags=kwargs.get('tags', []),
            dependencies=kwargs.get('dependencies', []),
            deadline=kwargs.get('deadline'),
            project_id=project_id,
            project_name=project.name
        )
        
        # Add to tracking
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        self.task_projects[task_id] = project_id
        
        if project_id not in self.project_tasks:
            self.project_tasks[project_id] = []
        self.project_tasks[project_id].append(task_id)
        
        # Save to project-specific file
        self._save_project_tasks(project_id)
        
        logger.info(f"Created task {task_id} for project {project.name}: {title}")
        return task_id
    
    def _save_project_tasks(self, project_id: str):
        """Save tasks for a specific project"""
        workspace = self.project_manager.get_project_workspace(project_id)
        if not workspace:
            return
        
        task_file = workspace / "task_assignments" / "task_queue.json"
        task_file.parent.mkdir(exist_ok=True)
        
        # Get tasks for this project
        project_task_ids = self.project_tasks.get(project_id, [])
        project_tasks = []
        queue = []
        
        for task_id in project_task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                project_tasks.append(task.to_dict())
                if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
                    queue.append(task_id)
        
        # Save to file
        data = {
            'project_id': project_id,
            'tasks': project_tasks,
            'queue': queue,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        with open(task_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def assign_task_to_agent(self, task_id: str, agent_id: str, 
                           check_project_match: bool = True) -> bool:
        """Assign task to agent with optional project checking"""
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        project_id = self.task_projects.get(task_id)
        
        # Check project match if required
        if check_project_match and project_id:
            # In project-dedicated mode, ensure agent belongs to project
            # This would be enforced by the lifecycle manager
            pass
        
        # Use parent class assignment logic
        success = super().assign_task_to_agent(task_id, agent_id)
        
        if success and project_id:
            # Save to project-specific file
            self._save_project_tasks(project_id)
        
        return success
    
    def get_project_tasks(self, project_id: str, 
                         status_filter: Optional[TaskStatus] = None) -> List[ProjectTask]:
        """Get all tasks for a specific project"""
        task_ids = self.project_tasks.get(project_id, [])
        tasks = []
        
        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if not status_filter or task.status == status_filter:
                    tasks.append(task)
        
        return tasks
    
    def get_project_queue_status(self, project_id: str) -> Dict:
        """Get queue status for a specific project"""
        tasks = self.get_project_tasks(project_id)
        
        return {
            'project_id': project_id,
            'total_tasks': len(tasks),
            'pending': len([t for t in tasks if t.status == TaskStatus.PENDING]),
            'assigned': len([t for t in tasks if t.status == TaskStatus.ASSIGNED]),
            'in_progress': len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            'completed': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            'blocked': len([t for t in tasks if t.status == TaskStatus.BLOCKED])
        }
    
    def get_agent_project_assignments(self) -> Dict[str, Set[str]]:
        """Get which projects each agent is working on"""
        agent_projects = {}
        
        for agent_id, agent in self.agents.items():
            projects = set()
            for task_id in agent.active_tasks:
                if task_id in self.task_projects:
                    projects.add(self.task_projects[task_id])
            agent_projects[agent_id] = projects
        
        return agent_projects
    
    def reassign_project_tasks(self, project_id: str, from_agent: str, to_agent: str):
        """Reassign all tasks from one agent to another within a project"""
        reassigned = 0
        
        task_ids = self.project_tasks.get(project_id, [])
        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.assigned_agent == from_agent and task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                    if self.assign_task_to_agent(task_id, to_agent):
                        reassigned += 1
        
        logger.info(f"Reassigned {reassigned} tasks from {from_agent} to {to_agent} in project {project_id}")
        return reassigned

def main():
    """CLI interface for project task assignment manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project-Aware Task Assignment Manager')
    parser.add_argument('--project', help='Project ID to manage')
    parser.add_argument('--create-task', action='store_true', help='Create a new task')
    parser.add_argument('--list-tasks', action='store_true', help='List project tasks')
    parser.add_argument('--assign', action='store_true', help='Process task assignments')
    parser.add_argument('--status', action='store_true', help='Show queue status')
    
    # Task creation parameters
    parser.add_argument('--title', help='Task title')
    parser.add_argument('--description', help='Task description')
    parser.add_argument('--type', choices=[t.value for t in TaskType], help='Task type')
    parser.add_argument('--priority', choices=[p.value for p in TaskPriority], help='Task priority')
    
    args = parser.parse_args()
    
    # Initialize project manager
    project_manager = ProjectManager()
    
    # Create task manager
    manager = ProjectTaskAssignmentManager(project_manager, args.project)
    
    if args.create_task:
        if not all([args.title, args.description, args.type, args.priority]):
            print("Error: --title, --description, --type, and --priority required for task creation")
            return
        
        task_id = manager.create_task(
            title=args.title,
            description=args.description,
            task_type=TaskType(args.type),
            priority=TaskPriority(args.priority),
            project_id=args.project
        )
        print(f"Created task: {task_id}")
    
    if args.list_tasks:
        if not args.project:
            print("Error: --project required to list tasks")
            return
        
        tasks = manager.get_project_tasks(args.project)
        print(f"Tasks for project {args.project}:")
        for task in tasks:
            print(f"  [{task.status.value}] {task.task_id}: {task.title} ({task.priority.value})")
    
    if args.assign:
        assignments = manager.assign_next_tasks()
        print(f"Made {len(assignments)} task assignments")
    
    if args.status:
        if args.project:
            status = manager.get_project_queue_status(args.project)
            print(f"Queue status for project {args.project}:")
        else:
            status = manager.get_task_queue_status()
            print("Global queue status:")
        
        for key, value in status.items():
            print(f"  {key}: {value}")

if __name__ == '__main__':
    main()