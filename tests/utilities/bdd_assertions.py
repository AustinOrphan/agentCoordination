"""
Custom Assertion Helpers for BDD Tests

This module provides specialized assertion helpers tailored for BDD edge case testing
in the multi-agent coordination system. These assertions provide clear, descriptive
error messages and integrate with the BDD reporting system.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import pytest

from .scenario_validators import ScenarioValidationResult
from .bdd_test_reporter import add_validation_result


class AssertionLevel(Enum):
    """Assertion severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AssertionContext:
    """Context information for assertions."""
    scenario_name: str
    step_name: str
    agent_id: Optional[str] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class BDDAssertionError(AssertionError):
    """Custom assertion error with enhanced context."""
    
    def __init__(self, message: str, context: AssertionContext, level: AssertionLevel = AssertionLevel.ERROR):
        self.context = context
        self.level = level
        super().__init__(self._format_message(message))
        
    def _format_message(self, message: str) -> str:
        """Format assertion error message with context."""
        formatted = f"\n🔍 BDD Assertion Failed ({self.level.value.upper()})\n"
        formatted += f"📝 Scenario: {self.context.scenario_name}\n"
        formatted += f"🎯 Step: {self.context.step_name}\n"
        
        if self.context.agent_id:
            formatted += f"🤖 Agent: {self.context.agent_id}\n"
            
        if self.context.timestamp:
            formatted += f"⏰ Time: {self.context.timestamp}\n"
            
        formatted += f"❌ Error: {message}\n"
        
        if self.context.additional_data:
            formatted += f"📊 Additional Data: {json.dumps(self.context.additional_data, indent=2)}\n"
            
        return formatted


