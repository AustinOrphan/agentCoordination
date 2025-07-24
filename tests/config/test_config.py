"""
Test Configuration Management

This module provides configuration management for switching between mock and real
system testing modes, including environment setup, adapter selection, and test
execution parameters.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from ..adapters.adapter_factory import AdapterMode


class TestMode(Enum):
    """Test execution modes."""
    MOCK_ONLY = "mock_only"
    REAL_ONLY = "real_only"
    BOTH = "both"
    AUTO = "auto"  # Automatically determine based on environment


class TestSuite(Enum):
    """Test suite categories."""
    UNIT = "unit"
    INTEGRATION = "integration"
    STRESS = "stress"
    PROPERTY_BASED = "property_based"
    BDD = "bdd"
    ALL = "all"


@dataclass
class CoordinationSystemConfig:
    """Configuration for coordination system paths and settings."""
    coordination_root: str
    agent_status_dir: str
    communication_dir: str
    authority_pool_file: str
    agent_workloads_file: str
    coordination_master_file: str
    decision_log_file: str
    theme: str = "greek_letters"
    max_agents: int = 24
    
    def validate(self) -> bool:
        """Validate that all required paths exist for real system testing."""
        required_paths = [
            self.coordination_root,
            self.agent_status_dir,
            self.communication_dir
        ]
        
        return all(os.path.exists(path) for path in required_paths)


@dataclass
class TestExecutionConfig:
    """Configuration for test execution parameters."""
    timeout_seconds: float = 300.0
    retry_attempts: int = 3
    parallel_execution: bool = False
    cleanup_after_test: bool = True
    save_test_artifacts: bool = True
    verbose_logging: bool = False
    performance_monitoring: bool = True
    stress_test_intensity: str = "medium"  # light, medium, heavy, extreme
    
    
@dataclass
class TestConfig:
    """Master test configuration."""
    test_mode: TestMode
    adapter_mode: AdapterMode
    test_suites: List[TestSuite]
    coordination_config: CoordinationSystemConfig
    execution_config: TestExecutionConfig
    custom_settings: Dict[str, Any]
    
    @classmethod
    def from_environment(cls) -> 'TestConfig':
        """Create test configuration from environment variables."""
        # Determine test mode
        test_mode_env = os.getenv('COORDINATION_TEST_MODE', 'auto').lower()
        test_mode = TestMode.AUTO
        
        for mode in TestMode:
            if mode.value == test_mode_env:
                test_mode = mode
                break
                
        # Determine adapter mode
        adapter_mode_env = os.getenv('COORDINATION_ADAPTER_MODE', 'mock').lower()
        adapter_mode = AdapterMode.MOCK if adapter_mode_env == 'mock' else AdapterMode.REAL
        
        # Get coordination root
        coordination_root = os.getenv(
            'COORDINATION_ROOT',
            '/Users/austinorphan/Library/Mobile Documents/com~apple~CloudDocs/src/agentCoordination'
        )
        
        # Build coordination system config
        coordination_config = CoordinationSystemConfig(
            coordination_root=coordination_root,
            agent_status_dir=os.path.join(coordination_root, 'agent_status'),
            communication_dir=os.path.join(coordination_root, 'agent_communication'),
            authority_pool_file=os.path.join(coordination_root, 'authority_pool.json'),
            agent_workloads_file=os.path.join(coordination_root, 'agent_workloads.json'),
            coordination_master_file=os.path.join(coordination_root, 'AGENT_COORDINATION_MASTER.json'),
            decision_log_file=os.path.join(coordination_root, 'DECISION_LOG.json'),
            theme=os.getenv('COORDINATION_THEME', 'greek_letters'),
            max_agents=int(os.getenv('COORDINATION_MAX_AGENTS', '24'))
        )
        
        # Build execution config
        execution_config = TestExecutionConfig(
            timeout_seconds=float(os.getenv('TEST_TIMEOUT', '300.0')),
            retry_attempts=int(os.getenv('TEST_RETRY_ATTEMPTS', '3')),
            parallel_execution=os.getenv('TEST_PARALLEL', 'false').lower() == 'true',
            cleanup_after_test=os.getenv('TEST_CLEANUP', 'true').lower() == 'true',
            save_test_artifacts=os.getenv('TEST_SAVE_ARTIFACTS', 'true').lower() == 'true',
            verbose_logging=os.getenv('TEST_VERBOSE', 'false').lower() == 'true',
            performance_monitoring=os.getenv('TEST_PERFORMANCE_MONITORING', 'true').lower() == 'true',
            stress_test_intensity=os.getenv('STRESS_TEST_INTENSITY', 'medium')
        )
        
        # Parse test suites
        test_suites_env = os.getenv('TEST_SUITES', 'all')
        if test_suites_env == 'all':
            test_suites = [TestSuite.ALL]
        else:
            suite_names = [s.strip() for s in test_suites_env.split(',')]
            test_suites = []
            for suite_name in suite_names:
                for suite in TestSuite:
                    if suite.value == suite_name:
                        test_suites.append(suite)
                        break
        
        return cls(
            test_mode=test_mode,
            adapter_mode=adapter_mode,
            test_suites=test_suites,
            coordination_config=coordination_config,
            execution_config=execution_config,
            custom_settings={}
        )
    
    @classmethod
    def from_file(cls, config_file: str) -> 'TestConfig':
        """Load test configuration from JSON file."""
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        # Convert enum strings back to enums
        test_mode = TestMode(config_data['test_mode'])
        adapter_mode = AdapterMode(config_data['adapter_mode'])
        test_suites = [TestSuite(suite) for suite in config_data['test_suites']]
        
        coordination_config = CoordinationSystemConfig(**config_data['coordination_config'])
        execution_config = TestExecutionConfig(**config_data['execution_config'])
        
        return cls(
            test_mode=test_mode,
            adapter_mode=adapter_mode,
            test_suites=test_suites,
            coordination_config=coordination_config,
            execution_config=execution_config,
            custom_settings=config_data.get('custom_settings', {})
        )
    
    def save_to_file(self, config_file: str):
        """Save test configuration to JSON file."""
        config_data = asdict(self)
        
        # Convert enums to strings
        config_data['test_mode'] = self.test_mode.value
        config_data['adapter_mode'] = self.adapter_mode.value
        config_data['test_suites'] = [suite.value for suite in self.test_suites]
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def is_real_system_available(self) -> bool:
        """Check if real coordination system is available for testing."""
        return self.coordination_config.validate()
    
    def get_effective_adapter_mode(self) -> AdapterMode:
        """Get the effective adapter mode based on test mode and system availability."""
        if self.test_mode == TestMode.MOCK_ONLY:
            return AdapterMode.MOCK
        elif self.test_mode == TestMode.REAL_ONLY:
            return AdapterMode.REAL
        elif self.test_mode == TestMode.AUTO:
            return AdapterMode.REAL if self.is_real_system_available() else AdapterMode.MOCK
        else:  # BOTH mode
            return self.adapter_mode
    
    def should_run_suite(self, suite: TestSuite) -> bool:
        """Check if a specific test suite should be run."""
        return TestSuite.ALL in self.test_suites or suite in self.test_suites
    
    def get_coordination_root(self, for_mock: bool = False) -> str:
        """Get appropriate coordination root directory."""
        if for_mock:
            import tempfile
            return tempfile.mkdtemp(prefix="coordination_test_")
        else:
            return self.coordination_config.coordination_root


class TestConfigManager:
    """Manages test configuration loading and environment setup."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config: Optional[TestConfig] = None
        
    def load_config(self) -> TestConfig:
        """Load test configuration from file or environment."""
        if self._config:
            return self._config
            
        if self.config_file and os.path.exists(self.config_file):
            self._config = TestConfig.from_file(self.config_file)
        else:
            self._config = TestConfig.from_environment()
            
        return self._config
    
    def get_config(self) -> TestConfig:
        """Get current test configuration."""
        if not self._config:
            return self.load_config()
        return self._config
    
    def create_mock_config(self) -> TestConfig:
        """Create a configuration for mock-only testing."""
        base_config = self.get_config()
        
        # Create a copy with mock settings
        mock_coordination_config = CoordinationSystemConfig(
            coordination_root="/tmp/coordination_test",
            agent_status_dir="/tmp/coordination_test/agent_status",
            communication_dir="/tmp/coordination_test/agent_communication",
            authority_pool_file="/tmp/coordination_test/authority_pool.json",
            agent_workloads_file="/tmp/coordination_test/agent_workloads.json",
            coordination_master_file="/tmp/coordination_test/AGENT_COORDINATION_MASTER.json",
            decision_log_file="/tmp/coordination_test/DECISION_LOG.json",
            theme=base_config.coordination_config.theme,
            max_agents=base_config.coordination_config.max_agents
        )
        
        return TestConfig(
            test_mode=TestMode.MOCK_ONLY,
            adapter_mode=AdapterMode.MOCK,
            test_suites=base_config.test_suites,
            coordination_config=mock_coordination_config,
            execution_config=base_config.execution_config,
            custom_settings=base_config.custom_settings
        )
    
    def create_real_config(self) -> TestConfig:
        """Create a configuration for real system testing."""
        base_config = self.get_config()
        
        return TestConfig(
            test_mode=TestMode.REAL_ONLY,
            adapter_mode=AdapterMode.REAL,
            test_suites=base_config.test_suites,
            coordination_config=base_config.coordination_config,
            execution_config=base_config.execution_config,
            custom_settings=base_config.custom_settings
        )
    
    def save_default_configs(self, output_dir: str = "tests/config"):
        """Save default configuration templates."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Mock configuration
        mock_config = self.create_mock_config()
        mock_config.save_to_file(os.path.join(output_dir, "mock_test_config.json"))
        
        # Real configuration
        real_config = self.create_real_config()
        real_config.save_to_file(os.path.join(output_dir, "real_test_config.json"))
        
        # Combined configuration
        combined_config = TestConfig(
            test_mode=TestMode.BOTH,
            adapter_mode=AdapterMode.MOCK,  # Default to mock
            test_suites=[TestSuite.ALL],
            coordination_config=real_config.coordination_config,
            execution_config=TestExecutionConfig(),
            custom_settings={}
        )
        combined_config.save_to_file(os.path.join(output_dir, "combined_test_config.json"))


# Global configuration manager instance
config_manager = TestConfigManager()


def get_test_config() -> TestConfig:
    """Get the current test configuration."""
    return config_manager.get_config()


def setup_test_environment(config: TestConfig) -> bool:
    """Setup test environment based on configuration."""
    try:
        # Create necessary directories for mock testing
        if config.get_effective_adapter_mode() == AdapterMode.MOCK:
            coordination_root = config.get_coordination_root(for_mock=True)
            os.makedirs(coordination_root, exist_ok=True)
            os.makedirs(os.path.join(coordination_root, 'agent_status'), exist_ok=True)
            os.makedirs(os.path.join(coordination_root, 'agent_communication'), exist_ok=True)
            
        # Validate real system if required
        elif config.get_effective_adapter_mode() == AdapterMode.REAL:
            if not config.is_real_system_available():
                print("Warning: Real coordination system not available, falling back to mock")
                return False
                
        return True
        
    except Exception as e:
        print(f"Failed to setup test environment: {e}")
        return False


if __name__ == "__main__":
    # Create and save default configurations
    manager = TestConfigManager()
    manager.save_default_configs()
    
    # Show current configuration
    config = manager.get_config()
    print("Current Test Configuration:")
    print(f"  Test Mode: {config.test_mode.value}")
    print(f"  Adapter Mode: {config.adapter_mode.value}")
    print(f"  Effective Adapter Mode: {config.get_effective_adapter_mode().value}")
    print(f"  Test Suites: {[s.value for s in config.test_suites]}")
    print(f"  Coordination Root: {config.coordination_config.coordination_root}")
    print(f"  Real System Available: {config.is_real_system_available()}")