#!/usr/bin/env python3
"""
Edge case data generators for BDD testing.
Uses Hypothesis strategies to generate complex test scenarios.
"""

import random
import string
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

try:
    import hypothesis.strategies as st
    from hypothesis import composite
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Fallback implementations if hypothesis not available

# Add project imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from coordination_system.conflict_resolution import ConflictType, ConflictSeverity
from coordination_system.load_balancer import LoadBalancingStrategy, TaskPriority


class EdgeCaseType(Enum):
    """Types of edge cases for testing."""
    NORMAL = "normal"
    BOUNDARY = "boundary"
    EXTREME = "extreme"
    INVALID = "invalid"
    STRESS = "stress"


@dataclass
class AgentConfiguration:
    """Agent configuration for testing."""
    name: str
    expertise_domains: List[str]
    max_concurrent_tasks: int
    cpu_cores: int
    memory_gb: int
    current_workload: float = 0.0
    status: str = "active"
    network_latency_ms: int = 10
    reliability_score: float = 0.95


@dataclass
class TaskRequest:
    """Task request for testing."""
    id: str
    description: str
    domain: str
    priority: TaskPriority
    estimated_duration: int
    resource_requirements: Dict[str, Any]
    dependencies: List[str] = None
    required_expertise: List[str] = None
    deadline: Optional[datetime] = None


@dataclass
class ConflictScenario:
    """Conflict scenario for testing."""
    conflict_type: ConflictType
    severity: ConflictSeverity
    parties: List[str]
    description: str
    context: Dict[str, Any]
    cascade_trigger: Optional[str] = None
    resolution_timeout: int = 300


@dataclass
class WorkloadPattern:
    """Workload pattern for testing."""
    pattern_type: str
    agent_workloads: Dict[str, float]
    task_arrival_rate: float
    peak_hours: List[int]
    failure_probability: float = 0.0


class EdgeCaseGenerators:
    """Collection of edge case generators for testing."""
    
    DOMAINS = [
        "security", "frontend", "backend", "infrastructure", 
        "devops", "database", "machine_learning", "testing",
        "documentation", "api_design", "ui_ux", "performance"
    ]
    
    AGENT_NAMES = [
        "shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse",
        "tuna", "salmon", "marlin", "stingray", "turtle", "orca"
    ]
    
    CONFLICT_DESCRIPTIONS = [
        "Resource allocation dispute",
        "Authority over feature development",
        "Code review disagreement",
        "Architecture decision conflict",
        "Priority setting dispute",
        "Testing strategy disagreement",
        "Deployment timeline conflict",
        "Performance optimization approach"
    ]
    
    @staticmethod
    def generate_agent_name() -> str:
        """Generate random agent name."""
        if random.random() < 0.8:  # 80% use predefined names
            return random.choice(EdgeCaseGenerators.AGENT_NAMES)
        else:  # 20% generate new names
            return f"agent_{random.randint(100, 999)}"
    
    @staticmethod
    def generate_domain() -> str:
        """Generate random domain."""
        return random.choice(EdgeCaseGenerators.DOMAINS)
    
    @staticmethod
    def generate_expertise_domains(count: Optional[int] = None) -> List[str]:
        """Generate list of expertise domains."""
        if count is None:
            count = random.randint(1, 4)
        return random.sample(EdgeCaseGenerators.DOMAINS, min(count, len(EdgeCaseGenerators.DOMAINS)))