class BDDAssertions:
    """Main assertion helper class for BDD tests."""
    
    def __init__(self, context: AssertionContext):
        self.context = context
        
    @contextmanager
    def soft_assertions(self):
        """Context manager for soft assertions that collect errors without failing immediately."""
        errors = []
        original_assert = self._assert_with_context
        
        def soft_assert(condition, message, level=AssertionLevel.ERROR, **kwargs):
            if not condition:
                error = BDDAssertionError(message, self.context, level)
                errors.append(error)
                return False
            return True
            
        self._assert_with_context = soft_assert
        
        try:
            yield soft_assert
        finally:
            self._assert_with_context = original_assert
            if errors:
                combined_message = "\n".join(str(error) for error in errors)
                raise BDDAssertionError(f"Multiple soft assertions failed:\n{combined_message}", self.context)
    
    def _assert_with_context(self, condition: bool, message: str, level: AssertionLevel = AssertionLevel.ERROR, **kwargs):
        """Base assertion method with context."""
        if not condition:
            raise BDDAssertionError(message, self.context, level)
        return True
    
    # Agent Status Assertions
    def assert_agent_status(self, agent_data: Dict[str, Any], expected_status: str):
        """Assert agent has expected status."""
        actual_status = agent_data.get('status', 'unknown')
        self._assert_with_context(
            actual_status == expected_status,
            f"Agent status mismatch. Expected: {expected_status}, Actual: {actual_status}",
            additional_data={'agent_data': agent_data}
        )
        
    def assert_agent_exists(self, agent_id: str, agent_list: List[Dict[str, Any]]):
        """Assert agent exists in the system."""
        agent_ids = [agent.get('id', agent.get('name', '')) for agent in agent_list]
        self._assert_with_context(
            agent_id in agent_ids,
            f"Agent {agent_id} not found in system. Available agents: {agent_ids}",
            additional_data={'available_agents': agent_ids}
        )
        
    def assert_agent_workload(self, agent_data: Dict[str, Any], max_tasks: int):
        """Assert agent workload is within acceptable limits."""
        tasks = agent_data.get('current_tasks', [])
        task_count = len(tasks)
        self._assert_with_context(
            task_count <= max_tasks,
            f"Agent workload exceeded. Current: {task_count}, Max: {max_tasks}",
            additional_data={'tasks': tasks}
        )
    
    # Authority Assertions
    def assert_authority_assignment(self, agent_id: str, authority_type: str, authority_pool: Dict[str, Any]):
        """Assert agent has specific authority assignment."""
        current_holder = authority_pool.get('authorities', {}).get(authority_type, {}).get('current_holder')
        self._assert_with_context(
            current_holder == agent_id,
            f"Authority assignment mismatch for {authority_type}. Expected: {agent_id}, Actual: {current_holder}",
            additional_data={'authority_pool': authority_pool}
        )
        
    def assert_authority_request_pending(self, agent_id: str, authority_type: str, authority_pool: Dict[str, Any]):
        """Assert authority request is pending."""
        pending_requests = authority_pool.get('pending_requests', [])
        matching_request = next(
            (req for req in pending_requests 
             if req.get('requester_id') == agent_id and req.get('authority_type') == authority_type),
            None
        )
        self._assert_with_context(
            matching_request is not None,
            f"No pending authority request found for agent {agent_id} requesting {authority_type}",
            additional_data={'pending_requests': pending_requests}
        )
        
    def assert_authority_backup_assigned(self, authority_type: str, authority_pool: Dict[str, Any]):
        """Assert authority has backup assigned."""
        authority_data = authority_pool.get('authorities', {}).get(authority_type, {})
        backup = authority_data.get('backup_holder')
        self._assert_with_context(
            backup is not None,
            f"No backup assigned for authority {authority_type}",
            additional_data={'authority_data': authority_data}
        )
    
    # Conflict Resolution Assertions
    def assert_conflict_detected(self, conflict_id: str, conflict_database: Dict[str, Any]):
        """Assert conflict is properly detected and recorded."""
        conflicts = conflict_database.get('conflicts', {})
        self._assert_with_context(
            conflict_id in conflicts,
            f"Conflict {conflict_id} not found in database",
            additional_data={'available_conflicts': list(conflicts.keys())}
        )
        
    def assert_conflict_resolution_applied(self, conflict_id: str, conflict_database: Dict[str, Any]):
        """Assert conflict resolution has been applied."""
        conflict = conflict_database.get('conflicts', {}).get(conflict_id, {})
        resolution = conflict.get('resolution')
        self._assert_with_context(
            resolution is not None and resolution.get('status') == 'applied',
            f"Conflict {conflict_id} resolution not applied. Current status: {resolution.get('status') if resolution else 'None'}",
            additional_data={'conflict': conflict}
        )
        
    def assert_conflict_priority(self, conflict_id: str, expected_priority: str, conflict_database: Dict[str, Any]):
        """Assert conflict has expected priority level."""
        conflict = conflict_database.get('conflicts', {}).get(conflict_id, {})
        actual_priority = conflict.get('priority', 'unknown')
        self._assert_with_context(
            actual_priority == expected_priority,
            f"Conflict {conflict_id} priority mismatch. Expected: {expected_priority}, Actual: {actual_priority}",
            additional_data={'conflict': conflict}
        )
    
    # Communication Assertions
    def assert_message_delivered(self, message_id: str, recipient: str, communication_log: List[Dict[str, Any]]):
        """Assert message was successfully delivered."""
        delivered_messages = [
            msg for msg in communication_log 
            if msg.get('id') == message_id and msg.get('recipient') == recipient and msg.get('status') == 'delivered'
        ]
        self._assert_with_context(
            len(delivered_messages) > 0,
            f"Message {message_id} not delivered to {recipient}",
            additional_data={'communication_log': communication_log}
        )
        
    def assert_message_ordering(self, messages: List[Dict[str, Any]], expected_order: List[str]):
        """Assert messages are in expected order."""
        actual_order = [msg.get('id', '') for msg in messages]
        self._assert_with_context(
            actual_order == expected_order,
            f"Message ordering incorrect. Expected: {expected_order}, Actual: {actual_order}",
            additional_data={'messages': messages}
        )
        
    def assert_communication_channel_active(self, agent_id: str, channel_status: Dict[str, Any]):
        """Assert communication channel is active for agent."""
        agent_channel = channel_status.get(agent_id, {})
        status = agent_channel.get('status', 'inactive')
        self._assert_with_context(
            status == 'active',
            f"Communication channel for {agent_id} not active. Status: {status}",
            additional_data={'channel_status': channel_status}
        )
    
    # Load Balancing Assertions
    def assert_load_balanced(self, agents: List[Dict[str, Any]], tolerance: float = 0.2):
        """Assert workload is balanced across agents."""
        if len(agents) < 2:
            return  # Cannot balance with fewer than 2 agents
            
        workloads = [len(agent.get('current_tasks', [])) for agent in agents]
        avg_workload = sum(workloads) / len(workloads)
        max_deviation = max(abs(workload - avg_workload) for workload in workloads)
        max_allowed_deviation = avg_workload * tolerance
        
        self._assert_with_context(
            max_deviation <= max_allowed_deviation,
            f"Load imbalance detected. Max deviation: {max_deviation:.2f}, Allowed: {max_allowed_deviation:.2f}",
            additional_data={'workloads': workloads, 'agents': [a.get('id', 'unknown') for a in agents]}
        )
        
    def assert_task_distribution_strategy(self, strategy_name: str, current_strategy: Dict[str, Any]):
        """Assert current task distribution strategy."""
        actual_strategy = current_strategy.get('name', 'unknown')
        self._assert_with_context(
            actual_strategy == strategy_name,
            f"Task distribution strategy mismatch. Expected: {strategy_name}, Actual: {actual_strategy}",
            additional_data={'current_strategy': current_strategy}
        )
    
    # Performance Assertions
    def assert_response_time(self, operation_time: float, max_time: float, operation_name: str = "operation"):
        """Assert operation completed within expected time."""
        self._assert_with_context(
            operation_time <= max_time,
            f"{operation_name} took too long. Actual: {operation_time:.3f}s, Max: {max_time:.3f}s",
            level=AssertionLevel.WARNING,
            additional_data={'operation_time': operation_time, 'max_time': max_time}
        )
        
    def assert_resource_usage(self, usage_data: Dict[str, float], limits: Dict[str, float]):
        """Assert resource usage is within limits."""
        for resource, usage in usage_data.items():
            limit = limits.get(resource)
            if limit is not None:
                self._assert_with_context(
                    usage <= limit,
                    f"{resource} usage exceeded limit. Usage: {usage:.2f}, Limit: {limit:.2f}",
                    level=AssertionLevel.WARNING,
                    additional_data={'usage_data': usage_data, 'limits': limits}
                )
    
    # Data Integrity Assertions
    def assert_json_structure(self, data: Dict[str, Any], required_fields: List[str]):
        """Assert JSON data has required structure."""
        missing_fields = [field for field in required_fields if field not in data]
        self._assert_with_context(
            len(missing_fields) == 0,
            f"Missing required fields: {missing_fields}",
            additional_data={'data': data, 'required_fields': required_fields}
        )
        
    def assert_data_consistency(self, data1: Dict[str, Any], data2: Dict[str, Any], key_path: str):
        """Assert data consistency between two sources."""
        def get_nested_value(data, path):
            keys = path.split('.')
            value = data
            for key in keys:
                value = value.get(key, {})
            return value
            
        value1 = get_nested_value(data1, key_path)
        value2 = get_nested_value(data2, key_path)
        
        self._assert_with_context(
            value1 == value2,
            f"Data inconsistency at {key_path}. Source 1: {value1}, Source 2: {value2}",
            additional_data={'data1': data1, 'data2': data2, 'key_path': key_path}
        )
    
    # State Transition Assertions
    def assert_state_transition(self, previous_state: str, current_state: str, valid_transitions: Dict[str, List[str]]):
        """Assert state transition is valid."""
        allowed_transitions = valid_transitions.get(previous_state, [])
        self._assert_with_context(
            current_state in allowed_transitions,
            f"Invalid state transition from {previous_state} to {current_state}. Allowed: {allowed_transitions}",
            additional_data={'valid_transitions': valid_transitions}
        )
        
    def assert_system_stability(self, metrics: Dict[str, float], stability_thresholds: Dict[str, float]):
        """Assert system is in stable state."""
        unstable_metrics = []
        for metric, value in metrics.items():
            threshold = stability_thresholds.get(metric)
            if threshold is not None and value > threshold:
                unstable_metrics.append((metric, value, threshold))
                
        self._assert_with_context(
            len(unstable_metrics) == 0,
            f"System instability detected: {unstable_metrics}",
            level=AssertionLevel.CRITICAL,
            additional_data={'metrics': metrics, 'thresholds': stability_thresholds}
        )


