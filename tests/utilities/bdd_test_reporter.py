"""
BDD Test Reporting Utilities

This module provides comprehensive reporting capabilities for BDD tests including:
- Custom pytest plugin for BDD-specific reporting
- HTML report generation with scenario details
- JSON export for CI/CD integration
- Performance metrics and coverage analysis
- Integration with scenario validators
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import pytest
from pytest import TestReport
from _pytest.config import Config
from _pytest.terminal import TerminalReporter

from .scenario_validators import ScenarioValidator, ScenarioValidationResult


@dataclass
class BDDTestResult:
    """Structured result for a BDD test scenario."""
    scenario_name: str
    feature_file: str
    test_function: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: Optional[str] = None
    validation_results: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class BDDTestSuite:
    """Complete test suite results."""
    name: str
    total_scenarios: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    results: List[BDDTestResult]
    summary: Dict[str, Any]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class BDDTestReporter:
    """Main BDD test reporter with multiple output formats."""
    
    def __init__(self, output_dir: str = "test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BDDTestResult] = []
        self.start_time: Optional[float] = None
        self.validator = ScenarioValidator()
        
    def start_session(self):
        """Start a new test session."""
        self.start_time = time.time()
        self.results.clear()
        
    def add_result(self, result: BDDTestResult):
        """Add a test result to the reporter."""
        self.results.append(result)
        
    def generate_html_report(self, filename: str = "bdd_report.html") -> Path:
        """Generate an HTML report with detailed BDD test results."""
        html_content = self._generate_html_content()
        report_path = self.output_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
        
    def generate_json_report(self, filename: str = "bdd_report.json") -> Path:
        """Generate a JSON report for CI/CD integration."""
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        suite = BDDTestSuite(
            name="BDD Edge Cases Test Suite",
            total_scenarios=len(self.results),
            passed=len([r for r in self.results if r.status == "passed"]),
            failed=len([r for r in self.results if r.status == "failed"]),
            skipped=len([r for r in self.results if r.status == "skipped"]),
            errors=len([r for r in self.results if r.status == "error"]),
            total_duration=total_duration,
            results=self.results,
            summary=self._generate_summary()
        )
        
        report_path = self.output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(suite), f, indent=2, default=str)
            
        return report_path
        
    def generate_junit_xml(self, filename: str = "bdd_junit.xml") -> Path:
        """Generate JUnit XML format for CI/CD integration."""
        xml_content = self._generate_junit_xml_content()
        report_path = self.output_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
            
        return report_path
        
    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        passed = len([r for r in self.results if r.status == "passed"])
        failed = len([r for r in self.results if r.status == "failed"])
        skipped = len([r for r in self.results if r.status == "skipped"])
        errors = len([r for r in self.results if r.status == "error"])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BDD Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ padding: 15px; border-radius: 5px; text-align: center; }}
        .passed {{ background: #d4edda; color: #155724; }}
        .failed {{ background: #f8d7da; color: #721c24; }}
        .skipped {{ background: #fff3cd; color: #856404; }}
        .error {{ background: #f8d7da; color: #721c24; }}
        .scenario {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .scenario.passed {{ border-left: 5px solid #28a745; }}
        .scenario.failed {{ border-left: 5px solid #dc3545; }}
        .scenario.skipped {{ border-left: 5px solid #ffc107; }}
        .scenario.error {{ border-left: 5px solid #dc3545; }}
        .error-message {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }}
        .metrics {{ background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 3px; }}
        pre {{ background: #f8f9fa; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>BDD Edge Cases Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Scenarios: {len(self.results)}</p>
    </div>
    
    <div class="summary">
        <div class="metric passed">
            <h3>{passed}</h3>
            <p>Passed</p>
        </div>
        <div class="metric failed">
            <h3>{failed}</h3>
            <p>Failed</p>
        </div>
        <div class="metric skipped">
            <h3>{skipped}</h3>
            <p>Skipped</p>
        </div>
        <div class="metric error">
            <h3>{errors}</h3>
            <p>Errors</p>
        </div>
    </div>
    
    <h2>Scenario Details</h2>
"""
        
        for result in self.results:
            html += f"""
    <div class="scenario {result.status}">
        <h3>{result.scenario_name}</h3>
        <p><strong>Feature:</strong> {result.feature_file}</p>
        <p><strong>Test Function:</strong> {result.test_function}</p>
        <p><strong>Status:</strong> {result.status.upper()}</p>
        <p><strong>Duration:</strong> {result.duration:.3f}s</p>
        
        {f'<div class="error-message"><strong>Error:</strong><br><pre>{result.error_message}</pre></div>' if result.error_message else ''}
        
        {self._format_validation_results_html(result.validation_results) if result.validation_results else ''}
        
        {self._format_performance_metrics_html(result.performance_metrics) if result.performance_metrics else ''}
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
        
    def _format_validation_results_html(self, validation_results: List[Dict[str, Any]]) -> str:
        """Format validation results for HTML display."""
        html = '<div class="metrics"><strong>Validation Results:</strong><ul>'
        for validation in validation_results:
            status = "✓" if validation.get('valid', False) else "✗"
            html += f'<li>{status} {validation.get("validator", "Unknown")}: {validation.get("message", "No message")}</li>'
        html += '</ul></div>'
        return html
        
    def _format_performance_metrics_html(self, metrics: Dict[str, float]) -> str:
        """Format performance metrics for HTML display."""
        html = '<div class="metrics"><strong>Performance Metrics:</strong><ul>'
        for metric, value in metrics.items():
            html += f'<li>{metric}: {value:.3f}</li>'
        html += '</ul></div>'
        return html
        
    def _generate_junit_xml_content(self) -> str:
        """Generate JUnit XML content."""
        total_duration = sum(r.duration for r in self.results)
        failed_count = len([r for r in self.results if r.status in ["failed", "error"]])
        
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="BDD_Edge_Cases" 
           tests="{len(self.results)}" 
           failures="{failed_count}" 
           time="{total_duration:.3f}">
"""
        
        for result in self.results:
            xml += f'    <testcase name="{result.scenario_name}" '
            xml += f'classname="{result.feature_file}" '
            xml += f'time="{result.duration:.3f}"'
            
            if result.status in ["failed", "error"]:
                xml += f'>\n        <failure message="{result.error_message or "Test failed"}">'
                xml += f'{result.error_message or "No error message"}'
                xml += '</failure>\n    </testcase>\n'
            elif result.status == "skipped":
                xml += '>\n        <skipped/>\n    </testcase>\n'
            else:
                xml += '/>\n'
                
        xml += "</testsuite>\n"
        return xml
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "total_scenarios": len(self.results),
            "passed": len([r for r in self.results if r.status == "passed"]),
            "failed": len([r for r in self.results if r.status == "failed"]),
            "skipped": len([r for r in self.results if r.status == "skipped"]),
            "errors": len([r for r in self.results if r.status == "error"]),
            "pass_rate": len([r for r in self.results if r.status == "passed"]) / len(self.results) * 100 if self.results else 0,
            "total_duration": sum(r.duration for r in self.results),
            "average_duration": sum(r.duration for r in self.results) / len(self.results) if self.results else 0,
            "features_tested": len(set(r.feature_file for r in self.results)),
            "scenarios_with_validations": len([r for r in self.results if r.validation_results]),
            "scenarios_with_performance_metrics": len([r for r in self.results if r.performance_metrics])
        }


