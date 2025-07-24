#!/usr/bin/env python3
"""
Comprehensive test runner for Multi-Agent Coordination System
Runs different test suites with appropriate configurations
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
import json
from datetime import datetime


class TestRunner:
    """Test runner with multiple test suite configurations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        
    def run_unit_tests(self, verbose=False, coverage=False):
        """Run unit tests."""
        print("🧪 Running Unit Tests")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_dynamic_authority_manager.py"),
            str(self.tests_dir / "test_conflict_resolution.py"),
            str(self.tests_dir / "test_load_balancer.py"),
            "-m", "unit",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=coordination_system", "--cov=.", "--cov-report=html", "--cov-report=term"])
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_integration_tests(self, verbose=False):
        """Run integration tests."""
        print("🔗 Running Integration Tests")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_integration.py"),
            "-m", "integration",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_e2e_tests(self, verbose=False):
        """Run end-to-end tests."""
        print("🚀 Running End-to-End Tests")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_end_to_end.py"),
            "-m", "e2e",
            "--tb=short",
            "-s"  # Don't capture output for e2e tests
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_performance_tests(self, verbose=False):
        """Run performance tests."""
        print("⚡ Running Performance Tests")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_performance.py"),
            "-m", "performance",
            "--tb=short",
            "-s"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_error_handling_tests(self, verbose=False):
        """Run error handling tests."""
        print("🛡️ Running Error Handling Tests")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_error_handling.py"),
            "-m", "error_handling",
            "--tb=short",
            "-s"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_fast_tests(self, verbose=False, coverage=False):
        """Run fast tests (unit + integration)."""
        print("⚡ Running Fast Test Suite")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir),
            "-m", "not slow",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=coordination_system", "--cov=.", "--cov-report=html", "--cov-report=term"])
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_all_tests(self, verbose=False, coverage=False):
        """Run all tests."""
        print("🎯 Running Complete Test Suite")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir),
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=coordination_system", "--cov=.", "--cov-report=html", "--cov-report=term"])
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_smoke_tests(self, verbose=False):
        """Run minimal smoke tests."""
        print("💨 Running Smoke Tests")
        
        # Just run a few key tests to verify basic functionality
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "test_dynamic_authority_manager.py::TestDynamicAuthorityManager::test_initialization"),
            str(self.tests_dir / "test_conflict_resolution.py::TestConflictResolutionSystem::test_initialization"),
            str(self.tests_dir / "test_load_balancer.py::TestLoadBalancer::test_initialization"),
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_specific_test(self, test_pattern, verbose=False):
        """Run specific test matching pattern."""
        print(f"🔍 Running Specific Tests: {test_pattern}")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir),
            "-k", test_pattern,
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("📋 Checking Test Dependencies")
        
        required_packages = ["pytest", "pytest-cov"]
        optional_packages = ["psutil"]
        
        missing_required = []
        missing_optional = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✓ {package}")
            except ImportError:
                missing_required.append(package)
                print(f"  ✗ {package} (REQUIRED)")
        
        for package in optional_packages:
            try:
                __import__(package)
                print(f"  ✓ {package} (optional)")
            except ImportError:
                missing_optional.append(package)
                print(f"  ⚠ {package} (optional, enhanced functionality)")
        
        if missing_required:
            print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
            print("Install with: pip install " + " ".join(missing_required))
            return False
        
        if missing_optional:
            print(f"\n⚠️ Missing optional packages: {', '.join(missing_optional)}")
            print("Install with: pip install " + " ".join(missing_optional))
        
        return True
    
    def generate_test_report(self, results):
        """Generate test execution report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "summary": {
                "total_suites": len(results),
                "passed_suites": len([r for r in results if r["returncode"] == 0]),
                "failed_suites": len([r for r in results if r["returncode"] != 0])
            }
        }
        
        report_file = self.project_root / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Test report saved to: {report_file}")
        return report


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Coordination System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Suite Options:
  unit          - Run unit tests only (fast)
  integration   - Run integration tests only  
  e2e           - Run end-to-end tests (slow)
  performance   - Run performance tests (slow)
  error         - Run error handling tests
  fast          - Run fast tests (unit + integration)
  all           - Run complete test suite
  smoke         - Run minimal smoke tests
  
Examples:
  python run_tests.py unit -v --coverage
  python run_tests.py fast 
  python run_tests.py all --verbose
  python run_tests.py specific -k "test_authority"
        """
    )
    
    parser.add_argument(
        "suite",
        choices=["unit", "integration", "e2e", "performance", "error", "fast", "all", "smoke", "specific"],
        help="Test suite to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        help="Run tests matching keyword (for 'specific' suite)"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check test dependencies and exit"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate test report"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check dependencies if requested
    if args.check_deps:
        deps_ok = runner.check_dependencies()
        sys.exit(0 if deps_ok else 1)
    
    # Check dependencies before running tests
    if not runner.check_dependencies():
        print("\n❌ Cannot run tests due to missing dependencies")
        sys.exit(1)
    
    print(f"\n🚀 Starting {args.suite.upper()} test suite")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    # Run selected test suite
    if args.suite == "unit":
        result = runner.run_unit_tests(args.verbose, args.coverage)
    elif args.suite == "integration":
        result = runner.run_integration_tests(args.verbose)
    elif args.suite == "e2e":
        result = runner.run_e2e_tests(args.verbose)
    elif args.suite == "performance":
        result = runner.run_performance_tests(args.verbose)
    elif args.suite == "error":
        result = runner.run_error_handling_tests(args.verbose)
    elif args.suite == "fast":
        result = runner.run_fast_tests(args.verbose, args.coverage)
    elif args.suite == "all":
        result = runner.run_all_tests(args.verbose, args.coverage)
    elif args.suite == "smoke":
        result = runner.run_smoke_tests(args.verbose)
    elif args.suite == "specific":
        if not args.keyword:
            print("❌ Keyword (-k) required for specific test suite")
            sys.exit(1)
        result = runner.run_specific_test(args.keyword, args.verbose)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Record result
    results.append({
        "suite": args.suite,
        "returncode": result.returncode,
        "duration_seconds": duration
    })
    
    print("=" * 60)
    print(f"⏱️ Total execution time: {duration:.2f} seconds")
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    # Generate report if requested
    if args.report:
        runner.generate_test_report(results)
    
    # Exit with test result code
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()