"""
System Integration Adapters

This package provides adapters to connect the test suite with both
mock and real coordination systems, enabling flexible testing approaches.

Key Components:
- BaseCoordinationAdapter: Common interface for all adapters
- RealSystemAdapter: Connects to actual coordination system
- MockSystemAdapter: Mock implementation for isolated testing
- AdapterFactory: Factory for creating appropriate adapters

Usage:
    from tests.adapters import AdapterFactory, AdapterMode
    
    # Create real system adapter
    adapter = AdapterFactory.create_adapter(
        AdapterMode.REAL,
        coordination_root="/path/to/coordination/system"
    )
    
    # Or create mock adapter for isolated testing
    adapter = AdapterFactory.create_adapter(AdapterMode.MOCK)
    
    # Use adapter in tests
    with adapter:
        adapter.setup_test_environment()
        # Run tests...
        adapter.cleanup_test_environment()
"""

from .base_adapter import BaseCoordinationAdapter, AdapterConfig, AdapterMode
from .real_system_adapter import RealSystemAdapter, RealSystemConfig
from .mock_system_adapter import MockSystemAdapter, MockSystemConfig
from .adapter_factory import AdapterFactory

__all__ = [
    "BaseCoordinationAdapter",
    "AdapterConfig", 
    "AdapterMode",
    "RealSystemAdapter",
    "RealSystemConfig",
    "MockSystemAdapter", 
    "MockSystemConfig",
    "AdapterFactory"
]