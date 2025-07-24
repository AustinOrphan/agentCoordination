"""
Test Configuration Module

Provides configuration management for coordination system testing.
"""

from .test_config import (
    TestMode,
    TestSuite,
    TestConfig,
    CoordinationSystemConfig,
    TestExecutionConfig,
    TestConfigManager,
    config_manager,
    get_test_config,
    setup_test_environment
)

__all__ = [
    'TestMode',
    'TestSuite', 
    'TestConfig',
    'CoordinationSystemConfig',
    'TestExecutionConfig',
    'TestConfigManager',
    'config_manager',
    'get_test_config',
    'setup_test_environment'
]