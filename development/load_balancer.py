#!/usr/bin/env python3
"""
Load Balancing System for Multi-Agent Coordination
Distributes tasks and workload efficiently across agents
"""

import json
import time
import math
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"           # Distribute evenly in rotation
    LEAST_CONNECTIONS = "least_connections" # Assign to agent with fewest active tasks
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin" # Consider agent capacity weights
    RESOURCE_AWARE = "resource_aware"     # Consider CPU/memory usage
    EXPERTISE_BASED = "expertise_based"   # Route based on domain expertise
    ADAPTIVE = "adaptive"                 # Dynamically adjust strategy
    PRIORITY_QUEUE = "priority_queue"     # Handle high-priority tasks first

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class AgentCapacity:
    """Agent capacity and resource information."""
    agent_id: str
    max_concurrent_tasks: int
    current_task_count: int
    cpu_usage_percent: float
    memory_usage_percent: float
    expertise_domains: List[str]
    capacity_weight: float
    availability_score: float
    last_task_assigned: Optional[str]

@dataclass
class TaskRequest:
    """Task assignment request."""
    task_id: str
    title: str
    description: str
    domain: str
    priority: int
    estimated_duration_minutes: int
    required_expertise_level: str
    deadline: Optional[str]
    dependencies: List[str]
    resource_requirements: Dict[str, float]
    metadata: Dict

@dataclass
class LoadBalancingMetrics:
    """Load balancing performance metrics."""
    timestamp: str
    strategy_used: str
    total_agents: int
    active_agents: int
    total_tasks_assigned: int
    average_load_percent: float
    load_distribution_stddev: float
    task_queue_size: int
    assignment_latency_ms: float

