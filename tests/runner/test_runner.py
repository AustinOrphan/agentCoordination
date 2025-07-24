"""
Unified Test Runner

This module provides a unified test runner that can execute different test suites
in both mock and real system modes based on configuration.
"""

import os
import sys
import time
import subprocess
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import pytest

from ..config import TestConfig, TestMode, TestSuite, AdapterMode, get_test_config
from ..adapters.adapter_factory import AdapterFactory


@dataclass
class TestResult:
    """Result of a test execution."""
    suite: TestSuite
    adapter_mode: AdapterMode
    success: bool
    duration: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    error_message: Optional[str] = None
    artifacts: List[str] = None


class CoordinationTestRunner:
    """Unified test runner for coordination system tests."""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or get_test_config()
        self.results: List[TestResult] = []
        self.test_root = Path(__file__).parent.parent
        
    def run_all_tests(self) -> List[TestResult]:
        """Run all configured test suites."""
        print("🚀 Starting Coordination System Test Suite")
        print(f"   Test Mode: {self.config.test_mode.value}")
        print(f"   Adapter Mode: {self.config.get_effective_adapter_mode().value}")
        print(f"   Test Suites: {[s.value for s in self.config.test_suites]}")
        print(f"   Real System Available: {self.config.is_real_system_available()}")
        print()
        
        start_time = time.time()
        
        # Determine which adapter modes to test
        adapter_modes = self._get_adapter_modes_to_test()
        
        # Run each test suite in each adapter mode
        for suite in self.config.test_suites:
            if suite == TestSuite.ALL:
                # Run all suites
                for actual_suite in TestSuite:
                    if actual_suite != TestSuite.ALL:
                        for adapter_mode in adapter_modes:
                            result = self._run_test_suite(actual_suite, adapter_mode)
                            self.results.append(result)
            else:
                for adapter_mode in adapter_modes:
                    result = self._run_test_suite(suite, adapter_mode)
                    self.results.append(result)
        
        total_duration = time.time() - start_time
        
        # Print summary
        self._print_summary(total_duration)
        
        return self.results
    
    def _get_adapter_modes_to_test(self) -> List[AdapterMode]:
        """Determine which adapter modes to test based on configuration."""
        if self.config.test_mode == TestMode.MOCK_ONLY:
            return [AdapterMode.MOCK]
        elif self.config.test_mode == TestMode.REAL_ONLY:
            return [AdapterMode.REAL]
        elif self.config.test_mode == TestMode.BOTH:
            return [AdapterMode.MOCK, AdapterMode.REAL]
        else:  # AUTO
            available_mode = self.config.get_effective_adapter_mode()
            return [available_mode]
    
    def _run_test_suite(self, suite: TestSuite, adapter_mode: AdapterMode) -> TestResult:
        """Run a specific test suite with the given adapter mode."""
        print(f"🧪 Running {suite.value} tests in {adapter_mode.value} mode...")
        
        start_time = time.time()
        
        try:
            # Prepare test environment
            if not self._setup_test_environment(adapter_mode):
                return TestResult(
                    suite=suite,
                    adapter_mode=adapter_mode,
                    success=False,
                    duration=0.0,
                    tests_run=0,
                    tests_passed=0,
                    tests_failed=0,
                    tests_skipped=0,
                    error_message="Failed to setup test environment"
                )
            
            # Get test directory and patterns
            test_patterns = self._get_test_patterns(suite)
            
            # Build pytest command
            pytest_args = self._build_pytest_args(suite, adapter_mode, test_patterns)
            
            # Run tests
            result = self._execute_pytest(pytest_args)
            
            duration = time.time() - start_time
            
            return TestResult(
                suite=suite,
                adapter_mode=adapter_mode,
                success=result['success'],
                duration=duration,
                tests_run=result['tests_run'],
                tests_passed=result['tests_passed'],
                tests_failed=result['tests_failed'],
                tests_skipped=result['tests_skipped'],
                error_message=result.get('error_message'),
                artifacts=result.get('artifacts', [])
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                suite=suite,
                adapter_mode=adapter_mode,
                success=False,
                duration=duration,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                error_message=str(e)
            )
    
    def _setup_test_environment(self, adapter_mode: AdapterMode) -> bool:
        """Setup test environment for the given adapter mode."""
        try:
            # Set environment variables
            os.environ['COORDINATION_ADAPTER_MODE'] = adapter_mode.value
            os.environ['COORDINATION_ROOT'] = self.config.coordination_config.coordination_root
            os.environ['TEST_TIMEOUT'] = str(self.config.execution_config.timeout_seconds)
            
            # Test adapter connectivity
            adapter = AdapterFactory.create_adapter(
                mode=adapter_mode,
                coordination_root=self.config.coordination_config.coordination_root
            )
            
            return adapter.setup_test_environment()
            
        except Exception as e:
            print(f"   ❌ Failed to setup test environment: {e}")
            return False
    
    def _get_test_patterns(self, suite: TestSuite) -> List[str]:
        """Get test file patterns for a test suite."""
        patterns = {
            TestSuite.UNIT: ["test_*.py", "*_test.py"],
            TestSuite.INTEGRATION: ["integration/test_*.py"],
            TestSuite.STRESS: ["stress/test_*.py"],
            TestSuite.PROPERTY_BASED: ["property_based/test_*.py"],
            TestSuite.BDD: ["bdd/test_*.py", "**/*.feature"]
        }
        
        return patterns.get(suite, ["test_*.py"])
    
    def _build_pytest_args(self, suite: TestSuite, adapter_mode: AdapterMode, test_patterns: List[str]) -> List[str]:
        """Build pytest command arguments."""
        args = []
        
        # Add test directories/patterns
        for pattern in test_patterns:
            test_path = self.test_root / pattern
            if test_path.exists() or '*' in pattern:
                args.append(str(test_path))
        
        # Add suite-specific markers
        if suite != TestSuite.ALL:
            args.extend(["-m", suite.value])
        
        # Add adapter mode parameter
        args.extend(["-k", f"not slow or {adapter_mode.value}"])
        
        # Add configuration options
        if self.config.execution_config.verbose_logging:
            args.append("-v")
        
        if self.config.execution_config.parallel_execution:
            args.extend(["-n", "auto"])
        
        # Add timeout
        args.extend(["--timeout", str(int(self.config.execution_config.timeout_seconds))])
        
        # Add output options
        if self.config.execution_config.save_test_artifacts:
            args.extend(["--tb=short", "--junit-xml=test_results.xml"])
        
        # Add coverage if configured
        if suite in [TestSuite.UNIT, TestSuite.INTEGRATION]:
            args.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
        
        return args
    
    def _execute_pytest(self, pytest_args: List[str]) -> Dict[str, Any]:
        """Execute pytest with the given arguments."""
        try:
            # Run pytest
            result = pytest.main(pytest_args)
            
            # Parse results (this is a simplified version)
            # In real implementation, you'd parse the actual pytest output/results
            success = result == 0
            
            return {
                'success': success,
                'tests_run': 0,  # Would be parsed from pytest output
                'tests_passed': 0,  # Would be parsed from pytest output
                'tests_failed': 0 if success else 1,  # Would be parsed from pytest output
                'tests_skipped': 0,  # Would be parsed from pytest output
                'artifacts': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 1,
                'tests_skipped': 0,
                'error_message': str(e),
                'artifacts': []
            }
    
    def _print_summary(self, total_duration: float):
        """Print test execution summary."""
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        
        total_tests = sum(r.tests_run for r in self.results)
        total_passed = sum(r.tests_passed for r in self.results)
        total_failed = sum(r.tests_failed for r in self.results)
        total_skipped = sum(r.tests_skipped for r in self.results)
        
        successful_suites = len([r for r in self.results if r.success])
        total_suites = len(self.results)
        
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Test Suites: {successful_suites}/{total_suites} successful")
        print(f"Total Tests: {total_tests}")
        print(f"  ✅ Passed: {total_passed}")
        print(f"  ❌ Failed: {total_failed}")
        print(f"  ⏭️  Skipped: {total_skipped}")
        print(f"Success Rate: {(total_passed/max(total_tests, 1))*100:.1f}%")
        print()
        
        # Print details by suite
        print("RESULTS BY SUITE:")
        print("-"*40)
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.suite.value} ({result.adapter_mode.value}) - {result.duration:.2f}s")
            if result.error_message:
                print(f"      Error: {result.error_message}")
        
        print()
        
        # Print configuration summary
        print("CONFIGURATION:")
        print(f"  Test Mode: {self.config.test_mode.value}")
        print(f"  Coordination Root: {self.config.coordination_config.coordination_root}")
        print(f"  Real System Available: {self.config.is_real_system_available()}")
        
        if total_failed > 0:
            print(f"\n⚠️  {total_failed} tests failed. Check the detailed output above.")
        else:
            print(f"\n🎉 All tests passed!")


def run_coordination_tests(config_file: Optional[str] = None) -> bool:
    """Run coordination system tests with optional config file."""
    try:
        # Load configuration
        if config_file:
            from ..config import TestConfigManager
            config_manager = TestConfigManager(config_file)
            config = config_manager.load_config()
        else:
            config = get_test_config()
        
        # Create and run test runner
        runner = CoordinationTestRunner(config)
        results = runner.run_all_tests()
        
        # Return overall success
        return all(result.success for result in results)
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run coordination system tests")
    parser.add_argument("--config", help="Test configuration file")
    parser.add_argument("--mode", choices=["mock", "real", "both", "auto"], 
                       help="Test mode override")
    parser.add_argument("--suite", choices=["unit", "integration", "stress", "property_based", "bdd", "all"],
                       help="Test suite to run")
    
    args = parser.parse_args()
    
    # Override environment if arguments provided
    if args.mode:
        os.environ['COORDINATION_TEST_MODE'] = args.mode
    if args.suite:
        os.environ['TEST_SUITES'] = args.suite
    
    # Run tests
    success = run_coordination_tests(args.config)
    sys.exit(0 if success else 1)