class BDDPytestPlugin:
    """Pytest plugin for BDD test reporting."""
    
    def __init__(self):
        self.reporter = BDDTestReporter()
        self.start_times: Dict[str, float] = {}
        
    def pytest_sessionstart(self, session):
        """Called when test session starts."""
        self.reporter.start_session()
        
    def pytest_runtest_setup(self, item):
        """Called before each test runs."""
        self.start_times[item.nodeid] = time.time()
        
    def pytest_runtest_makereport(self, item, call) -> Optional[TestReport]:
        """Called when test report is made."""
        if call.when == "call":  # Only process the actual test call, not setup/teardown
            duration = time.time() - self.start_times.get(item.nodeid, time.time())
            
            # Extract BDD-specific information
            scenario_name = self._extract_scenario_name(item)
            feature_file = self._extract_feature_file(item)
            
            # Determine test status
            status = "passed"
            error_message = None
            
            if call.excinfo:
                if call.excinfo.typename == "Skipped":
                    status = "skipped"
                else:
                    status = "failed" if call.excinfo.typename in ["AssertionError", "Failed"] else "error"
                    error_message = str(call.excinfo.value)
                    
            # Create test result
            result = BDDTestResult(
                scenario_name=scenario_name,
                feature_file=feature_file,
                test_function=item.name,
                status=status,
                duration=duration,
                error_message=error_message,
                validation_results=getattr(item, '_validation_results', None),
                performance_metrics=getattr(item, '_performance_metrics', None)
            )
            
            self.reporter.add_result(result)
            
        return None
        
    def pytest_sessionfinish(self, session, exitstatus):
        """Called when test session finishes."""
        # Generate all report formats
        html_path = self.reporter.generate_html_report()
        json_path = self.reporter.generate_json_report()
        junit_path = self.reporter.generate_junit_xml()
        
        print(f"\nBDD Test Reports Generated:")
        print(f"  HTML: {html_path}")
        print(f"  JSON: {json_path}")
        print(f"  JUnit XML: {junit_path}")
        
    def _extract_scenario_name(self, item) -> str:
        """Extract scenario name from test item."""
        # Try to get from BDD markers first
        for marker in item.iter_markers("scenario"):
            if marker.args:
                return marker.args[0]
                
        # Fallback to test function name
        return item.name.replace("test_", "").replace("_", " ").title()
        
    def _extract_feature_file(self, item) -> str:
        """Extract feature file name from test item."""
        # Try to get from BDD markers first
        for marker in item.iter_markers("feature"):
            if marker.args:
                return marker.args[0]
                
        # Try to infer from file path
        file_path = str(item.fspath)
        if "features" in file_path:
            # Extract feature file name
            parts = file_path.split("/")
            for i, part in enumerate(parts):
                if part == "features" and i + 1 < len(parts):
                    return parts[i + 1]
                    
        return "Unknown Feature"


