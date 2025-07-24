#!/usr/bin/env python3
"""
Work Tracking System for Agent Performance Analytics
Tracks agent productivity, task completion, and performance metrics
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task completion statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class PerformanceMetric(Enum):
    """Performance metrics to track."""
    TASKS_COMPLETED = "tasks_completed"
    AVERAGE_COMPLETION_TIME = "average_completion_time"
    SUCCESS_RATE = "success_rate"
    COLLABORATION_SCORE = "collaboration_score"
    AVAILABILITY_PERCENTAGE = "availability_percentage"
    EXPERTISE_UTILIZATION = "expertise_utilization"

@dataclass
class TaskRecord:
    """Individual task record for tracking."""
    task_id: str
    agent_id: str
    title: str
    description: str
    domain: str
    authority_type: str
    assigned_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    complexity_score: Optional[int] = None  # 1-10 scale
    dependencies: List[str] = None
    collaborators: List[str] = None
    blockers: List[str] = None
    quality_score: Optional[int] = None  # 1-10 scale
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.collaborators is None:
            self.collaborators = []
        if self.blockers is None:
            self.blockers = []

@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for an agent."""
    agent_id: str
    period_start: str
    period_end: str
    total_tasks: int = 0
    completed_tasks: int = 0
    average_completion_time_hours: Optional[float] = None
    success_rate: Optional[float] = None
    collaboration_count: int = 0
    expertise_domains: List[str] = None
    availability_score: Optional[float] = None
    productivity_score: Optional[float] = None
    quality_average: Optional[float] = None
    
    def __post_init__(self):
        if self.expertise_domains is None:
            self.expertise_domains = []

