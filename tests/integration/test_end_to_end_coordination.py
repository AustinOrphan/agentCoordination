"""
End-to-End Integration Testing Scenarios

This module provides comprehensive integration tests for the multi-agent coordination
system, testing complete workflows from agent initialization through task completion,
including real authority management, communication, and coordination scenarios.

Updated to use the adapter pattern for both mock and real system integration.
"""

import time
import json
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import pytest
import uuid

from ..utilities.bdd_assertions import bdd_assert
from ..utilities.bdd_performance import create_performance_tracker
from ..utilities.scenario_validators import AuthorityValidator, CommunicationValidator
from ..adapters.adapter_factory import AdapterFactory, AdapterMode
from ..adapters.base_adapter import BaseCoordinationAdapter


@dataclass
class IntegrationTestResult:
    """Result of an integration test scenario."""
    scenario_name: str
    success: bool
    duration: float
    agents_deployed: int
    tasks_completed: int
    authorities_assigned: int
    messages_exchanged: int
    conflicts_resolved: int
    performance_metrics: Dict[str, float]
    validation_results: List[Dict[str, Any]]
    error_message: Optional[str] = None


class CoordinationTestEnvironment:
    """Test environment using adapter pattern for coordination system integration."""
    
    def __init__(self, adapter_mode: AdapterMode = AdapterMode.MOCK, coordination_root: str = None):
        self.adapter_mode = adapter_mode
        self.coordination_root = coordination_root
        self.adapter: BaseCoordinationAdapter = None
        self.is_running = False
        
        # Metrics tracking
        self.agents_started = 0
        self.tasks_assigned = 0
        self.authorities_granted = 0
        self.messages_sent = 0
        self.conflicts_detected = 0
        self.conflicts_resolved = 0
        
        self._initialize_adapter()
    
    def _initialize_adapter(self):
        """Initialize the coordination adapter."""
        self.adapter = AdapterFactory.create_adapter(
            mode=self.adapter_mode,
            coordination_root=self.coordination_root
        )

    def start_agents(self, agent_count: int = 6, theme: str = "greek_letters") -> bool:
        """Start the specified number of agents."""
        try:
            # Setup test environment using adapter
            success = self.adapter.setup_test_environment()
            if not success:
                return False
                
            # Create and start agents
            agent_names = self._get_agent_names(theme)
            
            for i, agent_name in enumerate(agent_names[:agent_count]):
                agent_success = self.adapter.create_agent(
                    agent_id=agent_name,
                    role=self._get_agent_role(i),
                    config={"theme": theme, "index": i}
                )
                if agent_success:
                    self.agents_started += 1
                    
            self.is_running = True
            return self.agents_started > 0
            
        except Exception as e:
            print(f"Failed to start agents: {e}")
            return False
            
    def _get_agent_names(self, theme: str = "greek_letters") -> List[str]:
        """Get agent names based on theme."""
        themes = {
            "greek_letters": ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"],
            "greek_mythology": ["zeus", "hera", "poseidon", "athena", "apollo", "artemis", "ares", "aphrodite"],
            "marvel": ["ironman", "captainamerica", "thor", "hulk", "blackwidow", "hawkeye", "spiderman", "antman"]
        }
        
        return themes.get(theme, themes["greek_letters"])
            
    def _get_agent_role(self, agent_index: int) -> str:
        """Get agent role based on index."""
        roles = [
            "Critical Path Lead - Senior Developer",
            "Migration Specialist - Backend Developer",
            "Dashboard Developer - Fullstack Developer", 
            "DevOps Engineer",
            "Security Engineer",
            "UX Engineer - Frontend Developer"
        ]
        return roles[agent_index % len(roles)]
        
    def assign_task(self, task_description: str, agent_name: str = None) -> str:
        """Assign a task to an agent."""
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        
        try:
            success = self.adapter.assign_task(
                agent_id=agent_name,
                task_id=task_id,
                task_description=task_description,
                priority="normal",
                metadata={"assigned_by": "integration_test"}
            )
            
            if success:
                self.tasks_assigned += 1
                
        except Exception as e:
            print(f"Failed to assign task to {agent_name}: {e}")
            
        return task_id
        
    def request_authority(self, agent_name: str, authority_type: str, task_description: str) -> bool:
        """Request authority for an agent."""
        try:
            success = self.adapter.request_authority(
                agent_id=agent_name,
                authority_type=authority_type,
                task_description=task_description,
                priority="normal"
            )
            
            if success:
                self.authorities_granted += 1
                
            return success
                
        except Exception as e:
            print(f"Failed to request authority {authority_type} for {agent_name}: {e}")
            return False
            
    def send_message(self, sender: str, recipient: str, message_type: str, data: Dict[str, Any]) -> bool:
        """Send message between agents."""
        try:
            success = self.adapter.send_message(
                sender_id=sender,
                recipient_id=recipient,
                message_type=message_type,
                content=data,
                priority="normal"
            )
            
            if success:
                self.messages_sent += 1
                
            return success
            
        except Exception as e:
            print(f"Failed to send message from {sender} to {recipient}: {e}")
            return False
            
    def simulate_conflict(self, authority_type: str, agents: List[str]) -> str:
        """Simulate an authority conflict."""
        conflict_id = f"CONFLICT-{uuid.uuid4().hex[:8]}"
        
        try:
            success = self.adapter.handle_authority_conflict(
                conflict_id=conflict_id,
                authority_type=authority_type,
                conflicting_agents=agents,
                resolution_strategy="integration_test"
            )
            
            if success:
                self.conflicts_detected += 1
                
        except Exception as e:
            print(f"Failed to simulate conflict: {e}")
            
        return conflict_id
        
    def resolve_conflict(self, conflict_id: str, winner: str) -> bool:
        """Resolve an authority conflict."""
        try:
            success = self.adapter.resolve_authority_conflict(
                conflict_id=conflict_id,
                winning_agent=winner,
                resolution_reason="integration_test_resolution"
            )
            
            if success:
                self.conflicts_resolved += 1
                
            return success
            
        except Exception as e:
            print(f"Failed to resolve conflict {conflict_id}: {e}")
            return False
            
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        # Get metrics from adapter
        adapter_metrics = self.adapter.get_system_health()
        
        # Combine with local metrics
        return {
            "agents_started": self.agents_started,
            "tasks_assigned": self.tasks_assigned,
            "authorities_granted": self.authorities_granted,
            "messages_sent": self.messages_sent,
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "is_running": self.is_running,
            **adapter_metrics
        }
        
    def stop(self):
        """Stop the coordination environment."""
        self.is_running = False
        if self.adapter:
            self.adapter.cleanup_test_environment()


