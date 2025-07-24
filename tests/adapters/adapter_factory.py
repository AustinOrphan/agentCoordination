"""
Adapter Factory

Factory for creating appropriate system adapters based on configuration
and environment settings.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from .base_adapter import BaseCoordinationAdapter, AdapterMode
from .real_system_adapter import RealSystemAdapter, RealSystemConfig
from .mock_system_adapter import MockSystemAdapter, MockSystemConfig


class AdapterFactory:
    """Factory for creating coordination system adapters."""
    
    @staticmethod
    def create_adapter(
        mode: AdapterMode,
        coordination_root: Optional[str] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> BaseCoordinationAdapter:
        """
        Create an appropriate adapter based on mode and configuration.
        
        Args:
            mode: The adapter mode (REAL, MOCK, HYBRID)
            coordination_root: Path to coordination system (required for REAL mode)
            config_overrides: Additional configuration parameters
            
        Returns:
            Configured adapter instance
            
        Raises:
            ValueError: If required parameters are missing
            FileNotFoundError: If coordination system path doesn't exist
        """
        config_overrides = config_overrides or {}
        
        if mode == AdapterMode.REAL:
            return AdapterFactory._create_real_adapter(coordination_root, config_overrides)
        elif mode == AdapterMode.MOCK:
            return AdapterFactory._create_mock_adapter(config_overrides)
        elif mode == AdapterMode.HYBRID:
            return AdapterFactory._create_hybrid_adapter(coordination_root, config_overrides)
        else:
            raise ValueError(f"Unsupported adapter mode: {mode}")
            
    @staticmethod
    def _create_real_adapter(
        coordination_root: Optional[str],
        config_overrides: Dict[str, Any]
    ) -> RealSystemAdapter:
        """Create real system adapter."""
        if not coordination_root:
            raise ValueError("coordination_root is required for REAL mode")
            
        root_path = Path(coordination_root)
        if not root_path.exists():
            raise FileNotFoundError(f"Coordination system not found at: {coordination_root}")
            
        config = RealSystemConfig(
            mode=AdapterMode.REAL,
            coordination_root=coordination_root,
            **config_overrides
        )
        
        return RealSystemAdapter(config)
        
    @staticmethod
    def _create_mock_adapter(config_overrides: Dict[str, Any]) -> MockSystemAdapter:
        """Create mock system adapter."""
        config = MockSystemConfig(
            mode=AdapterMode.MOCK,
            **config_overrides
        )
        
        return MockSystemAdapter(config)
        
    @staticmethod
    def _create_hybrid_adapter(
        coordination_root: Optional[str],
        config_overrides: Dict[str, Any]
    ) -> BaseCoordinationAdapter:
        """Create hybrid adapter (future implementation)."""
        # For now, default to mock adapter for hybrid mode
        # Future: Implement adapter that mixes real and mock components
        return AdapterFactory._create_mock_adapter(config_overrides)
        
    @staticmethod
    def create_from_environment() -> BaseCoordinationAdapter:
        """
        Create adapter based on environment variables.
        
        Environment Variables:
            COORDINATION_TEST_MODE: 'real', 'mock', or 'hybrid'
            COORDINATION_ROOT: Path to coordination system
            COORDINATION_TEST_CONFIG: JSON string with additional config
            
        Returns:
            Configured adapter instance
        """
        import json
        
        # Get mode from environment
        mode_str = os.getenv("COORDINATION_TEST_MODE", "mock").lower()
        mode = AdapterMode(mode_str)
        
        # Get coordination root
        coordination_root = os.getenv("COORDINATION_ROOT")
        
        # Get additional config
        config_json = os.getenv("COORDINATION_TEST_CONFIG", "{}")
        try:
            config_overrides = json.loads(config_json)
        except json.JSONDecodeError:
            config_overrides = {}
            
        return AdapterFactory.create_adapter(mode, coordination_root, config_overrides)
        
    @staticmethod
    def auto_detect_adapter(search_paths: Optional[list] = None) -> BaseCoordinationAdapter:
        """
        Auto-detect and create appropriate adapter.
        
        Args:
            search_paths: Paths to search for coordination system
            
        Returns:
            Configured adapter instance
        """
        if search_paths is None:
            search_paths = [
                ".",
                "..",
                os.getcwd(),
                os.path.expanduser("~/coordination"),
                "/opt/coordination"
            ]
            
        # Try to find real coordination system
        for search_path in search_paths:
            path = Path(search_path)
            
            # Look for coordination system markers
            markers = [
                "coordination_manager.sh",
                "manage_agents.sh", 
                "agent_status",
                "authority_pool.json"
            ]
            
            if all((path / marker).exists() for marker in markers):
                print(f"Found coordination system at: {path}")
                return AdapterFactory.create_adapter(
                    AdapterMode.REAL,
                    str(path.absolute())
                )
                
        # Fall back to mock adapter
        print("No coordination system found, using mock adapter")
        return AdapterFactory.create_adapter(AdapterMode.MOCK)
        
    @staticmethod
    def get_test_config(adapter_mode: AdapterMode) -> Dict[str, Any]:
        """
        Get recommended test configuration for adapter mode.
        
        Args:
            adapter_mode: The adapter mode
            
        Returns:
            Dictionary with recommended configuration
        """
        if adapter_mode == AdapterMode.REAL:
            return {
                "backup_original_files": True,
                "cleanup_on_exit": True,
                "use_existing_agents": True,
                "agent_startup_timeout": 30,
                "test_isolation": True
            }
        elif adapter_mode == AdapterMode.MOCK:
            return {
                "simulate_delays": True,
                "failure_rate": 0.0,
                "max_agents": 12,
                "test_isolation": True
            }
        else:  # HYBRID
            return {
                "test_isolation": True,
                "enable_logging": True
            }