# Hypothesis strategies (if available)
if HYPOTHESIS_AVAILABLE:
    
    @composite
    def agent_configurations(draw, 
                           edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL,
                           count: Optional[int] = None) -> List[AgentConfiguration]:
        """Generate agent configurations using Hypothesis."""
        if count is None:
            count = draw(st.integers(min_value=1, max_value=12))
        
        agents = []
        used_names = set()
        
        for i in range(count):
            # Generate unique agent name
            if edge_case_type == EdgeCaseType.EXTREME:
                name = draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and x not in used_names))
            else:
                name_choice = draw(st.sampled_from(EdgeCaseGenerators.AGENT_NAMES + [f"agent_{i}"]))
                name = name_choice if name_choice not in used_names else f"agent_{i}"
            used_names.add(name)
            
            # Generate expertise domains
            domain_count = draw(st.integers(min_value=1, max_value=5))
            if edge_case_type == EdgeCaseType.EXTREME:
                # Some agents have no expertise or too many
                domain_count = draw(st.integers(min_value=0, max_value=len(EdgeCaseGenerators.DOMAINS)))
            
            expertise = draw(st.lists(
                st.sampled_from(EdgeCaseGenerators.DOMAINS),
                min_size=domain_count,
                max_size=domain_count,
                unique=True
            ))
            
            # Generate resource specifications
            if edge_case_type == EdgeCaseType.EXTREME:
                max_tasks = draw(st.integers(min_value=0, max_value=1000))
                cpu_cores = draw(st.integers(min_value=1, max_value=128))
                memory_gb = draw(st.integers(min_value=1, max_value=1024))
                workload = draw(st.floats(min_value=0.0, max_value=200.0))  # Over 100% workload
                latency = draw(st.integers(min_value=1, max_value=10000))
                reliability = draw(st.floats(min_value=0.0, max_value=1.0))
            else:
                max_tasks = draw(st.integers(min_value=5, max_value=50))
                cpu_cores = draw(st.integers(min_value=2, max_value=32))
                memory_gb = draw(st.integers(min_value=4, max_value=64))
                workload = draw(st.floats(min_value=0.0, max_value=100.0))
                latency = draw(st.integers(min_value=1, max_value=500))
                reliability = draw(st.floats(min_value=0.8, max_value=1.0))
            
            status = draw(st.sampled_from(["active", "inactive", "maintenance", "offline"]))
            
            agent = AgentConfiguration(
                name=name,
                expertise_domains=expertise,
                max_concurrent_tasks=max_tasks,
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                current_workload=workload,
                status=status,
                network_latency_ms=latency,
                reliability_score=reliability
            )
            agents.append(agent)
        
        return agents
    
    @composite
    def task_requests(draw,
                     edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL,
                     count: Optional[int] = None) -> List[TaskRequest]:
        """Generate task requests using Hypothesis."""
        if count is None:
            count = draw(st.integers(min_value=1, max_value=100))
        
        tasks = []
        
        for i in range(count):
            task_id = f"TASK-{i:04d}"
            
            if edge_case_type == EdgeCaseType.EXTREME:
                description = draw(st.text(min_size=0, max_size=10000))
                duration = draw(st.integers(min_value=-1, max_value=100000))  # Negative duration
                cpu_req = draw(st.integers(min_value=-10, max_value=1000))
                memory_req = draw(st.integers(min_value=-1000, max_value=100000))
            else:
                description = draw(st.text(min_size=5, max_size=200).filter(lambda x: x.strip()))
                duration = draw(st.integers(min_value=1, max_value=480))  # 1-480 minutes
                cpu_req = draw(st.integers(min_value=1, max_value=100))
                memory_req = draw(st.integers(min_value=100, max_value=8192))
            
            domain = draw(st.sampled_from(EdgeCaseGenerators.DOMAINS))
            priority = draw(st.sampled_from(list(TaskPriority)))
            
            # Generate dependencies
            if i > 0 and random.random() < 0.3:  # 30% chance of dependencies
                dep_count = draw(st.integers(min_value=1, max_value=min(3, i)))
                dependencies = [f"TASK-{j:04d}" for j in random.sample(range(i), dep_count)]
            else:
                dependencies = []
            
            # Generate required expertise
            expertise_count = draw(st.integers(min_value=0, max_value=3))
            required_expertise = draw(st.lists(
                st.sampled_from(EdgeCaseGenerators.DOMAINS),
                min_size=expertise_count,
                max_size=expertise_count,
                unique=True
            )) if expertise_count > 0 else []
            
            # Generate deadline
            deadline = None
            if random.random() < 0.4:  # 40% chance of deadline
                deadline = datetime.now() + timedelta(
                    hours=draw(st.integers(min_value=1, max_value=168))  # 1-168 hours
                )
            
            task = TaskRequest(
                id=task_id,
                description=description,
                domain=domain,
                priority=priority,
                estimated_duration=duration,
                resource_requirements={
                    "cpu": cpu_req,
                    "memory": memory_req,
                    "disk": draw(st.integers(min_value=0, max_value=10240)),
                    "network": draw(st.integers(min_value=0, max_value=1000))
                },
                dependencies=dependencies,
                required_expertise=required_expertise,
                deadline=deadline
            )
            tasks.append(task)
        
        return tasks
    
    @composite
    def conflict_scenarios(draw,
                          edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL,
                          count: Optional[int] = None) -> List[ConflictScenario]:
        """Generate conflict scenarios using Hypothesis."""
        if count is None:
            count = draw(st.integers(min_value=1, max_value=20))
        
        conflicts = []
        
        for i in range(count):
            conflict_type = draw(st.sampled_from(list(ConflictType)))
            severity = draw(st.sampled_from(list(ConflictSeverity)))
            
            # Generate parties
            if edge_case_type == EdgeCaseType.EXTREME:
                party_count = draw(st.integers(min_value=0, max_value=20))  # 0 parties (invalid)
            else:
                party_count = draw(st.integers(min_value=2, max_value=6))
            
            parties = draw(st.lists(
                st.sampled_from(EdgeCaseGenerators.AGENT_NAMES),
                min_size=party_count,
                max_size=party_count,
                unique=True
            )) if party_count > 0 else []
            
            description = draw(st.sampled_from(EdgeCaseGenerators.CONFLICT_DESCRIPTIONS))
            
            # Generate context
            context = {
                "resource": draw(st.sampled_from(["database_connection", "api_endpoint", "file_lock", "memory_pool"])),
                "impact_level": draw(st.sampled_from(["low", "medium", "high", "critical"])),
                "affected_systems": draw(st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=5)),
                "time_sensitive": draw(st.booleans()),
                "escalation_level": draw(st.integers(min_value=0, max_value=5))
            }
            
            # Generate cascade trigger (for cascading conflicts)
            cascade_trigger = None
            if i > 0 and random.random() < 0.2:  # 20% chance of cascading
                cascade_trigger = f"CONFLICT-{random.randint(0, i-1):04d}"
            
            # Generate resolution timeout
            if edge_case_type == EdgeCaseType.EXTREME:
                timeout = draw(st.integers(min_value=-1, max_value=86400))  # Negative timeout
            else:
                timeout = draw(st.integers(min_value=30, max_value=3600))
            
            conflict = ConflictScenario(
                conflict_type=conflict_type,
                severity=severity,
                parties=parties,
                description=description,
                context=context,
                cascade_trigger=cascade_trigger,
                resolution_timeout=timeout
            )
            conflicts.append(conflict)
        
        return conflicts
    
    @composite
    def workload_patterns(draw,
                         edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL) -> WorkloadPattern:
        """Generate workload patterns using Hypothesis."""
        pattern_types = ["uniform", "peak_hours", "bursty", "seasonal", "random", "extreme_peak"]
        
        if edge_case_type == EdgeCaseType.EXTREME:
            pattern_types.extend(["system_overload", "cascade_failure", "deadlock_pattern"])
        
        pattern_type = draw(st.sampled_from(pattern_types))
        
        # Generate agent workloads
        agent_count = draw(st.integers(min_value=3, max_value=12))
        agent_names = EdgeCaseGenerators.AGENT_NAMES[:agent_count]
        
        if pattern_type == "uniform":
            base_load = draw(st.floats(min_value=20.0, max_value=80.0))
            agent_workloads = {name: base_load + draw(st.floats(min_value=-10.0, max_value=10.0)) 
                             for name in agent_names}
        elif pattern_type == "extreme_peak":
            agent_workloads = {}
            for name in agent_names:
                if random.random() < 0.3:  # 30% of agents at extreme load
                    agent_workloads[name] = draw(st.floats(min_value=95.0, max_value=150.0))
                else:
                    agent_workloads[name] = draw(st.floats(min_value=5.0, max_value=30.0))
        elif pattern_type == "system_overload":
            # All agents overloaded
            agent_workloads = {name: draw(st.floats(min_value=100.0, max_value=200.0)) 
                             for name in agent_names}
        else:
            # Random distribution
            agent_workloads = {name: draw(st.floats(min_value=0.0, max_value=100.0)) 
                             for name in agent_names}
        
        # Generate task arrival rate
        if edge_case_type == EdgeCaseType.EXTREME:
            arrival_rate = draw(st.floats(min_value=0.0, max_value=1000.0))  # Very high rate
        else:
            arrival_rate = draw(st.floats(min_value=0.1, max_value=50.0))
        
        # Generate peak hours
        peak_count = draw(st.integers(min_value=1, max_value=6))
        peak_hours = draw(st.lists(
            st.integers(min_value=0, max_value=23),
            min_size=peak_count,
            max_size=peak_count,
            unique=True
        ))
        
        # Generate failure probability
        if edge_case_type == EdgeCaseType.EXTREME:
            failure_prob = draw(st.floats(min_value=0.0, max_value=0.5))  # Up to 50% failure rate
        else:
            failure_prob = draw(st.floats(min_value=0.0, max_value=0.1))  # Up to 10% failure rate
        
        return WorkloadPattern(
            pattern_type=pattern_type,
            agent_workloads=agent_workloads,
            task_arrival_rate=arrival_rate,
            peak_hours=peak_hours,
            failure_probability=failure_prob
        )
    
    # Network conditions generator
    @composite
    def network_conditions(draw,
                          edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL) -> Dict[str, Any]:
        """Generate network conditions for communication testing."""
        if edge_case_type == EdgeCaseType.EXTREME:
            latency = draw(st.integers(min_value=0, max_value=30000))  # Up to 30 seconds
            packet_loss = draw(st.floats(min_value=0.0, max_value=50.0))  # Up to 50% loss
            bandwidth_mbps = draw(st.floats(min_value=0.001, max_value=1.0))  # Very low bandwidth
            jitter = draw(st.integers(min_value=0, max_value=5000))
        else:
            latency = draw(st.integers(min_value=1, max_value=1000))
            packet_loss = draw(st.floats(min_value=0.0, max_value=10.0))
            bandwidth_mbps = draw(st.floats(min_value=1.0, max_value=1000.0))
            jitter = draw(st.integers(min_value=0, max_value=100))
        
        return {
            "latency_ms": latency,
            "packet_loss_percent": packet_loss,
            "bandwidth_mbps": bandwidth_mbps,
            "jitter_ms": jitter,
            "connection_drops": draw(st.booleans()),
            "partition_probability": draw(st.floats(min_value=0.0, max_value=0.1))
        }


