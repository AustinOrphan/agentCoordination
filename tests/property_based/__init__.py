"""
Property-Based Testing Infrastructure

This package provides property-based testing capabilities for the multi-agent
coordination system using Hypothesis. It includes:

- Stateful property testing with RuleBasedStateMachine
- System invariant verification
- Edge case generation and testing
- Coordination system property validation

Usage:
    pytest tests/property_based/ -v
    
Or run specific property tests:
    python tests/property_based/test_coordination_properties.py
"""

from .test_coordination_properties import (
    CoordinationSystemProperties,
    StatefulCoordinationTesting,
    AgentState,
    AuthorityState,
    CoordinationSystemState
)

__all__ = [
    "CoordinationSystemProperties",
    "StatefulCoordinationTesting", 
    "AgentState",
    "AuthorityState",
    "CoordinationSystemState"
]