class WorkTrackingSystem:
    """Comprehensive work tracking and performance analytics system."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.tasks_db_file = self.project_root / "work_tracking_tasks.json"
        self.metrics_db_file = self.project_root / "work_tracking_metrics.json"
        self.performance_reports_dir = self.project_root / "performance_reports"
        
        # Create directories
        self.performance_reports_dir.mkdir(exist_ok=True)
        
        # Initialize databases
        self.tasks_db = self._load_tasks_db()
        self.metrics_db = self._load_metrics_db()
        
        # Import authority manager for integration
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError as e:
            logger.warning(f"Authority manager not available: {e}")
            self.authority_manager = None
    
    def _load_tasks_db(self) -> Dict:
        """Load tasks database."""
        if self.tasks_db_file.exists():
            with open(self.tasks_db_file, 'r') as f:
                return json.load(f)
        return {"tasks": {}, "version": "1.0"}
    
    def _save_tasks_db(self):
        """Save tasks database."""
        with open(self.tasks_db_file, 'w') as f:
            json.dump(self.tasks_db, f, indent=2)
    
    def _load_metrics_db(self) -> Dict:
        """Load metrics database."""
        if self.metrics_db_file.exists():
            with open(self.metrics_db_file, 'r') as f:
                return json.load(f)
        return {"agent_metrics": {}, "team_metrics": {}, "version": "1.0"}
    
    def _save_metrics_db(self):
        """Save metrics database."""
        with open(self.metrics_db_file, 'w') as f:
            json.dump(self.metrics_db, f, indent=2)
    
    def create_task(
        self,
        agent_id: str,
        title: str,
        description: str,
        domain: str,
        authority_type: str = "task",
        estimated_hours: Optional[float] = None,
        complexity_score: Optional[int] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Create a new task record."""
        
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{agent_id}"
        
        task = TaskRecord(
            task_id=task_id,
            agent_id=agent_id,
            title=title,
            description=description,
            domain=domain,
            authority_type=authority_type,
            assigned_at=datetime.now().isoformat(),
            estimated_hours=estimated_hours,
            complexity_score=complexity_score,
            dependencies=dependencies or []
        )
        
        # Save to database
        self.tasks_db["tasks"][task_id] = asdict(task)
        self._save_tasks_db()
        
        logger.info(f"Created task {task_id} for agent {agent_id}: {title}")
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Mark a task as started."""
        if task_id in self.tasks_db["tasks"]:
            task = self.tasks_db["tasks"][task_id]
            task["status"] = TaskStatus.IN_PROGRESS.value
            task["started_at"] = datetime.now().isoformat()
            
            self._save_tasks_db()
            logger.info(f"Task {task_id} started by {task['agent_id']}")
            return True
        return False
    
    def complete_task(
        self,
        task_id: str,
        actual_hours: Optional[float] = None,
        quality_score: Optional[int] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Mark a task as completed."""
        if task_id in self.tasks_db["tasks"]:
            task = self.tasks_db["tasks"][task_id]
            task["status"] = TaskStatus.COMPLETED.value
            task["completed_at"] = datetime.now().isoformat()
            
            if actual_hours is not None:
                task["actual_hours"] = actual_hours
            
            if quality_score is not None:
                task["quality_score"] = quality_score
            
            if notes:
                task["completion_notes"] = notes
            
            # Calculate actual time if started
            if task.get("started_at") and not actual_hours:
                start_time = datetime.fromisoformat(task["started_at"])
                end_time = datetime.now()
                calculated_hours = (end_time - start_time).total_seconds() / 3600
                task["actual_hours"] = round(calculated_hours, 2)
            
            self._save_tasks_db()
            logger.info(f"Task {task_id} completed by {task['agent_id']}")
            
            # Update performance metrics
            self._update_agent_metrics(task["agent_id"])
            return True
        return False
    
    def add_task_blocker(self, task_id: str, blocker_description: str) -> bool:
        """Add a blocker to a task."""
        if task_id in self.tasks_db["tasks"]:
            task = self.tasks_db["tasks"][task_id]
            task["status"] = TaskStatus.BLOCKED.value
            task["blockers"].append({
                "description": blocker_description,
                "added_at": datetime.now().isoformat(),
                "resolved": False
            })
            
            self._save_tasks_db()
            logger.warning(f"Task {task_id} blocked: {blocker_description}")
            return True
        return False
    
    def resolve_task_blocker(self, task_id: str, blocker_description: str) -> bool:
        """Resolve a task blocker."""
        if task_id in self.tasks_db["tasks"]:
            task = self.tasks_db["tasks"][task_id]
            
            for blocker in task["blockers"]:
                if blocker["description"] == blocker_description and not blocker["resolved"]:
                    blocker["resolved"] = True
                    blocker["resolved_at"] = datetime.now().isoformat()
                    
                    # Check if all blockers are resolved
                    if all(b["resolved"] for b in task["blockers"]):
                        task["status"] = TaskStatus.IN_PROGRESS.value
                    
                    self._save_tasks_db()
                    logger.info(f"Task {task_id} blocker resolved: {blocker_description}")
                    return True
        return False
    
    def add_collaborator(self, task_id: str, collaborator_agent: str) -> bool:
        """Add a collaborator to a task."""
        if task_id in self.tasks_db["tasks"]:
            task = self.tasks_db["tasks"][task_id]
            if collaborator_agent not in task["collaborators"]:
                task["collaborators"].append(collaborator_agent)
                self._save_tasks_db()
                logger.info(f"Added collaborator {collaborator_agent} to task {task_id}")
                return True
        return False
    
    def _update_agent_metrics(self, agent_id: str):
        """Update performance metrics for an agent."""
        
        # Get all tasks for this agent
        agent_tasks = [
            task for task in self.tasks_db["tasks"].values()
            if task["agent_id"] == agent_id
        ]
        
        if not agent_tasks:
            return
        
        # Calculate metrics for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_tasks = [
            task for task in agent_tasks
            if datetime.fromisoformat(task["assigned_at"]) > thirty_days_ago
        ]
        
        completed_tasks = [
            task for task in recent_tasks
            if task["status"] == TaskStatus.COMPLETED.value
        ]
        
        metrics = AgentPerformanceMetrics(
            agent_id=agent_id,
            period_start=(datetime.now() - timedelta(days=30)).isoformat(),
            period_end=datetime.now().isoformat(),
            total_tasks=len(recent_tasks),
            completed_tasks=len(completed_tasks)
        )
        
        # Calculate success rate
        if recent_tasks:
            metrics.success_rate = len(completed_tasks) / len(recent_tasks) * 100
        
        # Calculate average completion time
        completion_times = []
        for task in completed_tasks:
            if task.get("actual_hours"):
                completion_times.append(task["actual_hours"])
        
        if completion_times:
            metrics.average_completion_time_hours = statistics.mean(completion_times)
        
        # Calculate collaboration score
        collaboration_count = sum(len(task.get("collaborators", [])) for task in recent_tasks)
        metrics.collaboration_count = collaboration_count
        
        # Calculate quality average
        quality_scores = [
            task["quality_score"] for task in completed_tasks
            if task.get("quality_score") is not None
        ]
        if quality_scores:
            metrics.quality_average = statistics.mean(quality_scores)
        
        # Calculate expertise domains
        domains = list(set(task["domain"] for task in recent_tasks))
        metrics.expertise_domains = domains
        
        # Calculate productivity score (weighted combination of metrics)
        productivity_factors = []
        
        if metrics.success_rate is not None:
            productivity_factors.append(metrics.success_rate / 100 * 0.4)  # 40% weight
        
        if metrics.average_completion_time_hours is not None and metrics.average_completion_time_hours > 0:
            # Inverse of completion time (faster = better)
            time_score = min(1.0, 10 / metrics.average_completion_time_hours)
            productivity_factors.append(time_score * 0.3)  # 30% weight
        
        if metrics.quality_average is not None:
            productivity_factors.append(metrics.quality_average / 10 * 0.3)  # 30% weight
        
        if productivity_factors:
            metrics.productivity_score = statistics.mean(productivity_factors) * 100
        
        # Save metrics
        if "agent_metrics" not in self.metrics_db:
            self.metrics_db["agent_metrics"] = {}
        
        self.metrics_db["agent_metrics"][agent_id] = asdict(metrics)
        self._save_metrics_db()
        
        logger.info(f"Updated performance metrics for agent {agent_id}")
    
    def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformanceMetrics]:
        """Get performance metrics for an agent."""
        if agent_id in self.metrics_db.get("agent_metrics", {}):
            metrics_data = self.metrics_db["agent_metrics"][agent_id]
            return AgentPerformanceMetrics(**metrics_data)
        return None
    
    def get_task_details(self, task_id: str) -> Optional[TaskRecord]:
        """Get details for a specific task."""
        if task_id in self.tasks_db["tasks"]:
            task_data = self.tasks_db["tasks"][task_id]
            return TaskRecord(**task_data)
        return None
    
    def get_agent_tasks(
        self,
        agent_id: str,
        status_filter: Optional[TaskStatus] = None,
        days_back: Optional[int] = None
    ) -> List[TaskRecord]:
        """Get tasks for an agent with optional filtering."""
        
        agent_tasks = [
            TaskRecord(**task_data)
            for task_data in self.tasks_db["tasks"].values()
            if task_data["agent_id"] == agent_id
        ]
        
        # Filter by status
        if status_filter:
            agent_tasks = [task for task in agent_tasks if task.status == status_filter.value]
        
        # Filter by date
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            agent_tasks = [
                task for task in agent_tasks
                if datetime.fromisoformat(task.assigned_at) > cutoff_date
            ]
        
        return sorted(agent_tasks, key=lambda t: t.assigned_at, reverse=True)
    
    def generate_performance_report(self, agent_id: str) -> Dict:
        """Generate a comprehensive performance report for an agent."""
        
        metrics = self.get_agent_performance(agent_id)
        recent_tasks = self.get_agent_tasks(agent_id, days_back=30)
        
        if not metrics:
            return {"error": f"No metrics found for agent {agent_id}"}
        
        # Task breakdown by status
        task_breakdown = {}
        for status in TaskStatus:
            task_breakdown[status.value] = len([
                task for task in recent_tasks if task.status == status.value
            ])
        
        # Domain expertise analysis
        domain_tasks = {}
        for task in recent_tasks:
            if task.domain not in domain_tasks:
                domain_tasks[task.domain] = {"total": 0, "completed": 0}
            domain_tasks[task.domain]["total"] += 1
            if task.status == TaskStatus.COMPLETED.value:
                domain_tasks[task.domain]["completed"] += 1
        
        # Calculate domain success rates
        domain_success_rates = {}
        for domain, counts in domain_tasks.items():
            if counts["total"] > 0:
                domain_success_rates[domain] = (counts["completed"] / counts["total"]) * 100
        
        # Collaboration analysis
        collaborations = {}
        for task in recent_tasks:
            for collaborator in task.collaborators:
                if collaborator not in collaborations:
                    collaborations[collaborator] = 0
                collaborations[collaborator] += 1
        
        report = {
            "agent_id": agent_id,
            "report_generated_at": datetime.now().isoformat(),
            "period": {
                "start": metrics.period_start,
                "end": metrics.period_end
            },
            "summary_metrics": asdict(metrics),
            "task_breakdown": task_breakdown,
            "domain_expertise": {
                "domains": list(domain_tasks.keys()),
                "success_rates": domain_success_rates,
                "primary_domain": max(domain_success_rates.items(), key=lambda x: x[1])[0] if domain_success_rates else None
            },
            "collaboration_analysis": {
                "frequent_collaborators": dict(sorted(collaborations.items(), key=lambda x: x[1], reverse=True)[:5]),
                "total_collaborative_tasks": len([t for t in recent_tasks if t.collaborators])
            },
            "recommendations": self._generate_recommendations(metrics, recent_tasks)
        }
        
        # Save report
        report_file = self.performance_reports_dir / f"{agent_id}_performance_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated performance report for {agent_id}: {report_file}")
        return report
    
    def _generate_recommendations(self, metrics: AgentPerformanceMetrics, tasks: List[TaskRecord]) -> List[str]:
        """Generate performance improvement recommendations."""
        
        recommendations = []
        
        # Success rate recommendations
        if metrics.success_rate is not None and metrics.success_rate < 80:
            recommendations.append("Consider breaking down complex tasks into smaller, manageable pieces")
        
        # Completion time recommendations
        if metrics.average_completion_time_hours is not None and metrics.average_completion_time_hours > 20:
            recommendations.append("Focus on time management and task prioritization techniques")
        
        # Quality recommendations
        if metrics.quality_average is not None and metrics.quality_average < 7:
            recommendations.append("Implement additional quality checks and peer reviews")
        
        # Collaboration recommendations
        if metrics.collaboration_count == 0:
            recommendations.append("Seek opportunities for collaboration and knowledge sharing")
        elif metrics.collaboration_count > len(tasks) * 0.8:
            recommendations.append("Balance collaborative work with independent task completion")
        
        # Domain expertise recommendations
        if len(metrics.expertise_domains) == 1:
            recommendations.append("Consider expanding expertise to additional domains")
        elif len(metrics.expertise_domains) > 5:
            recommendations.append("Focus on specializing in 2-3 core domains for deeper expertise")
        
        return recommendations


