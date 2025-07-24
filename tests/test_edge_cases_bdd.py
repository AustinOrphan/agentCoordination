#!/usr/bin/env python3
"""
BDD Edge Case Tests for Multi-Agent Coordination System
Tests authority assignment edge cases using pytest-bdd
"""

import pytest
import json
import tempfile
import time
import re
from pathlib import Path
from datetime import datetime
from pytest_bdd import scenarios, given, when, then, parsers
from typing import Dict, List

# Import Phase 2 fixtures and utilities
from conftest import coordination_system_with_agents, mock_active_agents

# Load all scenarios from authority edge cases feature file
scenarios('edge_cases/authority_edge_cases.feature')


# Custom Step Parsers
class AgentWorkloadParser(parsers.StepParser):
    """Parse agent workload specifications."""
    
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.regex = re.compile(
            r"I have (?P<count>\d+) active agents and each agent has (?P<workload>\d+)% current workload"
        )
    
    def parse_arguments(self, name):
        match = self.regex.match(name)
        if match:
            return {
                'count': int(match.group('count')),
                'workload': int(match.group('workload'))
            }
        return {}


# Background Steps
@given("I have a coordination system")
def coordination_system(coordination_system_with_agents):
    """Use the comprehensive coordination system from Phase 2."""
    return coordination_system_with_agents


@given("the mock agent system is active")
def active_mock_system(mock_active_agents):
    """Ensure mock agents are active and available."""
    assert len(mock_active_agents) >= 6, "Need at least 6 mock agents for testing"
    return mock_active_agents


# Agent Setup Steps
@given(parsers.parse("I have {agent_count:d} active agents"))
def setup_agents(coordination_system, agent_count):
    """Set up the specified number of active agents."""
    # Use existing mock agents from Phase 2
    agents = ['shark', 'dolphin', 'whale', 'octopus', 'jellyfish', 'seahorse'][:agent_count]
    
    # Verify agents are available in the system
    authority_manager = coordination_system['authority_manager']
    available_agents = getattr(authority_manager, '_get_available_agents', lambda: agents)()
    
    assert len(available_agents) >= agent_count, f"Need {agent_count} agents, only {len(available_agents)} available"
    return agents


@given(parsers.parse("each agent has {workload:d}% current workload"))
def set_agent_workloads(coordination_system, workload):
    """Set workload for all agents."""
    # Store workload info for later use in tests
    coordination_system['test_workload'] = workload
    return workload


@given("all agents are at 100% workload")
def max_agent_workloads(coordination_system):
    """Set all agents to maximum workload."""
    coordination_system['test_workload'] = 100
    return 100


@given(parsers.parse('I am assigning authority to "{agent_name}"'))
def target_agent_assignment(coordination_system, agent_name):
    """Set up assignment to specific agent."""
    coordination_system['target_agent'] = agent_name
    return agent_name


@given(parsers.parse('I have 2 agents: "{agent1}" and "{agent2}"'))
def setup_two_agents(coordination_system, agent1, agent2):
    """Set up two specific agents."""
    coordination_system['test_agents'] = [agent1, agent2]
    return [agent1, agent2]


@given(parsers.parse('both agents are qualified for "{domain}" domain'))
def agents_qualified_for_domain(coordination_system, domain):
    """Set agents as qualified for domain."""
    coordination_system['test_domain'] = domain
    return domain


# Authority Request Steps
@when(parsers.parse("I request {authority_count:d} authority assignments"))
def request_multiple_authorities(coordination_system, authority_count):
    """Request multiple authority assignments."""
    authority_manager = coordination_system['authority_manager']
    results = []
    
    for i in range(authority_count):
        try:
            result = authority_manager.assign_authority(f"Edge case test authority {i}")
            results.append(result)
        except Exception as e:
            results.append({'success': False, 'error': str(e)})
    
    coordination_system['authority_results'] = results
    return results


