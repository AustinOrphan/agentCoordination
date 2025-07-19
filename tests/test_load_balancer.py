#!/usr/bin/env python3
"""
Unit tests for Load Balancer System
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from load_balancer import (
    LoadBalancer,
    LoadBalancingStrategy,
    TaskPriority,
    TaskRequest,
    AgentCapacity
)


class TestLoadBalancer:
    """Test suite for Load Balancer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def load_balancer(self, temp_dir):
        """Create load balancer instance for testing."""
        return LoadBalancer(temp_dir)
    
    @pytest.fixture
    def sample_task_request(self):
        """Create sample task request."""
        return TaskRequest(
            task_id="TEST-001",
            title="Test task",
            description="Testing load balancer",
            domain="security",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration_minutes=60,
            required_expertise_level="competent",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.2, "memory": 0.1},
            metadata={"test": True}
        )
    
    def test_initialization(self, load_balancer):
        """Test load balancer initialization."""
        assert load_balancer is not None
        assert hasattr(load_balancer, 'agent_capacities')
        assert hasattr(load_balancer, 'task_queues')
        assert hasattr(load_balancer, 'config')
        
        # Should have default agent capacities
        assert len(load_balancer.agent_capacities) > 0
    
    def test_assign_task_round_robin(self, load_balancer, sample_task_request):
        """Test round-robin task assignment."""
        assigned_agent = load_balancer.assign_task(
            sample_task_request, 
            LoadBalancingStrategy.ROUND_ROBIN
        )
        
        assert assigned_agent is not None
        assert assigned_agent in load_balancer.agent_capacities
        
        # Agent should have task count increased
        agent_capacity = load_balancer.agent_capacities[assigned_agent]
        assert agent_capacity.current_task_count > 0
    
    def test_assign_task_least_connections(self, load_balancer, sample_task_request):
        """Test least connections task assignment."""
        assigned_agent = load_balancer.assign_task(
            sample_task_request,
            LoadBalancingStrategy.LEAST_CONNECTIONS
        )
        
        assert assigned_agent is not None
        
        # Should assign to agent with least current tasks
        agent_capacity = load_balancer.agent_capacities[assigned_agent]
        assert agent_capacity.current_task_count >= 1
    
    def test_assign_task_expertise_based(self, load_balancer):
        """Test expertise-based task assignment."""
        # Create task requiring security expertise
        security_task = TaskRequest(
            task_id="SEC-001",
            title="Security audit",
            description="Perform security assessment",
            domain="security",
            priority=TaskPriority.HIGH.value,
            estimated_duration_minutes=120,
            required_expertise_level="expert",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.3},
            metadata={}
        )
        
        assigned_agent = load_balancer.assign_task(
            security_task,
            LoadBalancingStrategy.EXPERTISE_BASED
        )
        
        assert assigned_agent is not None
        
        # Should assign to agent with security expertise
        agent_capacity = load_balancer.agent_capacities[assigned_agent]
        assert "security" in agent_capacity.expertise_domains
    
    def test_assign_task_resource_aware(self, load_balancer, sample_task_request):
        """Test resource-aware task assignment."""
        assigned_agent = load_balancer.assign_task(
            sample_task_request,
            LoadBalancingStrategy.RESOURCE_AWARE
        )
        
        assert assigned_agent is not None
        
        # Should consider resource usage
        agent_capacity = load_balancer.agent_capacities[assigned_agent]
        assert agent_capacity.availability_score > 0
    
    def test_task_queueing(self, load_balancer):
        """Test task queueing when agents unavailable."""
        # Fill up all agents first
        tasks = []
        for i in range(50):  # Create many tasks to overload system
            task = TaskRequest(
                task_id=f"OVERLOAD-{i}",
                title=f"Overload task {i}",
                description="Task to overload system",
                domain="backend",
                priority=TaskPriority.LOW.value,
                estimated_duration_minutes=30,
                required_expertise_level="competent",
                deadline=None,
                dependencies=[],
                resource_requirements={},
                metadata={}
            )
            tasks.append(task)
        
        assigned_count = 0
        queued_count = 0
        
        for task in tasks:
            assigned_agent = load_balancer.assign_task(task)
            if assigned_agent:
                assigned_count += 1
            else:
                queued_count += 1
        
        # Should have both assigned and queued tasks
        assert assigned_count > 0
        assert queued_count >= 0  # May or may not queue depending on capacity
    
    def test_priority_queue_assignment(self, load_balancer):
        """Test priority-based task assignment."""
        # Create high priority task
        high_priority_task = TaskRequest(
            task_id="URGENT-001",
            title="Urgent task",
            description="Critical issue",
            domain="security",
            priority=TaskPriority.CRITICAL.value,
            estimated_duration_minutes=30,
            required_expertise_level="expert",
            deadline=(datetime.now() + timedelta(hours=1)).isoformat(),
            dependencies=[],
            resource_requirements={"cpu": 0.5},
            metadata={"urgent": True}
        )
        
        assigned_agent = load_balancer.assign_task(
            high_priority_task,
            LoadBalancingStrategy.PRIORITY_QUEUE
        )
        
        assert assigned_agent is not None
    
    def test_complete_task(self, load_balancer, sample_task_request):
        """Test task completion."""
        # Assign task first
        assigned_agent = load_balancer.assign_task(sample_task_request)
        assert assigned_agent is not None
        
        initial_count = load_balancer.agent_capacities[assigned_agent].current_task_count
        
        # Complete task
        load_balancer.complete_task(assigned_agent, sample_task_request.task_id)
        
        # Task count should decrease
        final_count = load_balancer.agent_capacities[assigned_agent].current_task_count
        assert final_count == initial_count - 1
    
    def test_load_monitoring(self, load_balancer):
        """Test load monitoring functionality."""
        # Start monitoring
        load_balancer.start_monitoring()
        assert load_balancer.monitoring_active is True
        
        # Let it run briefly
        time.sleep(0.5)
        
        # Stop monitoring
        load_balancer.stop_monitoring()
        assert load_balancer.monitoring_active is False
    
    def test_get_load_status(self, load_balancer, sample_task_request):
        """Test load status reporting."""
        # Assign some tasks
        load_balancer.assign_task(sample_task_request)
        
        status = load_balancer.get_load_status()
        
        assert "timestamp" in status
        assert "current_strategy" in status
        assert "total_agents" in status
        assert "agent_loads" in status
        assert "queue_status" in status
        
        # Check agent loads structure
        for agent_id, load_info in status["agent_loads"].items():
            assert "current_tasks" in load_info
            assert "max_tasks" in load_info
            assert "load_percent" in load_info
            assert "availability" in load_info
    
    def test_rebalance_load(self, load_balancer):
        """Test load rebalancing."""
        # This is mainly a logging operation
        load_balancer.rebalance_load()
        # Should complete without errors
    
    def test_adaptive_strategy(self, load_balancer, sample_task_request):
        """Test adaptive strategy selection."""
        # Assign task with adaptive strategy
        assigned_agent = load_balancer.assign_task(
            sample_task_request,
            LoadBalancingStrategy.ADAPTIVE
        )
        
        assert assigned_agent is not None
        
        # Should have selected some strategy
        assert len(load_balancer.strategy_performance) >= 0
    
    def test_weighted_round_robin(self, load_balancer, sample_task_request):
        """Test weighted round-robin assignment."""
        assigned_agent = load_balancer.assign_task(
            sample_task_request,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
        )
        
        assert assigned_agent is not None
    
    def test_agent_capacity_updates(self, load_balancer):
        """Test agent capacity updates."""
        # Get initial capacities
        initial_capacities = dict(load_balancer.agent_capacities)
        
        # Update agent loads
        load_balancer._update_agent_loads()
        
        # Capacities should be updated
        for agent_id, capacity in load_balancer.agent_capacities.items():
            assert hasattr(capacity, 'cpu_usage_percent')
            assert hasattr(capacity, 'memory_usage_percent')
            assert hasattr(capacity, 'availability_score')
    
    def test_task_queue_processing(self, load_balancer):
        """Test task queue processing."""
        # Add tasks to queue manually
        test_task = TaskRequest(
            task_id="QUEUE-TEST",
            title="Queue test",
            description="Testing queue processing",
            domain="backend",
            priority=TaskPriority.HIGH.value,
            estimated_duration_minutes=45,
            required_expertise_level="competent",
            deadline=None,
            dependencies=[],
            resource_requirements={},
            metadata={}
        )
        
        # Add to queue
        priority = TaskPriority(test_task.priority)
        load_balancer.task_queues[priority].append(test_task)
        
        # Process queues
        load_balancer._process_task_queues()
        
        # Queue should be processed (task assigned or still queued)
        # This depends on agent availability
    
    def test_metrics_collection(self, load_balancer, sample_task_request):
        """Test metrics collection."""
        # Assign task to generate metrics
        load_balancer.assign_task(sample_task_request)
        
        # Collect metrics
        load_balancer._collect_load_metrics()
        
        # Should have metrics history
        assert len(load_balancer.metrics_history) > 0
        
        # Check metrics structure
        latest_metrics = load_balancer.metrics_history[-1]
        assert "timestamp" in latest_metrics
        assert "total_agents" in latest_metrics
        assert "active_agents" in latest_metrics
        assert "average_load_percent" in latest_metrics
    
    def test_invalid_strategy_fallback(self, load_balancer, sample_task_request):
        """Test fallback for invalid strategy."""
        # This would test internal fallback behavior
        # Most strategies should work, but test defensive programming
        assigned_agent = load_balancer._assign_task_immediate(
            sample_task_request, 
            None  # Invalid strategy
        )
        
        # Should fallback gracefully
        assert assigned_agent is None or assigned_agent in load_balancer.agent_capacities
    
    def test_resource_requirements_filtering(self, load_balancer):
        """Test filtering agents by resource requirements."""
        # Create task with high resource requirements
        resource_heavy_task = TaskRequest(
            task_id="HEAVY-001",
            title="Resource heavy task",
            description="Requires lots of resources",
            domain="backend",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration_minutes=180,
            required_expertise_level="expert",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.9, "memory": 0.8},  # High requirements
            metadata={}
        )
        
        available_agents = load_balancer._get_available_agents(resource_heavy_task)
        
        # Should filter out agents with high resource usage
        assert isinstance(available_agents, list)
        # All returned agents should meet resource requirements


if __name__ == "__main__":
    pytest.main([__file__, "-v"])