"""
Test Runner Module

Provides unified test execution capabilities for coordination system testing.
"""

from .test_runner import (
    TestResult,
    CoordinationTestRunner,
    run_coordination_tests
)

__all__ = [
    'TestResult',
    'CoordinationTestRunner', 
    'run_coordination_tests'
]