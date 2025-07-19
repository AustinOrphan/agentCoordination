#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path for all tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "coordination_system"))


@pytest.fixture(scope="session")
def project_root_path():
    """Provide project root path for tests."""
    return project_root


@pytest.fixture
def temp_test_dir():
    """Create and cleanup temporary directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="agentcoord_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_agent_list():
    """Provide list of mock agents for testing."""
    return ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]


def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as an error handling test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "flaky: mark test as potentially flaky"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark based on file names
        if "test_dynamic_authority" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "test_conflict_resolution" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "test_load_balancer" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        elif "test_end_to_end" in item.fspath.basename:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
        elif "test_performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "test_error_handling" in item.fspath.basename:
            item.add_marker(pytest.mark.error_handling)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup common test environment."""
    # Ensure clean state for each test
    import os
    import logging
    
    # Set test environment
    os.environ['TESTING'] = '1'
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during tests
        format='%(levelname)s: %(message)s'
    )
    
    yield
    
    # Cleanup after test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


# Custom assertions for better test readability
class TestAssertions:
    """Custom assertion helpers for agent coordination tests."""
    
    @staticmethod
    def assert_authority_result_valid(result):
        """Assert that an authority assignment result is valid."""
        assert isinstance(result, dict), "Authority result should be a dictionary"
        assert "success" in result, "Authority result should have 'success' field"
        assert "assigned_agent" in result, "Authority result should have 'assigned_agent' field"
        assert "authority_types" in result, "Authority result should have 'authority_types' field"
        
        if result["success"]:
            assert result["assigned_agent"], "Successful assignment should have an agent"
            assert isinstance(result["authority_types"], list), "Authority types should be a list"
    
    @staticmethod
    def assert_task_assignment_valid(assigned_agent, expected_agents=None):
        """Assert that a task assignment is valid."""
        if assigned_agent is not None:
            if expected_agents:
                assert assigned_agent in expected_agents, f"Agent {assigned_agent} should be in expected agents {expected_agents}"
    
    @staticmethod
    def assert_conflict_id_valid(conflict_id):
        """Assert that a conflict ID is valid."""
        assert conflict_id is not None, "Conflict ID should not be None"
        assert isinstance(conflict_id, str), "Conflict ID should be a string"
        assert conflict_id.startswith("CONF-"), "Conflict ID should start with 'CONF-'"
    
    @staticmethod
    def assert_load_status_valid(load_status):
        """Assert that load status structure is valid."""
        required_fields = ["timestamp", "current_strategy", "total_agents", "agent_loads", "queue_status"]
        for field in required_fields:
            assert field in load_status, f"Load status should have '{field}' field"
        
        assert load_status["total_agents"] > 0, "Should have at least one agent"
        assert isinstance(load_status["agent_loads"], dict), "Agent loads should be a dictionary"


@pytest.fixture
def test_assertions():
    """Provide custom assertion helpers."""
    return TestAssertions


# Performance measurement fixture
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time
    import psutil
    import os
    
    start_time = time.perf_counter()
    start_memory = 0
    
    try:
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        pass
    
    yield
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    end_memory = 0
    try:
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
    except (ImportError, NameError):
        pass
    
    memory_delta = end_memory - start_memory if end_memory > 0 else 0
    
    # Log performance metrics (can be collected by CI/CD)
    print(f"\n📊 Test Performance: {duration:.3f}s, {memory_delta:.2f}MB memory delta")


# Error injection fixture for testing robustness
@pytest.fixture
def error_injector():
    """Inject errors for robustness testing."""
    class ErrorInjector:
        def __init__(self):
            self.failure_rate = 0.0
            self.call_count = 0
        
        def set_failure_rate(self, rate):
            """Set failure rate between 0.0 and 1.0."""
            self.failure_rate = max(0.0, min(1.0, rate))
        
        def maybe_fail(self, exception_type=RuntimeError, message="Injected error"):
            """Maybe raise an exception based on failure rate."""
            import random
            self.call_count += 1
            
            if random.random() < self.failure_rate:
                raise exception_type(message)
    
    return ErrorInjector()


# Data generator fixture for consistent test data
@pytest.fixture
def test_data_generator():
    """Generate consistent test data."""
    class TestDataGenerator:
        def __init__(self):
            self.task_counter = 0
            self.conflict_counter = 0
        
        def create_task_request(self, **overrides):
            """Create a test task request with defaults."""
            from load_balancer import TaskRequest, TaskPriority
            
            self.task_counter += 1
            defaults = {
                'task_id': f"TEST-TASK-{self.task_counter:03d}",
                'title': f"Test Task {self.task_counter}",
                'description': f"Generated test task number {self.task_counter}",
                'domain': "backend",
                'priority': TaskPriority.MEDIUM.value,
                'estimated_duration_minutes': 60,
                'required_expertise_level': "competent",
                'deadline': None,
                'dependencies': [],
                'resource_requirements': {"cpu": 0.2, "memory": 0.1},
                'metadata': {"test": True, "generated": True}
            }
            defaults.update(overrides)
            return TaskRequest(**defaults)
        
        def create_conflict_parties(self, num_parties=2):
            """Create test conflict parties."""
            from conflict_resolution import ConflictParty
            
            parties = []
            for i in range(num_parties):
                party = ConflictParty(
                    agent_id=f"test_agent_{i}",
                    position=f"Test position {i}",
                    justification=f"Test justification {i}",
                    priority_level=5 + i,
                    authority_level=f"test_authority_{i}",
                    expertise_domains=[f"domain_{i}", "common_domain"]
                )
                parties.append(party)
            
            return parties
    
    return TestDataGenerator()