class LoadBalancer:
    """Intelligent load balancing system for multi-agent coordination."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.load_balancer_config_file = self.project_root / "load_balancer_config.json"
        self.agent_capacity_file = self.project_root / "agent_capacities.json"
        self.load_metrics_file = self.project_root / "load_balancing_metrics.json"
        
        # Load balancing state
        self.config = self._load_config()
        self.agent_capacities = self._load_agent_capacities()
        self.metrics_history = []
        
        # Task queue management
        self.task_queues = {
            TaskPriority.EMERGENCY: deque(),
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.MEDIUM: deque(),
            TaskPriority.LOW: deque()
        }
        
        # Round-robin state
        self.round_robin_index = 0
        
        # Adaptive strategy state
        self.strategy_performance = defaultdict(list)
        self.current_strategy = LoadBalancingStrategy.ADAPTIVE
        
        # Load monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Import related systems
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        
        try:
            from domain_specific_agent_roles import DomainSpecificRoleManager
            self.role_manager = DomainSpecificRoleManager(project_root)
        except ImportError:
            self.role_manager = None
            logger.warning("Role manager not available")
        
        try:
            from work_tracking_system import WorkTrackingSystem
            self.work_tracker = WorkTrackingSystem(project_root)
        except ImportError:
            self.work_tracker = None
            logger.warning("Work tracker not available")
        
        self._initialize_default_capacities()
        
        logger.info("⚖️ Load balancer initialized")
    
    def _load_config(self) -> Dict:
        """Load load balancer configuration."""
        if self.load_balancer_config_file.exists():
            with open(self.load_balancer_config_file, 'r') as f:
                return json.load(f)
        
        return {
            "default_strategy": LoadBalancingStrategy.ADAPTIVE.value,
            "max_queue_size": 1000,
            "assignment_timeout_seconds": 30,
            "load_threshold_percent": 80,
            "rebalancing_interval_minutes": 5,
            "adaptive_strategy_window_minutes": 15,
            "resource_monitoring_enabled": True
        }
    
    def _save_config(self):
        """Save load balancer configuration."""
        with open(self.load_balancer_config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_agent_capacities(self) -> Dict[str, AgentCapacity]:
        """Load agent capacity information."""
        if self.agent_capacity_file.exists():
            with open(self.agent_capacity_file, 'r') as f:
                data = json.load(f)
                return {
                    agent_id: AgentCapacity(**agent_data) 
                    for agent_id, agent_data in data.items()
                }
        return {}
    
    def _save_agent_capacities(self):
        """Save agent capacity information."""
        data = {
            agent_id: asdict(capacity) 
            for agent_id, capacity in self.agent_capacities.items()
        }
        with open(self.agent_capacity_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_default_capacities(self):
        """Initialize default agent capacities."""
        
        if not self.agent_capacities:
            default_agents = [
                ("shark", ["security", "backend"], 8),
                ("dolphin", ["frontend", "ui"], 6),
                ("whale", ["infrastructure", "deployment"], 10),
                ("octopus", ["data", "analytics"], 7),
                ("jellyfish", ["quality", "testing"], 5),
                ("seahorse", ["backend", "api"], 9)
            ]
            
            for agent_id, domains, capacity in default_agents:
                self.agent_capacities[agent_id] = AgentCapacity(
                    agent_id=agent_id,
                    max_concurrent_tasks=capacity,
                    current_task_count=0,
                    cpu_usage_percent=0.0,
                    memory_usage_percent=0.0,
                    expertise_domains=domains,
                    capacity_weight=1.0,
                    availability_score=1.0,
                    last_task_assigned=None
                )
            
            self._save_agent_capacities()
            logger.info("Initialized default agent capacities")
    
    def start_monitoring(self):
        """Start load monitoring and automatic rebalancing."""
        
        if self.monitoring_active:
            logger.warning("Load monitoring already active")
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self._update_agent_loads()
                    self._process_task_queues()
                    self._collect_load_metrics()
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"Error in load monitoring loop: {e}")
        
        self.monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("📊 Started load monitoring")
    
    def stop_monitoring(self):
        """Stop load monitoring."""
        
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("📊 Stopped load monitoring")
    
    def assign_task(self, task_request: TaskRequest, strategy: Optional[LoadBalancingStrategy] = None) -> Optional[str]:
        """Assign a task to the most appropriate agent."""
        
        start_time = time.perf_counter()
        
        if strategy is None:
            strategy = self._select_strategy()
        
        # Add task to appropriate priority queue if no agents available
        priority = TaskPriority(task_request.priority)
        
        # Try immediate assignment
        assigned_agent = self._assign_task_immediate(task_request, strategy)
        
        if assigned_agent:
            # Update agent capacity
            self.agent_capacities[assigned_agent].current_task_count += 1
            self.agent_capacities[assigned_agent].last_task_assigned = task_request.task_id
            self._save_agent_capacities()
            
            # Record metrics
            assignment_time = (time.perf_counter() - start_time) * 1000
            self._record_assignment_metrics(strategy, assignment_time, len(self.task_queues[priority]))
            
            logger.info(f"⚖️ Assigned task {task_request.task_id} to {assigned_agent} ({strategy.value})")
            return assigned_agent
        
        else:
            # Queue task for later assignment
            self.task_queues[priority].append(task_request)
            logger.warning(f"⏳ Queued task {task_request.task_id} (priority: {priority.name})")
            return None
    
    def _assign_task_immediate(self, task_request: TaskRequest, strategy: LoadBalancingStrategy) -> Optional[str]:
        """Attempt immediate task assignment using specified strategy."""
        
        available_agents = self._get_available_agents(task_request)
        
        if not available_agents:
            return None
        
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_assignment(available_agents)
        
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_assignment(available_agents)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_assignment(available_agents)
        
        elif strategy == LoadBalancingStrategy.RESOURCE_AWARE:
            return self._resource_aware_assignment(available_agents)
        
        elif strategy == LoadBalancingStrategy.EXPERTISE_BASED:
            return self._expertise_based_assignment(available_agents, task_request)
        
        elif strategy == LoadBalancingStrategy.PRIORITY_QUEUE:
            return self._priority_queue_assignment(available_agents, task_request)
        
        elif strategy == LoadBalancingStrategy.ADAPTIVE:
            # Use the currently best-performing strategy
            best_strategy = self._get_best_performing_strategy()
            # Avoid recursion by checking if best strategy is also adaptive
            if best_strategy == LoadBalancingStrategy.ADAPTIVE:
                best_strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
            return self._assign_task_immediate(task_request, best_strategy)
        
        else:
            # Fallback to round robin
            return self._round_robin_assignment(available_agents)
    
    def _get_available_agents(self, task_request: TaskRequest) -> List[str]:
        """Get list of agents available for task assignment."""
        
        available = []
        
        for agent_id, capacity in self.agent_capacities.items():
            # Check if agent has capacity
            if capacity.current_task_count >= capacity.max_concurrent_tasks:
                continue
            
            # Check if agent has required expertise
            if task_request.domain and task_request.domain not in capacity.expertise_domains:
                continue
            
            # Check resource requirements
            resource_reqs = task_request.resource_requirements
            if resource_reqs.get("cpu", 0) > 0 and capacity.cpu_usage_percent > 90:
                continue
            if resource_reqs.get("memory", 0) > 0 and capacity.memory_usage_percent > 90:
                continue
            
            # Check availability score
            if capacity.availability_score < 0.5:
                continue
            
            available.append(agent_id)
        
        return available
    
    def _round_robin_assignment(self, available_agents: List[str]) -> str:
        """Round-robin task assignment."""
        
        if not available_agents:
            return None
        
        # Find next agent in rotation
        for _ in range(len(available_agents)):
            candidate = available_agents[self.round_robin_index % len(available_agents)]
            self.round_robin_index = (self.round_robin_index + 1) % len(available_agents)
            
            if candidate in available_agents:
                return candidate
        
        return available_agents[0]
    
    def _least_connections_assignment(self, available_agents: List[str]) -> str:
        """Assign to agent with fewest active tasks."""
        
        min_tasks = float('inf')
        best_agent = None
        
        for agent_id in available_agents:
            capacity = self.agent_capacities[agent_id]
            if capacity.current_task_count < min_tasks:
                min_tasks = capacity.current_task_count
                best_agent = agent_id
        
        return best_agent
    
    def _weighted_round_robin_assignment(self, available_agents: List[str]) -> str:
        """Weighted round-robin based on agent capacity."""
        
        # Calculate weights based on remaining capacity
        weights = []
        for agent_id in available_agents:
            capacity = self.agent_capacities[agent_id]
            remaining_capacity = capacity.max_concurrent_tasks - capacity.current_task_count
            weight = remaining_capacity * capacity.capacity_weight
            weights.append(weight)
        
        # Select agent probabilistically based on weights
        total_weight = sum(weights)
        if total_weight == 0:
            return available_agents[0]
        
        import random
        target = random.uniform(0, total_weight)
        current_weight = 0
        
        for i, weight in enumerate(weights):
            current_weight += weight
            if current_weight >= target:
                return available_agents[i]
        
        return available_agents[-1]
    
    def _resource_aware_assignment(self, available_agents: List[str]) -> str:
        """Assign based on current resource usage."""
        
        best_agent = None
        best_score = float('inf')
        
        for agent_id in available_agents:
            capacity = self.agent_capacities[agent_id]
            
            # Calculate resource pressure score (lower is better)
            cpu_pressure = capacity.cpu_usage_percent / 100.0
            memory_pressure = capacity.memory_usage_percent / 100.0
            task_pressure = capacity.current_task_count / capacity.max_concurrent_tasks
            
            score = (cpu_pressure + memory_pressure + task_pressure) / 3.0
            
            if score < best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    def _expertise_based_assignment(self, available_agents: List[str], task_request: TaskRequest) -> str:
        """Assign based on expertise match."""
        
        if not task_request.domain:
            return self._least_connections_assignment(available_agents)
        
        # Score agents by expertise level
        expertise_scores = {}
        
        for agent_id in available_agents:
            if self.role_manager:
                try:
                    expertise = self.role_manager.get_agent_expertise_summary(agent_id)
                    agent_expertise = expertise.get("expertise", {})
                    
                    if task_request.domain in agent_expertise:
                        level = agent_expertise[task_request.domain]["level"]
                        level_scores = {
                            "novice": 1,
                            "competent": 2,
                            "proficient": 3,
                            "expert": 4,
                            "master": 5
                        }
                        expertise_scores[agent_id] = level_scores.get(level, 1)
                    else:
                        expertise_scores[agent_id] = 0
                except Exception:
                    expertise_scores[agent_id] = 1
            else:
                # Fallback: check if domain is in expertise_domains
                capacity = self.agent_capacities[agent_id]
                expertise_scores[agent_id] = 2 if task_request.domain in capacity.expertise_domains else 1
        
        # Select agent with highest expertise score
        best_agent = max(available_agents, key=lambda agent: expertise_scores.get(agent, 0))
        return best_agent
    
    def _priority_queue_assignment(self, available_agents: List[str], task_request: TaskRequest) -> str:
        """Assign considering task priority and agent suitability."""
        
        # For high-priority tasks, prefer agents with lighter loads
        if task_request.priority >= TaskPriority.HIGH.value:
            return self._least_connections_assignment(available_agents)
        else:
            return self._round_robin_assignment(available_agents)
    
    def _select_strategy(self) -> LoadBalancingStrategy:
        """Select the best load balancing strategy."""
        
        if self.current_strategy == LoadBalancingStrategy.ADAPTIVE:
            return self._get_best_performing_strategy()
        else:
            return self.current_strategy
    
    def _get_best_performing_strategy(self) -> LoadBalancingStrategy:
        """Get the currently best-performing strategy."""
        
        if not self.strategy_performance:
            return LoadBalancingStrategy.LEAST_CONNECTIONS
        
        # Calculate average assignment time for each strategy
        strategy_scores = {}
        
        for strategy, times in self.strategy_performance.items():
            if times:
                avg_time = sum(times) / len(times)
                strategy_scores[strategy] = avg_time
        
        if strategy_scores:
            best_strategy = min(strategy_scores.items(), key=lambda x: x[1])[0]
            return LoadBalancingStrategy(best_strategy)
        
        return LoadBalancingStrategy.LEAST_CONNECTIONS
    
    def _update_agent_loads(self):
        """Update agent load information."""
        
        try:
            import psutil
            
            for agent_id, capacity in self.agent_capacities.items():
                # Simulate agent resource usage (in real system would query actual agents)
                base_cpu = capacity.current_task_count * 10  # 10% CPU per task
                base_memory = capacity.current_task_count * 5  # 5% memory per task
                
                # Add some randomness
                import random
                cpu_variance = random.uniform(-5, 5)
                memory_variance = random.uniform(-3, 3)
                
                capacity.cpu_usage_percent = max(0, min(100, base_cpu + cpu_variance))
                capacity.memory_usage_percent = max(0, min(100, base_memory + memory_variance))
                
                # Update availability score
                if capacity.cpu_usage_percent > 90 or capacity.memory_usage_percent > 90:
                    capacity.availability_score = 0.3
                elif capacity.cpu_usage_percent > 70 or capacity.memory_usage_percent > 70:
                    capacity.availability_score = 0.7
                else:
                    capacity.availability_score = 1.0
            
            self._save_agent_capacities()
            
        except ImportError:
            pass  # psutil not available
    
    def _process_task_queues(self):
        """Process queued tasks and attempt assignment."""
        
        # Process queues in priority order
        for priority in [TaskPriority.EMERGENCY, TaskPriority.CRITICAL, 
                        TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]:
            
            queue = self.task_queues[priority]
            processed = []
            
            while queue:
                task_request = queue.popleft()
                assigned_agent = self._assign_task_immediate(task_request, self._select_strategy())
                
                if assigned_agent:
                    # Update agent capacity
                    self.agent_capacities[assigned_agent].current_task_count += 1
                    self.agent_capacities[assigned_agent].last_task_assigned = task_request.task_id
                    
                    logger.info(f"⚖️ Assigned queued task {task_request.task_id} to {assigned_agent}")
                else:
                    processed.append(task_request)
            
            # Re-queue unprocessed tasks
            queue.extend(processed)
    
    def _collect_load_metrics(self):
        """Collect load balancing metrics."""
        
        total_agents = len(self.agent_capacities)
        active_agents = sum(1 for c in self.agent_capacities.values() if c.current_task_count > 0)
        total_tasks = sum(c.current_task_count for c in self.agent_capacities.values())
        
        # Calculate load distribution
        loads = [c.current_task_count / c.max_concurrent_tasks 
                for c in self.agent_capacities.values()]
        avg_load = sum(loads) / len(loads) if loads else 0
        
        # Calculate standard deviation
        if loads:
            variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
            stddev = math.sqrt(variance)
        else:
            stddev = 0
        
        # Count queued tasks
        queue_size = sum(len(queue) for queue in self.task_queues.values())
        
        metrics = LoadBalancingMetrics(
            timestamp=datetime.now().isoformat(),
            strategy_used=self.current_strategy.value,
            total_agents=total_agents,
            active_agents=active_agents,
            total_tasks_assigned=total_tasks,
            average_load_percent=avg_load * 100,
            load_distribution_stddev=stddev,
            task_queue_size=queue_size,
            assignment_latency_ms=0  # Will be updated with actual measurements
        )
        
        self.metrics_history.append(asdict(metrics))
        
        # Keep only recent metrics (last 100 records)
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Save metrics
        with open(self.load_metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
    
    def _record_assignment_metrics(self, strategy: LoadBalancingStrategy, 
                                  assignment_time_ms: float, queue_size: int):
        """Record task assignment performance metrics."""
        
        # Update strategy performance tracking
        strategy_name = strategy.value
        if len(self.strategy_performance[strategy_name]) >= 20:
            self.strategy_performance[strategy_name].pop(0)
        self.strategy_performance[strategy_name].append(assignment_time_ms)
        
        # Update latest metrics record
        if self.metrics_history:
            self.metrics_history[-1]["assignment_latency_ms"] = assignment_time_ms
            self.metrics_history[-1]["task_queue_size"] = queue_size
    
    def complete_task(self, agent_id: str, task_id: str):
        """Mark a task as completed and update agent capacity."""
        
        if agent_id in self.agent_capacities:
            capacity = self.agent_capacities[agent_id]
            if capacity.current_task_count > 0:
                capacity.current_task_count -= 1
                self._save_agent_capacities()
                
                logger.info(f"✅ Task {task_id} completed by {agent_id}")
                
                # Process queued tasks that might now be assignable
                self._process_task_queues()
    
    def get_load_status(self) -> Dict:
        """Get current load balancing status."""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_strategy": self.current_strategy.value,
            "total_agents": len(self.agent_capacities),
            "agent_loads": {
                agent_id: {
                    "current_tasks": capacity.current_task_count,
                    "max_tasks": capacity.max_concurrent_tasks,
                    "load_percent": (capacity.current_task_count / capacity.max_concurrent_tasks) * 100,
                    "cpu_percent": capacity.cpu_usage_percent,
                    "memory_percent": capacity.memory_usage_percent,
                    "availability": capacity.availability_score
                }
                for agent_id, capacity in self.agent_capacities.items()
            },
            "queue_status": {
                priority.name: len(queue) 
                for priority, queue in self.task_queues.items()
            },
            "strategy_performance": dict(self.strategy_performance)
        }
    
    def rebalance_load(self):
        """Manually trigger load rebalancing."""
        
        logger.info("🔄 Triggering load rebalancing")
        
        # Identify overloaded and underloaded agents
        overloaded = []
        underloaded = []
        
        for agent_id, capacity in self.agent_capacities.items():
            load_percent = capacity.current_task_count / capacity.max_concurrent_tasks
            
            if load_percent > 0.8:  # Over 80% capacity
                overloaded.append(agent_id)
            elif load_percent < 0.3:  # Under 30% capacity
                underloaded.append(agent_id)
        
        if overloaded and underloaded:
            logger.info(f"🔄 Rebalancing: {len(overloaded)} overloaded, {len(underloaded)} underloaded agents")
            # In a real system, would implement task migration logic
        else:
            logger.info("✅ Load is well-balanced, no rebalancing needed")


def demonstrate_load_balancing():
    """Demonstrate the load balancing system."""
    
    logger.info("⚖️ Starting Load Balancing System Demonstration")
    
    balancer = LoadBalancer()
    
    print("\n" + "="*60)
    print("⚖️ LOAD BALANCING DEMO")
    print("="*60)
    
    # Start monitoring
    balancer.start_monitoring()
    
    # Create sample task requests
    sample_tasks = [
        TaskRequest(
            task_id="TASK-001",
            title="Security audit",
            description="Perform comprehensive security audit",
            domain="security",
            priority=TaskPriority.HIGH.value,
            estimated_duration_minutes=120,
            required_expertise_level="expert",
            deadline=(datetime.now() + timedelta(hours=4)).isoformat(),
            dependencies=[],
            resource_requirements={"cpu": 0.3, "memory": 0.2},
            metadata={"client": "internal", "type": "audit"}
        ),
        TaskRequest(
            task_id="TASK-002",
            title="Frontend optimization",
            description="Optimize React components for performance",
            domain="frontend",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration_minutes=90,
            required_expertise_level="proficient",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.2, "memory": 0.1},
            metadata={"framework": "react", "type": "optimization"}
        ),
        TaskRequest(
            task_id="TASK-003",
            title="Database migration",
            description="Migrate user data to new database schema",
            domain="infrastructure",
            priority=TaskPriority.CRITICAL.value,
            estimated_duration_minutes=180,
            required_expertise_level="expert",
            deadline=(datetime.now() + timedelta(hours=6)).isoformat(),
            dependencies=["TASK-001"],
            resource_requirements={"cpu": 0.4, "memory": 0.3},
            metadata={"database": "postgresql", "type": "migration"}
        ),
        TaskRequest(
            task_id="TASK-004",
            title="Analytics dashboard",
            description="Build new analytics dashboard",
            domain="data",
            priority=TaskPriority.LOW.value,
            estimated_duration_minutes=240,
            required_expertise_level="competent",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.2, "memory": 0.2},
            metadata={"visualization": "d3", "type": "dashboard"}
        ),
        TaskRequest(
            task_id="TASK-005",
            title="API testing",
            description="Comprehensive API endpoint testing",
            domain="quality",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration_minutes=60,
            required_expertise_level="competent",
            deadline=None,
            dependencies=["TASK-003"],
            resource_requirements={"cpu": 0.1, "memory": 0.1},
            metadata={"test_type": "integration", "coverage": "full"}
        )
    ]
    
    print("\n📋 Assigning tasks with different strategies:")
    
    strategies_to_test = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_CONNECTIONS,
        LoadBalancingStrategy.EXPERTISE_BASED,
        LoadBalancingStrategy.RESOURCE_AWARE
    ]
    
    # Test different strategies
    for i, task in enumerate(sample_tasks):
        strategy = strategies_to_test[i % len(strategies_to_test)]
        assigned_agent = balancer.assign_task(task, strategy)
        
        status = "✅ Assigned" if assigned_agent else "⏳ Queued"
        print(f"   {status} {task.task_id} ({task.domain}) → {assigned_agent or 'QUEUE'} [{strategy.value}]")
    
    # Show current load status
    print(f"\n📊 Current load status:")
    status = balancer.get_load_status()
    
    for agent_id, load_info in status["agent_loads"].items():
        load_percent = load_info["load_percent"]
        status_icon = "🔴" if load_percent > 80 else "🟡" if load_percent > 50 else "🟢"
        print(f"   {status_icon} {agent_id}: {load_info['current_tasks']}/{load_info['max_tasks']} tasks ({load_percent:.0f}%)")
    
    # Check queue status
    total_queued = sum(status["queue_status"].values())
    if total_queued > 0:
        print(f"\n⏳ Queued tasks: {total_queued}")
        for priority, count in status["queue_status"].items():
            if count > 0:
                print(f"   {priority}: {count}")
    
    # Test adaptive strategy performance
    print(f"\n🧠 Strategy performance:")
    for strategy, times in status["strategy_performance"].items():
        if times:
            avg_time = sum(times) / len(times)
            print(f"   {strategy}: {avg_time:.1f}ms avg ({len(times)} samples)")
    
    # Simulate task completion
    print(f"\n✅ Simulating task completions:")
    for agent_id, load_info in status["agent_loads"].items():
        if load_info["current_tasks"] > 0:
            balancer.complete_task(agent_id, f"COMPLETED-{agent_id}")
            print(f"   {agent_id} completed a task")
    
    # Check if queued tasks get assigned
    time.sleep(1)
    final_status = balancer.get_load_status()
    final_queued = sum(final_status["queue_status"].values())
    
    if final_queued < total_queued:
        print(f"📈 Queue processing: {total_queued - final_queued} tasks assigned from queue")
    
    # Trigger manual rebalancing
    print(f"\n🔄 Testing load rebalancing:")
    balancer.rebalance_load()
    
    # Stop monitoring
    balancer.stop_monitoring()
    
    print(f"\n💾 Configuration saved to:")
    print(f"   Load balancer config: {balancer.load_balancer_config_file}")
    print(f"   Agent capacities: {balancer.agent_capacity_file}")
    print(f"   Load metrics: {balancer.load_metrics_file}")
    
    logger.info("⚖️ Load balancing demonstration completed")


if __name__ == "__main__":
    demonstrate_load_balancing()