def pytest_configure(config: Config):
    """Configure pytest with BDD plugin."""
    config.pluginmanager.register(BDDPytestPlugin(), "bdd_reporter")


# Utility functions for test integration
def add_validation_result(item, validator_name: str, valid: bool, message: str):
    """Add validation result to current test item."""
    if not hasattr(item, '_validation_results'):
        item._validation_results = []
    
    item._validation_results.append({
        'validator': validator_name,
        'valid': valid,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })


def add_performance_metric(item, metric_name: str, value: float):
    """Add performance metric to current test item."""
    if not hasattr(item, '_performance_metrics'):
        item._performance_metrics = {}
    
    item._performance_metrics[metric_name] = value


def measure_performance(func):
    """Decorator to measure test performance."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Try to add to current test item if available
            import pytest
            if hasattr(pytest, '_current_test_item'):
                add_performance_metric(pytest._current_test_item, f'{func.__name__}_duration', duration)
                
            return result
        except Exception as e:
            duration = time.time() - start_time
            if hasattr(pytest, '_current_test_item'):
                add_performance_metric(pytest._current_test_item, f'{func.__name__}_duration', duration)
                add_performance_metric(pytest._current_test_item, f'{func.__name__}_error', 1.0)
            raise
            
    return wrapper


# CLI interface for standalone reporting
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate BDD test reports")
    parser.add_argument("--input", help="Input JSON results file")
    parser.add_argument("--output-dir", default="test_reports", help="Output directory")
    parser.add_argument("--format", choices=["html", "json", "junit", "all"], default="all", help="Report format")
    
    args = parser.parse_args()
    
    reporter = BDDTestReporter(args.output_dir)
    
    if args.input:
        with open(args.input, 'r') as f:
            data = json.load(f)
            for result_data in data.get('results', []):
                result = BDDTestResult(**result_data)
                reporter.add_result(result)
    
    if args.format in ["html", "all"]:
        html_path = reporter.generate_html_report()
        print(f"HTML report: {html_path}")
        
    if args.format in ["json", "all"]:
        json_path = reporter.generate_json_report()
        print(f"JSON report: {json_path}")
        
    if args.format in ["junit", "all"]:
        junit_path = reporter.generate_junit_xml()
        print(f"JUnit XML report: {junit_path}")