# Fallback generators (if Hypothesis not available)
class FallbackGenerators:
    """Fallback generators when Hypothesis is not available."""
    
    @staticmethod
    def agent_configurations(edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL,
                           count: Optional[int] = None) -> List[AgentConfiguration]:
        """Generate agent configurations without Hypothesis."""
        if count is None:
            count = random.randint(3, 8)
        
        agents = []
        for i in range(count):
            name = EdgeCaseGenerators.AGENT_NAMES[i] if i < len(EdgeCaseGenerators.AGENT_NAMES) else f"agent_{i}"
            
            agent = AgentConfiguration(
                name=name,
                expertise_domains=EdgeCaseGenerators.generate_expertise_domains(),
                max_concurrent_tasks=random.randint(5, 50),
                cpu_cores=random.choice([2, 4, 8, 16, 32]),
                memory_gb=random.choice([4, 8, 16, 32, 64]),
                current_workload=random.uniform(0.0, 100.0),
                status=random.choice(["active", "inactive", "maintenance"]),
                network_latency_ms=random.randint(10, 500),
                reliability_score=random.uniform(0.8, 1.0)
            )
            agents.append(agent)
        
        return agents
    
    @staticmethod
    def task_requests(edge_case_type: EdgeCaseType = EdgeCaseType.NORMAL,
                     count: Optional[int] = None) -> List[TaskRequest]:
        """Generate task requests without Hypothesis."""
        if count is None:
            count = random.randint(5, 20)
        
        tasks = []
        for i in range(count):
            task = TaskRequest(
                id=f"TASK-{i:04d}",
                description=f"Test task {i}",
                domain=random.choice(EdgeCaseGenerators.DOMAINS),
                priority=random.choice(list(TaskPriority)),
                estimated_duration=random.randint(30, 480),
                resource_requirements={
                    "cpu": random.randint(10, 100),
                    "memory": random.randint(512, 8192),
                    "disk": random.randint(0, 10240),
                    "network": random.randint(0, 1000)
                },
                dependencies=[],
                required_expertise=EdgeCaseGenerators.generate_expertise_domains(random.randint(0, 2))
            )
            tasks.append(task)
        
        return tasks