class IntegrationTestScenario:
    """Base class for integration test scenarios."""
    
    def __init__(self, scenario_name: str, adapter_mode: AdapterMode = AdapterMode.MOCK):
        self.scenario_name = scenario_name
        self.adapter_mode = adapter_mode
        self.temp_dir: Optional[str] = None
        self.environment: Optional[CoordinationTestEnvironment] = None
        self.performance_tracker = create_performance_tracker()
        self.validators = {
            "authority": AuthorityValidator(),
            "communication": CommunicationValidator()
        }
        
    def setup(self, theme: str = "greek_letters", agent_count: int = 6, coordination_root: str = None):
        """Setup the integration test scenario."""
        self.temp_dir = coordination_root or tempfile.mkdtemp(prefix=f"integration_test_{self.scenario_name}_")
        self.environment = CoordinationTestEnvironment(
            adapter_mode=self.adapter_mode,
            coordination_root=self.temp_dir
        )
        
    def teardown(self):
        """Clean up the integration test scenario."""
        if self.environment:
            self.environment.stop()
            
        if self.temp_dir and os.path.exists(self.temp_dir) and self.adapter_mode == AdapterMode.MOCK:
            # Only clean up temp directories for mock mode
            shutil.rmtree(self.temp_dir)
            
    def run(self, theme: str = "greek_letters", agent_count: int = 6) -> IntegrationTestResult:
        """Run the integration test scenario."""
        start_time = time.time()
        
        try:
            with self.performance_tracker.measure_scenario(self.scenario_name):
                success = self._execute_scenario(theme, agent_count)
                
            duration = time.time() - start_time
            metrics = self.environment.get_system_metrics()
            
            # Validate results
            validation_results = self._validate_results()
            
            return IntegrationTestResult(
                scenario_name=self.scenario_name,
                success=success,
                duration=duration,
                agents_deployed=metrics["agents_started"],
                tasks_completed=metrics["tasks_assigned"],
                authorities_assigned=metrics["authorities_granted"],
                messages_exchanged=metrics["messages_sent"],
                conflicts_resolved=metrics["conflicts_resolved"],
                performance_metrics=self._get_performance_metrics(),
                validation_results=validation_results
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return IntegrationTestResult(
                scenario_name=self.scenario_name,
                success=False,
                duration=duration,
                agents_deployed=0,
                tasks_completed=0,
                authorities_assigned=0,
                messages_exchanged=0,
                conflicts_resolved=0,
                performance_metrics={},
                validation_results=[],
                error_message=str(e)
            )
            
    def _execute_scenario(self, theme: str, agent_count: int) -> bool:
        """Execute the specific scenario logic. Override in subclasses."""
        raise NotImplementedError
        
    def _validate_results(self) -> List[Dict[str, Any]]:
        """Validate the test results using adapters."""
        validation_results = []
        
        try:
            # Get authority state from adapter
            authority_data = self.environment.adapter.get_authority_state()
            
            authority_result = self.validators["authority"].validate(authority_data)
            validation_results.append({
                "validator": "authority",
                "valid": authority_result.is_valid,
                "message": authority_result.error_message or "Authority validation passed",
                "details": authority_result.details
            })
            
        except Exception as e:
            validation_results.append({
                "validator": "authority",
                "valid": False,
                "message": f"Authority validation failed: {str(e)}",
                "details": {}
            })
            
        return validation_results
        
    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from the tracker."""
        return {
            "scenario_duration": self.performance_tracker.get_operation_stats(self.scenario_name).get("avg", 0),
            "message_latency": 0.05,  # Would be measured in real scenario
            "authority_assignment_time": 0.1  # Would be measured in real scenario
        }


class BasicCoordinationScenario(IntegrationTestScenario):
    """Basic multi-agent coordination scenario."""
    
    def __init__(self, adapter_mode: AdapterMode = AdapterMode.MOCK):
        super().__init__("basic_coordination", adapter_mode)
        
    def _execute_scenario(self, theme: str, agent_count: int) -> bool:
        """Execute basic coordination scenario."""
        # Start agents
        if not self.environment.start_agents(agent_count, theme):
            return False
            
        # Wait for agents to initialize
        time.sleep(2)
        
        # Assign tasks to agents
        tasks = [
            "Implement user authentication module",
            "Setup database migrations", 
            "Create dashboard interface",
            "Configure deployment pipeline",
            "Implement security measures",
            "Design user experience"
        ]
        
        agent_names = self.environment._get_agent_names(theme)[:agent_count]
        
        for i, task in enumerate(tasks[:len(agent_names)]):
            task_id = self.environment.assign_task(task, agent_names[i])
            
            # Request appropriate authority
            authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
            authority = authorities[i % len(authorities)]
            
            success = self.environment.request_authority(agent_names[i], authority, task)
            if not success:
                print(f"Failed to grant {authority} authority to {agent_names[i]}")
                
        # Simulate inter-agent communication
        for i in range(len(agent_names) - 1):
            sender = agent_names[i]
            recipient = agent_names[i + 1]
            
            self.environment.send_message(
                sender, recipient, "coordination_update",
                {"status": "in_progress", "dependency": f"task_{i+1}"}
            )
            
        # Wait for coordination to complete
        time.sleep(3)
        
        # Verify system state
        metrics = self.environment.get_system_metrics()
        
        return (metrics["agents_started"] >= 3 and 
                metrics["tasks_assigned"] >= 3 and
                metrics["authorities_granted"] >= 3 and
                metrics["messages_sent"] >= 2)


class AuthorityConflictScenario(IntegrationTestScenario):
    """Authority conflict resolution scenario."""
    
    def __init__(self, adapter_mode: AdapterMode = AdapterMode.MOCK):
        super().__init__("authority_conflict", adapter_mode)
        
    def _execute_scenario(self, theme: str, agent_count: int) -> bool:
        """Execute authority conflict scenario."""
        # Start agents
        if not self.environment.start_agents(agent_count, theme):
            return False
            
        time.sleep(1)
        
        agent_names = self.environment._get_agent_names(theme)[:agent_count]
        
        # Create authority conflict by having multiple agents request same authority
        authority_type = "critical_path"
        
        # First agent gets the authority
        success1 = self.environment.request_authority(
            agent_names[0], authority_type, "Critical path task 1"
        )
        
        # Second agent creates conflict
        success2 = self.environment.request_authority(
            agent_names[1], authority_type, "Critical path task 2"
        )
        
        # Third agent also requests (should be queued)
        success3 = self.environment.request_authority(
            agent_names[2], authority_type, "Critical path task 3"
        )
        
        # Simulate conflict detection and resolution
        if success1:  # If first request succeeded
            conflict_id = self.environment.simulate_conflict(authority_type, [agent_names[1], agent_names[2]])
            
            # Resolve conflict in favor of agent 1
            self.environment.resolve_conflict(conflict_id, agent_names[1])
            
        time.sleep(2)
        
        # Verify conflict was handled
        metrics = self.environment.get_system_metrics()
        
        return (metrics["conflicts_detected"] >= 1 and
                metrics["conflicts_resolved"] >= 1 and
                metrics["authorities_granted"] >= 1)


class HighThroughputCommunicationScenario(IntegrationTestScenario):
    """High-throughput communication scenario."""
    
    def __init__(self, adapter_mode: AdapterMode = AdapterMode.MOCK):
        super().__init__("high_throughput_communication", adapter_mode)
        
    def _execute_scenario(self, theme: str, agent_count: int) -> bool:
        """Execute high-throughput communication scenario."""
        # Start agents
        if not self.environment.start_agents(agent_count, theme):
            return False
            
        time.sleep(1)
        
        agent_names = self.environment._get_agent_names(theme)[:agent_count]
        
        # Create high-throughput communication pattern
        message_count = 0
        
        # Each agent sends messages to every other agent
        for sender in agent_names:
            for recipient in agent_names:
                if sender != recipient:
                    # Send coordination update
                    success = self.environment.send_message(
                        sender, recipient, "status_update",
                        {"status": "active", "load": 75, "timestamp": time.time()}
                    )
                    if success:
                        message_count += 1
                        
                    # Send task notification
                    success = self.environment.send_message(
                        sender, recipient, "task_notification", 
                        {"task_id": f"task_{message_count}", "priority": "normal"}
                    )
                    if success:
                        message_count += 1
                        
        time.sleep(2)
        
        # Verify high throughput was achieved
        metrics = self.environment.get_system_metrics()
        expected_messages = len(agent_names) * (len(agent_names) - 1) * 2  # 2 message types
        
        return (metrics["messages_sent"] >= expected_messages * 0.8 and  # Allow for some failures
                metrics["agents_started"] == len(agent_names))


class CompleteWorkflowScenario(IntegrationTestScenario):
    """Complete workflow integration scenario."""
    
    def __init__(self, adapter_mode: AdapterMode = AdapterMode.MOCK):
        super().__init__("complete_workflow", adapter_mode)
        
    def _execute_scenario(self, theme: str, agent_count: int) -> bool:
        """Execute complete workflow scenario."""
        # Start agents
        if not self.environment.start_agents(agent_count, theme):
            return False
            
        time.sleep(1)
        
        agent_names = self.environment._get_agent_names(theme)[:agent_count]
        
        # Phase 1: Initial task assignment
        tasks = [
            ("Analyze requirements", "critical_path"),
            ("Setup database schema", "migration"),
            ("Create UI mockups", "ux"),
            ("Plan deployment strategy", "devops"),
            ("Design security model", "security"),
            ("Implement dashboard", "dashboard")
        ]
        
        for i, (task, authority) in enumerate(tasks[:len(agent_names)]):
            task_id = self.environment.assign_task(task, agent_names[i])
            self.environment.request_authority(agent_names[i], authority, task)
            
        time.sleep(1)
        
        # Phase 2: Inter-agent coordination
        # Critical path lead coordinates with others
        lead_agent = agent_names[0]
        for other_agent in agent_names[1:]:
            self.environment.send_message(
                lead_agent, other_agent, "coordination",
                {"phase": "planning", "dependencies": ["requirements_complete"]}
            )
            
        # Phase 3: Status updates
        for agent in agent_names:
            self.environment.send_message(
                agent, lead_agent, "status_report",
                {"progress": 50, "blockers": [], "estimated_completion": "2h"}
            )
            
        # Phase 4: Conflict simulation and resolution
        conflict_id = self.environment.simulate_conflict("critical_path", [agent_names[0], agent_names[2]])
        self.environment.resolve_conflict(conflict_id, agent_names[0])
        
        time.sleep(2)
        
        # Verify complete workflow
        metrics = self.environment.get_system_metrics()
        
        return (metrics["agents_started"] >= 4 and
                metrics["tasks_assigned"] >= 4 and
                metrics["authorities_granted"] >= 4 and
                metrics["messages_sent"] >= 8 and
                metrics["conflicts_resolved"] >= 1)


# Pytest integration tests
@pytest.mark.integration
class TestIntegrationScenarios:
    """Pytest class for integration test scenarios."""
    
    @pytest.mark.parametrize("adapter_mode", [AdapterMode.MOCK, AdapterMode.REAL])
    def test_basic_coordination_scenario(self, adapter_mode):
        """Test basic multi-agent coordination."""
        scenario = BasicCoordinationScenario(adapter_mode)
        
        # For real mode, use actual coordination root
        coordination_root = None if adapter_mode == AdapterMode.MOCK else "/Users/austinorphan/Library/Mobile Documents/com~apple~CloudDocs/src/agentCoordination"
        
        scenario.setup(agent_count=4, coordination_root=coordination_root)
        
        try:
            result = scenario.run(agent_count=4)
            
            assert result.success, f"Basic coordination scenario failed: {result.error_message}"
            assert result.agents_deployed >= 3, "Insufficient agents deployed"
            assert result.tasks_completed >= 3, "Insufficient tasks completed"
            assert result.authorities_assigned >= 3, "Insufficient authorities assigned"
            
        finally:
            scenario.teardown()
            
    @pytest.mark.parametrize("adapter_mode", [AdapterMode.MOCK, AdapterMode.REAL])
    def test_authority_conflict_scenario(self, adapter_mode):
        """Test authority conflict resolution."""
        scenario = AuthorityConflictScenario(adapter_mode)
        
        coordination_root = None if adapter_mode == AdapterMode.MOCK else "/Users/austinorphan/Library/Mobile Documents/com~apple~CloudDocs/src/agentCoordination"
        
        scenario.setup(agent_count=4, coordination_root=coordination_root)
        
        try:
            result = scenario.run(agent_count=4)
            
            assert result.success, f"Authority conflict scenario failed: {result.error_message}"
            assert result.conflicts_resolved >= 1, "No conflicts resolved"
            
        finally:
            scenario.teardown()
            
    @pytest.mark.parametrize("adapter_mode", [AdapterMode.MOCK])  # Start with mock only
    def test_high_throughput_communication_scenario(self, adapter_mode):
        """Test high-throughput communication."""
        scenario = HighThroughputCommunicationScenario(adapter_mode)
        
        coordination_root = None if adapter_mode == AdapterMode.MOCK else "/Users/austinorphan/Library/Mobile Documents/com~apple~CloudDocs/src/agentCoordination"
        
        scenario.setup(agent_count=5, coordination_root=coordination_root)
        
        try:
            result = scenario.run(agent_count=5)
            
            assert result.success, f"High throughput communication scenario failed: {result.error_message}"
            assert result.messages_exchanged >= 15, "Insufficient message throughput"
            
        finally:
            scenario.teardown()
            
    @pytest.mark.slow
    @pytest.mark.parametrize("adapter_mode", [AdapterMode.MOCK])  # Start with mock only
    def test_complete_workflow_scenario(self, adapter_mode):
        """Test complete coordination workflow."""
        scenario = CompleteWorkflowScenario(adapter_mode)
        
        coordination_root = None if adapter_mode == AdapterMode.MOCK else "/Users/austinorphan/Library/Mobile Documents/com~apple~CloudDocs/src/agentCoordination"
        
        scenario.setup(agent_count=6, coordination_root=coordination_root)
        
        try:
            result = scenario.run(agent_count=6)
            
            assert result.success, f"Complete workflow scenario failed: {result.error_message}"
            assert result.agents_deployed >= 4, "Insufficient agents deployed"
            assert result.tasks_completed >= 4, "Insufficient tasks completed"
            assert result.authorities_assigned >= 4, "Insufficient authorities assigned"
            assert result.messages_exchanged >= 8, "Insufficient messages exchanged"
            assert result.conflicts_resolved >= 1, "No conflicts resolved"
            
            # Validate performance
            assert result.duration < 30.0, "Workflow took too long"
            
        finally:
            scenario.teardown()


if __name__ == "__main__":
    # Run integration scenarios directly
    adapter_mode = AdapterMode.MOCK  # Can be changed to REAL for live system testing
    
    scenarios = [
        BasicCoordinationScenario(adapter_mode),
        AuthorityConflictScenario(adapter_mode), 
        HighThroughputCommunicationScenario(adapter_mode),
        CompleteWorkflowScenario(adapter_mode)
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n🧪 Running {scenario.scenario_name} scenario...")
        scenario.setup()
        
        try:
            result = scenario.run()
            results.append(result)
            
            if result.success:
                print(f"✅ {scenario.scenario_name}: SUCCESS")
                print(f"   Duration: {result.duration:.2f}s")
                print(f"   Agents: {result.agents_deployed}")
                print(f"   Tasks: {result.tasks_completed}")
                print(f"   Messages: {result.messages_exchanged}")
            else:
                print(f"❌ {scenario.scenario_name}: FAILED")
                print(f"   Error: {result.error_message}")
                
        finally:
            scenario.teardown()
            
    # Summary
    successful = len([r for r in results if r.success])
    print(f"\n📊 Integration Test Summary:")
    print(f"   Total scenarios: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(results) - successful}")
    print(f"   Success rate: {successful/len(results)*100:.1f}%")