def demonstrate_work_tracking():
    """Demonstrate the work tracking system."""
    
    logger.info("📊 Starting Work Tracking System Demonstration")
    
    tracker = WorkTrackingSystem()
    
    # Create sample tasks for multiple agents
    agents = ["shark", "dolphin", "whale", "octopus"]
    
    sample_tasks = [
        ("shark", "Implement OAuth2 Authentication", "Build secure authentication system", "security", 8, 7),
        ("shark", "Security Audit of API Endpoints", "Review all API endpoints for vulnerabilities", "security", 12, 8),
        ("dolphin", "Redesign User Interface", "Update UI for better accessibility", "frontend", 16, 6),
        ("dolphin", "Mobile App Optimization", "Optimize mobile app performance", "frontend", 10, 5),
        ("whale", "Database Migration", "Migrate to new database schema", "data", 20, 9),
        ("whale", "Backup System Implementation", "Implement automated backup system", "infrastructure", 15, 8),
        ("octopus", "API Performance Testing", "Load test all API endpoints", "quality", 12, 7),
        ("octopus", "Test Automation Framework", "Build comprehensive test suite", "quality", 25, 9)
    ]
    
    created_tasks = []
    
    print("\n" + "="*60)
    print("📝 CREATING SAMPLE TASKS")
    print("="*60)
    
    for agent, title, desc, domain, hours, complexity in sample_tasks:
        task_id = tracker.create_task(
            agent_id=agent,
            title=title,
            description=desc,
            domain=domain,
            estimated_hours=hours,
            complexity_score=complexity
        )
        created_tasks.append(task_id)
        print(f"✅ {agent}: {title}")
    
    print(f"\nCreated {len(created_tasks)} tasks")
    
    # Simulate task progression
    print("\n" + "="*60)
    print("⚡ SIMULATING TASK PROGRESSION")
    print("="*60)
    
    import random
    
    for i, task_id in enumerate(created_tasks[:6]):  # Complete first 6 tasks
        # Start task
        tracker.start_task(task_id)
        print(f"▶️  Started task {i+1}")
        
        # Add some blockers and collaborations
        if random.random() < 0.3:  # 30% chance of blocker
            tracker.add_task_blocker(task_id, "Waiting for API documentation")
            tracker.resolve_task_blocker(task_id, "Waiting for API documentation")
        
        if random.random() < 0.4:  # 40% chance of collaboration
            collaborator = random.choice([a for a in agents if a != tracker.get_task_details(task_id).agent_id])
            tracker.add_collaborator(task_id, collaborator)
        
        # Complete task
        actual_hours = random.uniform(5, 20)
        quality_score = random.randint(6, 10)
        tracker.complete_task(task_id, actual_hours, quality_score)
        print(f"✅ Completed task {i+1}")
    
    # Generate performance reports
    print("\n" + "="*60)
    print("📊 GENERATING PERFORMANCE REPORTS")
    print("="*60)
    
    for agent in agents:
        report = tracker.generate_performance_report(agent)
        
        if "error" not in report:
            metrics = report["summary_metrics"]
            print(f"\n🤖 Agent {agent.upper()}:")
            print(f"   Tasks: {metrics['completed_tasks']}/{metrics['total_tasks']}")
            print(f"   Success Rate: {metrics['success_rate']:.1f}%" if metrics['success_rate'] else "   Success Rate: N/A")
            print(f"   Avg Time: {metrics['average_completion_time_hours']:.1f}h" if metrics['average_completion_time_hours'] else "   Avg Time: N/A")
            print(f"   Quality: {metrics['quality_average']:.1f}/10" if metrics['quality_average'] else "   Quality: N/A")
            print(f"   Productivity: {metrics['productivity_score']:.1f}%" if metrics['productivity_score'] else "   Productivity: N/A")
            
            if report["recommendations"]:
                print(f"   💡 Top Recommendation: {report['recommendations'][0]}")
        else:
            print(f"❌ {agent}: {report['error']}")
    
    logger.info("📈 Work Tracking System demonstration completed")


if __name__ == "__main__":
    demonstrate_work_tracking()