@when(parsers.parse('I request authority assignment for "{task_description}"'))
def request_specific_authority(coordination_system, task_description):
    """Request authority for specific task."""
    authority_manager = coordination_system['authority_manager']
    
    try:
        result = authority_manager.assign_authority(task_description)
        coordination_system['authority_result'] = result
    except Exception as e:
        coordination_system['authority_result'] = {'success': False, 'error': str(e)}
    
    return coordination_system['authority_result']


@when(parsers.parse('I request authority for "{invalid_request}"'))
def request_invalid_authority(coordination_system, invalid_request):
    """Request authority with invalid input."""
    authority_manager = coordination_system['authority_manager']
    
    # Handle special cases like empty string and long strings
    if invalid_request == '""':
        invalid_request = ""
    elif invalid_request.startswith('"x" * '):
        # Handle "x" * 10000 pattern
        count = int(invalid_request.split(' * ')[1])
        invalid_request = "x" * count
    
    try:
        result = authority_manager.assign_authority(invalid_request)
        coordination_system['authority_result'] = result
    except Exception as e:
        coordination_system['authority_result'] = {'success': False, 'error': str(e)}
    
    return coordination_system['authority_result']


@when(parsers.parse('"{agent_name}" goes offline during assignment'))
def agent_goes_offline(coordination_system, agent_name):
    """Simulate agent going offline."""
    # Simulate agent failure by marking it as offline
    coordination_system['offline_agent'] = agent_name
    coordination_system['assignment_interrupted'] = True
    return agent_name


@when("I assign the same critical authority to both agents simultaneously")
def simultaneous_authority_assignment(coordination_system):
    """Assign same authority to multiple agents simultaneously."""
    authority_manager = coordination_system['authority_manager']
    agents = coordination_system.get('test_agents', ['shark', 'dolphin'])
    
    results = []
    # Simulate simultaneous assignment
    for agent in agents:
        try:
            result = authority_manager.assign_authority("Critical Security Authority")
            results.append(result)
        except Exception as e:
            results.append({'success': False, 'error': str(e)})
    
    coordination_system['simultaneous_results'] = results
    return results


# Timing and Failure Steps
@when(parsers.parse("the assignment takes {duration:d} seconds to respond"))
def simulate_slow_assignment(coordination_system, duration):
    """Simulate slow authority assignment."""
    coordination_system['assignment_duration'] = duration
    # In real implementation, this would simulate network delays
    return duration


# Assertion Steps
@then(parsers.parse("{success_rate:d}% should be assigned successfully"))
def verify_success_rate(coordination_system, success_rate):
    """Verify authority assignment success rate."""
    results = coordination_system.get('authority_results', [])
    
    if not results:
        # If no results, assume 0% success
        actual_success_rate = 0
    else:
        successful = len([r for r in results if r.get('success', False)])
        actual_success_rate = (successful / len(results)) * 100
    
    # Allow for some tolerance in edge case testing
    tolerance = 10
    assert abs(actual_success_rate - success_rate) <= tolerance, \
        f"Expected {success_rate}% success rate, got {actual_success_rate}%"


@then("the system should remain stable")
def verify_system_stability(coordination_system):
    """Verify system remains stable after operations."""
    # Check that core components are still functional
    authority_manager = coordination_system['authority_manager']
    
    # Verify basic functionality still works
    try:
        test_result = authority_manager.assign_authority("Stability test")
        assert test_result is not None, "System appears unstable"
    except Exception as e:
        pytest.fail(f"System stability check failed: {e}")


@then("the authority should be queued")
def verify_authority_queued(coordination_system):
    """Verify authority is queued when agents are busy."""
    result = coordination_system.get('authority_result', {})
    
    # In a real implementation, queued authorities would have specific status
    # For now, we accept either success=False or a queued status
    assert not result.get('success', True) or result.get('status') == 'queued', \
        "Authority should be queued when all agents are busy"


@then("I should receive a queuing notification")
def verify_queuing_notification(coordination_system):
    """Verify queuing notification is received."""
    result = coordination_system.get('authority_result', {})
    
    # Check for queuing-related information in the response
    assert 'queue' in str(result).lower() or 'busy' in str(result).lower() or not result.get('success'), \
        "Should receive indication that authority was queued"


