#!/usr/bin/env python3
"""
Global Task Pool Manager
Implements cross-project priority-based task assignment for optimal agent utilization.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import heapq

from task_assignment_manager import TaskStatus, TaskPriority, TaskType, AgentCapability
from project_task_assignment_manager import ProjectTask
from project_manager import ProjectManager, Project, ProjectStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class GlobalTask:
    """Task with project context for global priority queue"""
    task: ProjectTask
    project_id: str
    project_name: str
    project_priority: float = 1.0  # Project-level priority multiplier
    global_score: float = 0.0
    
    def __lt__(self, other):
        """For heap priority queue - higher score = higher priority"""
        return self.global_score > other.global_score

class PoolMode(Enum):
    """Agent pool assignment modes"""
    PROJECT_DEDICATED = "project_dedicated"  # Agents assigned to specific projects
    GLOBAL_PRIORITY = "global_priority"      # Agents assigned by global priority
    HYBRID = "hybrid"                       # Mix of dedicated and pool agents

class GlobalTaskPoolManager:
    """Manages task assignments across multiple projects with global prioritization"""
    
    def __init__(self, project_manager: ProjectManager, pool_mode: PoolMode = PoolMode.GLOBAL_PRIORITY):
        self.project_manager = project_manager
        self.pool_mode = pool_mode
        self.global_task_queue: List[GlobalTask] = []
        self.agent_pool: Dict[str, AgentCapability] = {}
        self.agent_assignments: Dict[str, str] = {}  # agent_id -> project_id
        self.project_priorities: Dict[str, float] = {}  # project_id -> priority multiplier
        
        # Configuration
        self.config_file = Path("coordination_system/global_pool_config.json")
        self.load_config()
        
    def load_config(self):
        """Load global pool configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.pool_mode = PoolMode(config.get('pool_mode', 'global_priority'))
                self.project_priorities = config.get('project_priorities', {})
            except Exception as e:
                logger.error(f"Error loading global pool config: {e}")
    
    def save_config(self):
        """Save global pool configuration"""
        config = {
            'pool_mode': self.pool_mode.value,
            'project_priorities': self.project_priorities,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def set_pool_mode(self, mode: PoolMode):
        """Change the agent pool assignment mode"""
        self.pool_mode = mode
        self.save_config()
        logger.info(f"Set pool mode to: {mode.value}")
    
    def set_project_priority(self, project_id: str, priority: float):
        """Set project-level priority multiplier (0.1 to 2.0)"""
        priority = max(0.1, min(2.0, priority))  # Clamp to reasonable range
        self.project_priorities[project_id] = priority
        self.save_config()
        logger.info(f"Set project {project_id} priority to {priority}")
    
    def collect_all_tasks(self) -> List[GlobalTask]:
        """Collect all pending tasks from all active projects"""
        global_tasks = []
        
        for project in self.project_manager.list_projects(ProjectStatus.ACTIVE):
            # Skip if project workspace doesn't exist
            workspace = self.project_manager.get_project_workspace(project.project_id)
            if not workspace:
                continue
            
            # Load tasks from project
            task_file = workspace / "task_assignments" / "task_queue.json"
            if not task_file.exists():
                continue
            
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                
                tasks = task_data.get('tasks', [])
                project_priority = self.project_priorities.get(project.project_id, 1.0)
                
                for task_dict in tasks:
                    # Skip non-pending tasks
                    if task_dict.get('status') not in ['pending', 'assigned']:
                        continue
                    
                    # Convert to ProjectTask object
                    task = self._dict_to_task(task_dict, project.project_id, project.name)
                    
                    # Create GlobalTask with scoring
                    global_task = GlobalTask(
                        task=task,
                        project_id=project.project_id,
                        project_name=project.name,
                        project_priority=project_priority
                    )
                    
                    # Calculate global priority score
                    global_task.global_score = self._calculate_global_score(
                        task, project_priority
                    )
                    
                    global_tasks.append(global_task)
                    
            except Exception as e:
                logger.error(f"Error loading tasks from project {project.project_id}: {e}")
        
        return global_tasks
    
    def _dict_to_task(self, task_dict: Dict, project_id: str, project_name: str) -> ProjectTask:
        """Convert task dictionary to ProjectTask object"""
        # Add project context
        task_dict['project_id'] = project_id
        task_dict['project_name'] = project_name
        
        # Use ProjectTask's from_dict method
        return ProjectTask.from_dict(task_dict)
    
    def _calculate_global_score(self, task: ProjectTask, project_priority: float) -> float:
        """Calculate global priority score for a task"""
        # Base score from task priority
        priority_scores = {
            TaskPriority.CRITICAL: 1000.0,
            TaskPriority.HIGH: 100.0,
            TaskPriority.NORMAL: 10.0,
            TaskPriority.LOW: 1.0
        }
        base_score = priority_scores.get(task.priority, 10.0)
        
        # Apply project priority multiplier
        score = base_score * project_priority
        
        # Age factor (older tasks get slight boost)
        try:
            created = datetime.fromisoformat(task.created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(timezone.utc) - created).days
            age_bonus = min(age_days * 0.1, 5.0)  # Max 5 point bonus for age
            score += age_bonus
        except:
            pass
        
        # Dependency factor (tasks with no dependencies get boost)
        if not task.dependencies:
            score *= 1.2
        
        # Estimated time factor (shorter tasks get slight boost for quick wins)
        if task.estimated_hours < 2:
            score *= 1.1
        
        return score
    
    def build_global_queue(self) -> List[GlobalTask]:
        """Build and sort the global task queue by priority"""
        self.global_task_queue = self.collect_all_tasks()
        
        # Sort by global score (highest first)
        self.global_task_queue.sort(key=lambda gt: gt.global_score, reverse=True)
        
        logger.info(f"Built global queue with {len(self.global_task_queue)} tasks")
        return self.global_task_queue
    
    def get_agent_pool(self) -> Dict[str, AgentCapability]:
        """Get all available agents from all projects"""
        all_agents = {}
        
        if self.pool_mode == PoolMode.GLOBAL_PRIORITY:
            # In global mode, all agents go into the pool
            total_agent_count = sum(
                p.agent_count for p in self.project_manager.list_projects(ProjectStatus.ACTIVE)
            )
            
            # Create a pool of agents
            # Note: In real implementation, these would come from actual agent configs
            roles = [
                "Critical Path Lead",
                "Migration Specialist", 
                "Dashboard Developer",
                "DevOps Engineer",
                "Security Engineer",
                "UX Engineer"
            ]
            
            for i in range(total_agent_count):
                agent_id = f"agent_{i+1}"
                role = roles[i % len(roles)]
                all_agents[agent_id] = AgentCapability(agent_id, role, "global_pool")
                
        elif self.pool_mode == PoolMode.PROJECT_DEDICATED:
            # In dedicated mode, agents are tied to projects
            for project in self.project_manager.list_projects(ProjectStatus.ACTIVE):
                for i in range(project.agent_count):
                    agent_id = f"{project.project_id}_agent_{i+1}"
                    role = roles[i % len(roles)]
                    agent = AgentCapability(agent_id, role, project.project_id)
                    all_agents[agent_id] = agent
                    self.agent_assignments[agent_id] = project.project_id
                    
        else:  # HYBRID mode
            # Mix of dedicated and pool agents
            # Implementation depends on specific requirements
            pass
        
        self.agent_pool = all_agents
        return all_agents
    
    def assign_next_tasks(self) -> List[Dict[str, Any]]:
        """Assign tasks from global queue to available agents"""
        # Build global queue
        self.build_global_queue()
        
        # Get agent pool
        agents = self.get_agent_pool()
        
        assignments = []
        assigned_tasks = set()
        
        # Track agent workload
        agent_workloads = {agent_id: 0 for agent_id in agents}
        
        # Process tasks in priority order
        for global_task in self.global_task_queue:
            if global_task.task.task_id in assigned_tasks:
                continue
            
            # Check dependencies
            if not self._are_dependencies_met(global_task):
                continue
            
            # Find best available agent
            best_agent = None
            best_score = 0.0
            
            for agent_id, agent in agents.items():
                # In global mode, any agent can work on any project
                if self.pool_mode == PoolMode.PROJECT_DEDICATED:
                    # Check if agent belongs to the right project
                    if self.agent_assignments.get(agent_id) != global_task.project_id:
                        continue
                
                # Check agent availability (workload)
                if agent_workloads[agent_id] >= 3:  # Max 3 concurrent tasks
                    continue
                
                # Calculate assignment score
                score = agent.calculate_assignment_score(global_task.task)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            # Assign if we found a suitable agent
            if best_agent and best_score > 0.3:
                assignment = {
                    'task_id': global_task.task.task_id,
                    'agent_id': best_agent.agent_id,
                    'project_id': global_task.project_id,
                    'project_name': global_task.project_name,
                    'task_title': global_task.task.title,
                    'task_type': global_task.task.task_type.value,
                    'priority': global_task.task.priority.value,
                    'global_score': global_task.global_score,
                    'assignment_score': best_score,
                    'assigned_at': datetime.now(timezone.utc).isoformat()
                }
                
                assignments.append(assignment)
                assigned_tasks.add(global_task.task.task_id)
                agent_workloads[best_agent.agent_id] += 1
                
                # Update agent assignment tracking
                if self.pool_mode == PoolMode.GLOBAL_PRIORITY:
                    self.agent_assignments[best_agent.agent_id] = global_task.project_id
                
                logger.info(f"Assigned {global_task.task.title} from {global_task.project_name} "
                          f"to {best_agent.agent_id} (score: {best_score:.2f})")
        
        # Save assignments
        self._save_assignments(assignments)
        
        return assignments
    
    def _are_dependencies_met(self, global_task: GlobalTask) -> bool:
        """Check if task dependencies are met"""
        if not global_task.task.dependencies:
            return True
        
        # Load project tasks to check dependency status
        workspace = self.project_manager.get_project_workspace(global_task.project_id)
        if not workspace:
            return False
        
        task_file = workspace / "task_assignments" / "task_queue.json"
        if not task_file.exists():
            return False
        
        try:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            tasks = {t['task_id']: t for t in task_data.get('tasks', [])}
            
            for dep_id in global_task.task.dependencies:
                if dep_id not in tasks:
                    continue
                dep_task = tasks[dep_id]
                if dep_task.get('status') != 'completed':
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _save_assignments(self, assignments: List[Dict]):
        """Save global assignments"""
        assignments_file = Path("coordination_system/global_assignments.json")
        
        # Load existing or create new
        existing = []
        if assignments_file.exists():
            try:
                with open(assignments_file, 'r') as f:
                    data = json.load(f)
                existing = data.get('history', [])
            except:
                pass
        
        # Append new assignments
        existing.extend(assignments)
        
        # Save
        assignments_file.parent.mkdir(exist_ok=True)
        with open(assignments_file, 'w') as f:
            json.dump({
                'mode': self.pool_mode.value,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'active_assignments': assignments,
                'history': existing[-1000:]  # Keep last 1000 assignments
            }, f, indent=2)
    
    def get_project_queue_position(self, project_id: str) -> Dict[str, Any]:
        """Get information about where a project's tasks are in the global queue"""
        self.build_global_queue()
        
        project_tasks = [gt for gt in self.global_task_queue if gt.project_id == project_id]
        
        if not project_tasks:
            return {
                'project_id': project_id,
                'total_tasks': 0,
                'highest_position': None,
                'average_position': None
            }
        
        positions = []
        for i, gt in enumerate(self.global_task_queue):
            if gt.project_id == project_id:
                positions.append(i + 1)
        
        return {
            'project_id': project_id,
            'total_tasks': len(project_tasks),
            'highest_position': min(positions) if positions else None,
            'average_position': sum(positions) / len(positions) if positions else None,
            'task_positions': positions[:10]  # First 10 positions
        }
    
    def get_global_queue_summary(self) -> Dict[str, Any]:
        """Get summary of global task queue"""
        self.build_global_queue()
        
        # Group by project
        by_project = {}
        by_priority = {p.value: 0 for p in TaskPriority}
        
        for gt in self.global_task_queue:
            # By project
            if gt.project_id not in by_project:
                by_project[gt.project_id] = {
                    'name': gt.project_name,
                    'count': 0,
                    'priorities': {p.value: 0 for p in TaskPriority}
                }
            by_project[gt.project_id]['count'] += 1
            by_project[gt.project_id]['priorities'][gt.task.priority.value] += 1
            
            # By priority
            by_priority[gt.task.priority.value] += 1
        
        return {
            'total_tasks': len(self.global_task_queue),
            'mode': self.pool_mode.value,
            'by_project': by_project,
            'by_priority': by_priority,
            'top_10_tasks': [
                {
                    'project': gt.project_name,
                    'title': gt.task.title,
                    'priority': gt.task.priority.value,
                    'score': gt.global_score
                }
                for gt in self.global_task_queue[:10]
            ]
        }

def main():
    """CLI interface for global task pool"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Global Task Pool Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Set mode
    mode_parser = subparsers.add_parser('mode', help='Set pool mode')
    mode_parser.add_argument('mode', choices=['global_priority', 'project_dedicated', 'hybrid'])
    
    # Set project priority
    priority_parser = subparsers.add_parser('priority', help='Set project priority')
    priority_parser.add_argument('project', help='Project ID or name')
    priority_parser.add_argument('priority', type=float, help='Priority multiplier (0.1-2.0)')
    
    # Show queue
    queue_parser = subparsers.add_parser('queue', help='Show global task queue')
    queue_parser.add_argument('--project', help='Filter by project')
    
    # Process assignments
    assign_parser = subparsers.add_parser('assign', help='Process task assignments')
    
    # Summary
    summary_parser = subparsers.add_parser('summary', help='Show queue summary')
    
    args = parser.parse_args()
    
    # Initialize managers
    project_manager = ProjectManager()
    pool_manager = GlobalTaskPoolManager(project_manager)
    
    if args.command == 'mode':
        pool_manager.set_pool_mode(PoolMode(args.mode))
        print(f"Set pool mode to: {args.mode}")
        
    elif args.command == 'priority':
        # Find project
        project = project_manager.get_project(args.project)
        if not project:
            project = project_manager.get_project_by_name(args.project)
        
        if project:
            pool_manager.set_project_priority(project.project_id, args.priority)
            print(f"Set priority for {project.name} to {args.priority}")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'queue':
        if args.project:
            # Show project position
            project = project_manager.get_project(args.project)
            if not project:
                project = project_manager.get_project_by_name(args.project)
            
            if project:
                info = pool_manager.get_project_queue_position(project.project_id)
                print(f"Project: {project.name}")
                print(f"Total tasks in queue: {info['total_tasks']}")
                if info['highest_position']:
                    print(f"Highest position: #{info['highest_position']}")
                    print(f"Average position: #{info['average_position']:.1f}")
            else:
                print(f"Project not found: {args.project}")
        else:
            # Show full queue
            queue = pool_manager.build_global_queue()
            print(f"Global Task Queue ({len(queue)} tasks):")
            print(f"{'Pos':<4} {'Project':<20} {'Task':<40} {'Priority':<10} {'Score':<8}")
            print("-" * 90)
            for i, gt in enumerate(queue[:20]):  # Show top 20
                print(f"{i+1:<4} {gt.project_name[:20]:<20} {gt.task.title[:40]:<40} "
                      f"{gt.task.priority.value:<10} {gt.global_score:<8.1f}")
    
    elif args.command == 'assign':
        assignments = pool_manager.assign_next_tasks()
        print(f"Made {len(assignments)} task assignments:")
        for assign in assignments:
            print(f"  {assign['project_name']}: {assign['task_title']} -> {assign['agent_id']}")
    
    elif args.command == 'summary':
        summary = pool_manager.get_global_queue_summary()
        print(f"Global Task Pool Summary")
        print(f"Mode: {summary['mode']}")
        print(f"Total tasks: {summary['total_tasks']}")
        print(f"\nBy Priority:")
        for priority, count in summary['by_priority'].items():
            print(f"  {priority}: {count}")
        print(f"\nBy Project:")
        for project_id, info in summary['by_project'].items():
            print(f"  {info['name']}: {info['count']} tasks")

if __name__ == '__main__':
    main()