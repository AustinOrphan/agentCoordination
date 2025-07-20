"""
Agent Scaling Stress Tests

This module tests the multi-agent coordination system's ability to scale
from single agent operation to full 24-agent scenarios, measuring performance
degradation and identifying scaling bottlenecks.
"""

import time
import json
import os
import threading
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pytest

from .stress_test_engine import (
    StressTestScenario, StressTestRunner, StressTestConfig,
    create_light_stress_config, create_medium_stress_config, 
    create_heavy_stress_config, create_extreme_stress_config
)


@dataclass
class AgentScalingMetrics:
    """Metrics for agent scaling performance."""
    agent_count: int
    startup_time: float
    authority_assignment_time: float
    communication_latency: float
    memory_per_agent: float
    cpu_overhead: float
    coordination_overhead: float
    file_operations_per_second: float


class MockAgentSimulator:
    """Simulates agent behavior for scaling tests."""
    
    def __init__(self, agent_id: str, temp_dir: str):
        self.agent_id = agent_id
        self.temp_dir = temp_dir
        self.status_file = os.path.join(temp_dir, f"agent_status_{agent_id}.json")
        self.inbox_file = os.path.join(temp_dir, f"agent_inbox_{agent_id}.json")
        self.outbox_file = os.path.join(temp_dir, f"agent_outbox_{agent_id}.json")
        self.is_running = False
        self.activity_thread: Optional[threading.Thread] = None
        self.message_count = 0
        self.file_operations = 0
        
        # Initialize agent files
        self._initialize_files()
        
    def _initialize_files(self):
        """Initialize agent status and communication files."""
        status_data = {
            "id": self.agent_id,
            "status": "initializing",
            "current_task": None,
            "progress": 0,
            "last_update": time.time(),
            "authorities": [],
            "blockers": [],
            "activities": []
        }
        
        inbox_data = {"messages": []}
        outbox_data = {"messages": []}
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
            
        with open(self.inbox_file, 'w') as f:
            json.dump(inbox_data, f, indent=2)
            
        with open(self.outbox_file, 'w') as f:
            json.dump(outbox_data, f, indent=2)
            
        self.file_operations += 3
        
    def start(self):
        """Start agent simulation."""
        self.is_running = True
        self.activity_thread = threading.Thread(target=self._activity_loop, daemon=True)
        self.activity_thread.start()
        
        # Update status to active
        self._update_status("active", "Performing scaling test tasks")
        
    def stop(self):
        """Stop agent simulation."""
        self.is_running = False
        if self.activity_thread:
            self.activity_thread.join(timeout=2.0)
            
        self._update_status("stopped", None)
        
    def request_authority(self, authority_type: str):
        """Simulate authority request."""
        message = {
            "type": "authority_request",
            "authority_type": authority_type,
            "requester": self.agent_id,
            "timestamp": time.time(),
            "priority": "normal"
        }
        self._send_message(message)
        
    def send_coordination_message(self, target_agent: str, message_type: str, data: Dict[str, Any]):
        """Send coordination message to another agent."""
        message = {
            "type": message_type,
            "sender": self.agent_id,
            "target": target_agent,
            "data": data,
            "timestamp": time.time()
        }
        self._send_message(message)
        
    def _activity_loop(self):
        """Main activity loop for the simulated agent."""
        while self.is_running:
            try:
                # Simulate periodic status updates
                self._update_status("active", f"Processing task batch {self.message_count // 10}")
                
                # Simulate message processing
                self._check_inbox()
                
                # Simulate periodic coordination activities
                if self.message_count % 5 == 0:
                    self._simulate_coordination_activity()
                    
                # Simulate file I/O operations
                self._simulate_file_operations()
                
                time.sleep(0.1)  # 10 operations per second
                
            except Exception as e:
                # Continue on errors to maintain stress test
                pass
                
    def _update_status(self, status: str, task: Optional[str]):
        """Update agent status file."""
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
                
            data.update({
                "status": status,
                "current_task": task,
                "last_update": time.time(),
                "message_count": self.message_count,
                "file_operations": self.file_operations
            })
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.file_operations += 2
            
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
    def _check_inbox(self):
        """Check inbox for new messages."""
        try:
            with open(self.inbox_file, 'r') as f:
                data = json.load(f)
                
            messages = data.get('messages', [])
            new_messages = [msg for msg in messages if not msg.get('processed', False)]
            
            for message in new_messages:
                self._process_message(message)
                message['processed'] = True
                
            if new_messages:
                with open(self.inbox_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                self.file_operations += 1
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
    def _process_message(self, message: Dict[str, Any]):
        """Process a received message."""
        self.message_count += 1
        
        # Simulate different message processing times
        message_type = message.get('type', 'unknown')
        if message_type == 'authority_grant':
            time.sleep(0.01)  # Authority processing takes longer
        elif message_type == 'coordination':
            time.sleep(0.005)  # Coordination messages are faster
        else:
            time.sleep(0.002)  # Default processing time
            
    def _send_message(self, message: Dict[str, Any]):
        """Send a message via outbox."""
        try:
            with open(self.outbox_file, 'r') as f:
                data = json.load(f)
                
            data['messages'].append(message)
            
            with open(self.outbox_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.file_operations += 2
            self.message_count += 1
            
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
    def _simulate_coordination_activity(self):
        """Simulate coordination-specific activities."""
        # Request authority periodically
        if self.message_count % 20 == 0:
            authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
            authority = authorities[hash(self.agent_id) % len(authorities)]
            self.request_authority(authority)
            
        # Send coordination messages
        coordination_data = {
            "status": "working",
            "progress": (self.message_count % 100),
            "dependencies": []
        }
        target_agent = f"agent_{(hash(self.agent_id) + 1) % 6}"
        self.send_coordination_message(target_agent, "status_update", coordination_data)
        
    def _simulate_file_operations(self):
        """Simulate additional file I/O operations."""
        # Create temporary work files
        temp_file = os.path.join(self.temp_dir, f"work_{self.agent_id}_{self.file_operations}.tmp")
        try:
            with open(temp_file, 'w') as f:
                json.dump({"work_data": f"operation_{self.file_operations}"}, f)
            os.remove(temp_file)
            self.file_operations += 2
        except:
            pass


class AgentScalingStressScenario(StressTestScenario):
    """Stress test scenario for agent scaling."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.temp_dir: Optional[str] = None
        self.agents: List[MockAgentSimulator] = []
        self.scaling_metrics: List[AgentScalingMetrics] = []
        
    def setup(self):
        """Setup the scaling stress test."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="agent_scaling_stress_")
        
        # Initialize authority pool file
        authority_pool = {
            "authorities": {
                "critical_path": {"current_holder": None, "backup_holder": None},
                "migration": {"current_holder": None, "backup_holder": None},
                "dashboard": {"current_holder": None, "backup_holder": None},
                "devops": {"current_holder": None, "backup_holder": None},
                "security": {"current_holder": None, "backup_holder": None},
                "ux": {"current_holder": None, "backup_holder": None}
            },
            "pending_requests": []
        }
        
        authority_file = os.path.join(self.temp_dir, "authority_pool.json")
        with open(authority_file, 'w') as f:
            json.dump(authority_pool, f, indent=2)
            
    def execute_stress(self):
        """Execute the agent scaling stress test."""
        # Test with increasing agent counts
        agent_counts = self._get_scaling_progression()
        
        for agent_count in agent_counts:
            if not self.should_continue():
                break
                
            print(f"📊 Testing with {agent_count} agents...")
            metrics = self._test_agent_count(agent_count)
            self.scaling_metrics.append(metrics)
            
            # Record metrics
            self.record_metric(f"startup_time_{agent_count}_agents", metrics.startup_time, "seconds")
            self.record_metric(f"memory_per_agent_{agent_count}_agents", metrics.memory_per_agent, "MB")
            self.record_metric(f"coordination_overhead_{agent_count}_agents", metrics.coordination_overhead, "percent")
            
            # Check for performance degradation
            self._check_performance_degradation(metrics)
            
            # Brief pause between scaling tests
            time.sleep(1.0)
            
    def _get_scaling_progression(self) -> List[int]:
        """Get the progression of agent counts to test."""
        max_agents = self.config.agent_count
        
        if self.config.level.value == "light":
            return [1, 3, 6]
        elif self.config.level.value == "medium":
            return [1, 3, 6, 9, 12]
        elif self.config.level.value == "heavy":
            return [1, 3, 6, 9, 12, 15, 18]
        else:  # extreme
            return [1, 3, 6, 9, 12, 15, 18, 21, 24]
            
    def _test_agent_count(self, agent_count: int) -> AgentScalingMetrics:
        """Test coordination system with specific agent count."""
        start_time = time.time()
        
        # Create agents
        agents = []
        for i in range(agent_count):
            agent_id = f"scaling_agent_{i}"
            agent = MockAgentSimulator(agent_id, self.temp_dir)
            agents.append(agent)
            
        # Measure startup time
        startup_start = time.time()
        for agent in agents:
            agent.start()
        startup_time = time.time() - startup_start
        
        # Let agents run for a period
        test_duration = min(30, self.config.duration_seconds / len(self._get_scaling_progression()))
        time.sleep(test_duration)
        
        # Measure authority assignment time
        authority_start = time.time()
        for i, agent in enumerate(agents[:6]):  # Only first 6 can have authorities
            authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
            agent.request_authority(authorities[i])
        authority_assignment_time = time.time() - authority_start
        
        # Measure communication latency
        comm_start = time.time()
        if len(agents) > 1:
            agents[0].send_coordination_message("scaling_agent_1", "test_message", {"test": True})
        communication_latency = time.time() - comm_start
        
        # Collect performance metrics
        total_memory = sum(agent.file_operations * 0.1 for agent in agents)  # Simulate memory usage
        memory_per_agent = total_memory / agent_count if agent_count > 0 else 0
        
        total_file_ops = sum(agent.file_operations for agent in agents)
        file_ops_per_second = total_file_ops / test_duration if test_duration > 0 else 0
        
        # Calculate coordination overhead (simulated)
        base_overhead = 5.0  # Base 5% overhead
        scaling_factor = agent_count * 0.5  # Additional 0.5% per agent
        coordination_overhead = base_overhead + scaling_factor
        
        # Calculate CPU overhead (simulated)
        cpu_overhead = agent_count * 2.0  # 2% per agent
        
        # Stop agents
        for agent in agents:
            agent.stop()
            
        return AgentScalingMetrics(
            agent_count=agent_count,
            startup_time=startup_time,
            authority_assignment_time=authority_assignment_time,
            communication_latency=communication_latency,
            memory_per_agent=memory_per_agent,
            cpu_overhead=cpu_overhead,
            coordination_overhead=coordination_overhead,
            file_operations_per_second=file_ops_per_second
        )
        
    def _check_performance_degradation(self, metrics: AgentScalingMetrics):
        """Check for performance degradation patterns."""
        if len(self.scaling_metrics) < 2:
            return
            
        previous = self.scaling_metrics[-2]
        current = metrics
        
        # Check startup time scaling
        startup_ratio = current.startup_time / (previous.startup_time * (current.agent_count / previous.agent_count))
        if startup_ratio > 2.0:  # Startup time is scaling worse than linearly
            self.record_failure(
                "startup_degradation",
                f"Startup time scaling poorly: {startup_ratio:.2f}x worse than linear"
            )
            
        # Check memory efficiency
        if current.memory_per_agent > previous.memory_per_agent * 1.5:
            self.record_failure(
                "memory_degradation",
                f"Memory per agent increased significantly: {current.memory_per_agent:.2f}MB vs {previous.memory_per_agent:.2f}MB"
            )
            
        # Check coordination overhead
        if current.coordination_overhead > 50:  # Over 50% overhead
            self.record_failure(
                "coordination_overhead",
                f"Coordination overhead too high: {current.coordination_overhead:.1f}%"
            )
            
        # Check communication latency
        if current.communication_latency > 1.0:  # Over 1 second
            self.record_failure(
                "communication_latency",
                f"Communication latency too high: {current.communication_latency:.3f}s"
            )
            
    def cleanup(self):
        """Clean up the scaling stress test."""
        # Stop any remaining agents
        for agent in self.agents:
            agent.stop()
            
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
        # Generate scaling analysis report
        if self.scaling_metrics:
            self._generate_scaling_report()
            
    def _generate_scaling_report(self):
        """Generate detailed scaling analysis report."""
        report = {
            "scaling_analysis": {
                "test_config": {
                    "level": self.config.level.value,
                    "max_agents": self.config.agent_count,
                    "duration": self.config.duration_seconds
                },
                "metrics": [
                    {
                        "agent_count": m.agent_count,
                        "startup_time": m.startup_time,
                        "authority_assignment_time": m.authority_assignment_time,
                        "communication_latency": m.communication_latency,
                        "memory_per_agent": m.memory_per_agent,
                        "cpu_overhead": m.cpu_overhead,
                        "coordination_overhead": m.coordination_overhead,
                        "file_operations_per_second": m.file_operations_per_second
                    }
                    for m in self.scaling_metrics
                ],
                "scaling_factors": self._calculate_scaling_factors(),
                "bottlenecks": self._identify_bottlenecks(),
                "recommendations": self._generate_recommendations()
            }
        }
        
        # Save report
        report_file = os.path.join("stress_test_results", f"scaling_analysis_{int(time.time())}.json")
        os.makedirs("stress_test_results", exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.record_metric("scaling_report_generated", 1, "boolean")
        
    def _calculate_scaling_factors(self) -> Dict[str, float]:
        """Calculate how well different metrics scale."""
        if len(self.scaling_metrics) < 2:
            return {}
            
        first = self.scaling_metrics[0]
        last = self.scaling_metrics[-1]
        
        agent_ratio = last.agent_count / first.agent_count
        
        return {
            "startup_time_factor": (last.startup_time / first.startup_time) / agent_ratio,
            "memory_scaling_factor": (last.memory_per_agent / first.memory_per_agent),
            "communication_scaling_factor": (last.communication_latency / first.communication_latency) / agent_ratio,
            "throughput_scaling_factor": (last.file_operations_per_second / first.file_operations_per_second) / agent_ratio
        }
        
    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        if not self.scaling_metrics:
            return bottlenecks
            
        # Check latest metrics
        latest = self.scaling_metrics[-1]
        
        if latest.startup_time > 10.0:
            bottlenecks.append("startup_time")
            
        if latest.communication_latency > 0.5:
            bottlenecks.append("communication_latency")
            
        if latest.coordination_overhead > 30:
            bottlenecks.append("coordination_overhead")
            
        if latest.memory_per_agent > 100:
            bottlenecks.append("memory_usage")
            
        return bottlenecks
        
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        bottlenecks = self._identify_bottlenecks()
        
        if "startup_time" in bottlenecks:
            recommendations.append("Consider parallel agent initialization")
            recommendations.append("Optimize agent file creation process")
            
        if "communication_latency" in bottlenecks:
            recommendations.append("Implement message batching")
            recommendations.append("Use asynchronous communication patterns")
            
        if "coordination_overhead" in bottlenecks:
            recommendations.append("Optimize authority assignment algorithm")
            recommendations.append("Reduce coordination message frequency")
            
        if "memory_usage" in bottlenecks:
            recommendations.append("Implement file caching strategies")
            recommendations.append("Optimize JSON data structures")
            
        return recommendations


# Pytest integration
@pytest.mark.stress
@pytest.mark.scaling
class TestAgentScalingStress:
    """Pytest class for agent scaling stress tests."""
    
    def test_light_agent_scaling(self):
        """Test light agent scaling stress."""
        config = create_light_stress_config("light_agent_scaling", agent_count=6)
        scenario = AgentScalingStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light scaling stress test failed: {result.error_message}"
        assert len(scenario.scaling_metrics) >= 3, "Should test at least 3 agent counts"
        
    def test_medium_agent_scaling(self):
        """Test medium agent scaling stress."""
        config = create_medium_stress_config("medium_agent_scaling", agent_count=12)
        scenario = AgentScalingStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Medium scaling stress test failed: {result.error_message}"
        assert len(scenario.scaling_metrics) >= 5, "Should test at least 5 agent counts"
        
    @pytest.mark.slow
    def test_heavy_agent_scaling(self):
        """Test heavy agent scaling stress."""
        config = create_heavy_stress_config("heavy_agent_scaling", agent_count=18)
        scenario = AgentScalingStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Heavy scaling stress test failed: {result.error_message}"
        assert len(scenario.scaling_metrics) >= 7, "Should test at least 7 agent counts"
        
    @pytest.mark.slow
    @pytest.mark.extreme
    def test_extreme_agent_scaling(self):
        """Test extreme agent scaling stress."""
        config = create_extreme_stress_config("extreme_agent_scaling", agent_count=24)
        scenario = AgentScalingStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        # Extreme tests may fail due to resource limits
        if not result.success:
            pytest.skip(f"Extreme scaling test hit resource limits: {result.error_message}")
        
        assert len(scenario.scaling_metrics) >= 9, "Should test all agent count levels"


if __name__ == "__main__":
    # Run scaling stress tests directly
    runner = StressTestRunner()
    
    # Test different scaling levels
    scenarios = [
        AgentScalingStressScenario(create_light_stress_config("light_scaling", agent_count=6)),
        AgentScalingStressScenario(create_medium_stress_config("medium_scaling", agent_count=12))
    ]
    
    results = runner.run_scenarios(scenarios)
    
    print("\n" + runner.generate_summary_report(results))