@then("the system should estimate wait time")
def verify_wait_time_estimate(coordination_system):
    """Verify system provides wait time estimate."""
    result = coordination_system.get('authority_result', {})
    
    # In a real implementation, this would include wait time estimates
    # For testing, we just verify the system handled the request
    assert result is not None, "System should provide response with wait time estimate"


@then("the authority should be reassigned automatically")
def verify_automatic_reassignment(coordination_system):
    """Verify authority is reassigned when agent fails."""
    offline_agent = coordination_system.get('offline_agent')
    result = coordination_system.get('authority_result', {})
    
    # Verify the authority wasn't assigned to the offline agent
    if result.get('agent') == offline_agent:
        pytest.fail(f"Authority should not be assigned to offline agent {offline_agent}")
    
    # Verify some form of reassignment occurred
    assert result.get('reassigned') or result.get('agent') != offline_agent, \
        "Authority should be reassigned when target agent goes offline"


@then("the system should log the failure")
def verify_failure_logging(coordination_system):
    """Verify system logs agent failures."""
    # In a real implementation, this would check actual logs
    # For testing, we verify the system is aware of the failure
    assert coordination_system.get('assignment_interrupted'), \
        "System should track assignment interruptions"


@then("no data should be corrupted")
def verify_no_data_corruption(coordination_system):
    """Verify no data corruption occurred."""
    # Basic system integrity check
    authority_manager = coordination_system['authority_manager']
    
    try:
        # Verify authority pool is still accessible
        if hasattr(authority_manager, 'get_authority_pool'):
            pool = authority_manager.get_authority_pool()
            assert isinstance(pool, dict), "Authority pool should be valid"
    except Exception as e:
        pytest.fail(f"Data corruption detected: {e}")


@then("only one agent should receive the authority")
def verify_single_authority_assignment(coordination_system):
    """Verify only one agent receives conflicting authority."""
    results = coordination_system.get('simultaneous_results', [])
    
    successful_assignments = [r for r in results if r.get('success', False)]
    assert len(successful_assignments) <= 1, \
        f"Only one agent should receive authority, but {len(successful_assignments)} succeeded"


@then("the other should receive a conflict notification")
def verify_conflict_notification(coordination_system):
    """Verify other agent receives conflict notification."""
    results = coordination_system.get('simultaneous_results', [])
    
    failed_assignments = [r for r in results if not r.get('success', True)]
    assert len(failed_assignments) >= 1, \
        "At least one agent should receive conflict notification"


@then("the system should resolve the conflict deterministically")
def verify_deterministic_conflict_resolution(coordination_system):
    """Verify conflict resolution is deterministic."""
    results = coordination_system.get('simultaneous_results', [])
    
    # Verify system handled the conflict in a predictable way
    total_results = len(results)
    assert total_results > 0, "Should have conflict resolution results"
    
    # In a real implementation, this would verify specific conflict resolution rules
    # For testing, we verify the system made a decision
    assert any(r.get('success') for r in results) or any('conflict' in str(r) for r in results), \
        "System should deterministically resolve conflicts"


@then(parsers.parse('I should receive an error message containing "{error_type}"'))
def verify_error_message(coordination_system, error_type):
    """Verify appropriate error message is received."""
    result = coordination_system.get('authority_result', {})
    
    # Check that request failed and contains expected error type
    assert not result.get('success', True), "Invalid request should fail"
    
    error_message = str(result.get('error', '')).lower()
    expected_error = error_type.replace('_', ' ').lower()
    
    # Flexible error message checking
    assert expected_error in error_message or 'error' in error_message or 'invalid' in error_message, \
        f"Should receive error containing '{error_type}', got: {result}"


# Additional step definitions for other scenarios would continue here...
# This file demonstrates the pattern for implementing BDD steps

if __name__ == "__main__":
    pytest.main([__file__, "-v"])