# Main interface
def get_generators():
    """Get the appropriate generators based on availability."""
    if HYPOTHESIS_AVAILABLE:
        return {
            'agent_configurations': agent_configurations,
            'task_requests': task_requests,
            'conflict_scenarios': conflict_scenarios,
            'workload_patterns': workload_patterns,
            'network_conditions': network_conditions
        }
    else:
        return {
            'agent_configurations': FallbackGenerators.agent_configurations,
            'task_requests': FallbackGenerators.task_requests,
            'conflict_scenarios': lambda **kwargs: [],
            'workload_patterns': lambda **kwargs: None,
            'network_conditions': lambda **kwargs: {}
        }


# Convenience functions
def generate_edge_case_agents(count: int = 6, 
                            edge_type: EdgeCaseType = EdgeCaseType.NORMAL) -> List[AgentConfiguration]:
    """Generate agents for edge case testing."""
    generators = get_generators()
    if HYPOTHESIS_AVAILABLE:
        return generators['agent_configurations'](edge_case_type=edge_type, count=count).example()
    else:
        return generators['agent_configurations'](edge_case_type=edge_type, count=count)


def generate_edge_case_tasks(count: int = 10,
                           edge_type: EdgeCaseType = EdgeCaseType.NORMAL) -> List[TaskRequest]:
    """Generate tasks for edge case testing."""
    generators = get_generators()
    if HYPOTHESIS_AVAILABLE:
        return generators['task_requests'](edge_case_type=edge_type, count=count).example()
    else:
        return generators['task_requests'](edge_case_type=edge_type, count=count)


def generate_extreme_workload() -> WorkloadPattern:
    """Generate extreme workload pattern for stress testing."""
    generators = get_generators()
    if HYPOTHESIS_AVAILABLE:
        return generators['workload_patterns'](edge_case_type=EdgeCaseType.EXTREME).example()
    else:
        return WorkloadPattern(
            pattern_type="extreme_peak",
            agent_workloads={name: random.uniform(90.0, 150.0) for name in EdgeCaseGenerators.AGENT_NAMES[:6]},
            task_arrival_rate=100.0,
            peak_hours=[9, 10, 11, 14, 15, 16],
            failure_probability=0.2
        )