# Utility functions for creating assertion contexts
def create_assertion_context(scenario_name: str, step_name: str, **kwargs) -> AssertionContext:
    """Create assertion context for BDD tests."""
    return AssertionContext(
        scenario_name=scenario_name,
        step_name=step_name,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
        **kwargs
    )


def bdd_assert(scenario_name: str, step_name: str, **context_kwargs) -> BDDAssertions:
    """Create BDD assertion helper with context."""
    context = create_assertion_context(scenario_name, step_name, **context_kwargs)
    return BDDAssertions(context)


# Pytest integration functions
def pytest_bdd_assert(request, scenario_name: str = None, step_name: str = None) -> BDDAssertions:
    """Create BDD assertions integrated with pytest."""
    if scenario_name is None:
        scenario_name = getattr(request.node, 'scenario_name', request.node.name)
    if step_name is None:
        step_name = getattr(request.node, 'step_name', 'Unknown Step')
        
    context = create_assertion_context(scenario_name, step_name)
    assertions = BDDAssertions(context)
    
    # Hook into pytest for validation reporting
    original_assert = assertions._assert_with_context
    
    def tracked_assert(condition, message, level=AssertionLevel.ERROR, **kwargs):
        result = original_assert(condition, message, level, **kwargs)
        if hasattr(request.node, '_bdd_validations'):
            request.node._bdd_validations.append({
                'condition': condition,
                'message': message,
                'level': level.value,
                'passed': condition
            })
        return result
        
    assertions._assert_with_context = tracked_assert
    return assertions


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    context = create_assertion_context("Authority Edge Cases", "Agent requests authority")
    assertions = BDDAssertions(context)
    
    # Mock data for demonstration
    agent_data = {"id": "alpha", "status": "active", "current_tasks": ["task1", "task2"]}
    authority_pool = {
        "authorities": {
            "critical_path": {"current_holder": "alpha", "backup_holder": "beta"}
        }
    }
    
    try:
        assertions.assert_agent_status(agent_data, "active")
        assertions.assert_authority_assignment("alpha", "critical_path", authority_pool)
        print("All assertions passed!")
    except BDDAssertionError as e:
        print(f"Assertion failed: {e}")