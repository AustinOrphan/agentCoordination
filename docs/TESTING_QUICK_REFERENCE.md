# Testing Quick Reference Guide

## 🚀 Quick Start

### Run All Tests
```bash
# Install dependencies
pip install -r requirements-test.txt

# Run all BDD edge case tests
pytest tests/test_*_bdd.py -v

# Run light stress tests  
pytest tests/stress/ -m "not slow" -v
```

### Generate Reports
```bash
# HTML report with dashboard
pytest tests/ --html=reports/test_report.html --self-contained-html

# JSON report for CI/CD
pytest tests/ --json-report --json-report-file=reports/test_results.json
```

## 📊 Test Categories

| Category | Command | Description |
|----------|---------|-------------|
| **BDD Edge Cases** | `pytest tests/test_*_bdd.py` | 60+ behavior-driven edge case scenarios |
| **Light Stress** | `pytest tests/stress/ -m "not slow"` | Quick performance validation |
| **Heavy Stress** | `pytest tests/stress/` | Full stress testing suite |
| **Authority Tests** | `pytest tests/test_authority_edge_cases_bdd.py` | Authority system edge cases |
| **Conflict Tests** | `pytest tests/test_conflict_edge_cases_bdd.py` | Conflict resolution testing |
| **Communication Tests** | `pytest tests/test_communication_edge_cases_bdd.py` | Communication edge cases |
| **Load Balancing** | `pytest tests/test_load_balancing_edge_cases_bdd.py` | Load distribution testing |

## 🧪 BDD Test Structure

### Feature Files
```
features/edge_cases/
├── authority_edge_cases.feature      # 15 authority scenarios
├── conflict_edge_cases.feature       # 15 conflict scenarios  
├── load_balancing_edge_cases.feature # 14 load balancing scenarios
└── communication_edge_cases.feature  # 16 communication scenarios
```

### Example BDD Test
```bash
# Run specific scenario
pytest tests/test_authority_edge_cases_bdd.py::test_authority_conflicts_scenario -v

# Run with specific tags
pytest -m "authority and edge_case"
```

## 🔥 Stress Testing

### Stress Levels
```bash
# Light (60s, 3 agents, 500MB)
python tests/stress/test_agent_scaling_stress.py --level=light

# Medium (300s, 6 agents, 1GB)  
python tests/stress/test_agent_scaling_stress.py --level=medium

# Heavy (600s, 12 agents, 2GB)
python tests/stress/test_agent_scaling_stress.py --level=heavy

# Extreme (1200s, 24 agents, 4GB)
python tests/stress/test_agent_scaling_stress.py --level=extreme
```

### Scaling Tests
```python
# Test agent scaling 1→24
from tests.stress.test_agent_scaling_stress import AgentScalingStressScenario
from tests.stress.stress_test_engine import create_medium_stress_config, StressTestRunner

config = create_medium_stress_config("scaling_test", agent_count=12)
scenario = AgentScalingStressScenario(config) 
runner = StressTestRunner()
result = runner.run_scenario(scenario)
```

## 🛠️ Testing Utilities

### Custom Assertions
```python
from tests.utilities.bdd_assertions import bdd_assert

# Context-aware assertions
assertions = bdd_assert("Test Scenario", "Verification Step")
assertions.assert_agent_status(agent_data, "active")
assertions.assert_authority_assignment("agent_1", "critical_path", authority_pool)
```

### Performance Monitoring
```python
from tests.utilities.bdd_performance import create_performance_tracker

tracker = create_performance_tracker()

# Monitor entire scenario
with tracker.measure_scenario("Authority Test"):
    # Test operations
    pass

# Monitor specific operations  
with tracker.measure_operation("authority_request"):
    request_authority("agent_1", "critical_path")
```

### Data Generation
```python
from tests.utilities.edge_case_generators import generate_edge_case_data

# Generate test data
agents = generate_edge_case_data("agents", EdgeCaseType.BOUNDARY, count=10)
conflicts = generate_edge_case_data("conflicts", EdgeCaseType.STRESS, count=5)
```

### Scenario Validation
```python
from tests.utilities.scenario_validators import AuthorityValidator

validator = AuthorityValidator()
result = validator.validate(scenario_data)
assert result.is_valid, result.error_message
```

## 📈 Performance Monitoring

### Real-time Metrics
```python
# Automatic performance tracking
@measure_performance("critical_operation")
def critical_function():
    pass

# Manual metric recording  
tracker.record_metric("throughput", 150.5, "ops/sec")
tracker.count_throughput("requests", 10)
```

### Resource Monitoring
```python
from tests.stress.stress_test_engine import ResourceMonitor

monitor = ResourceMonitor(sampling_interval=0.5)
monitor.set_thresholds(process_memory_mb=1000, process_cpu_percent=80)
monitor.start_monitoring()

# Your test code here

summary = monitor.stop_monitoring()
print(f"Peak Memory: {summary['peak_memory_mb']:.1f}MB")
print(f"Peak CPU: {summary['peak_cpu_percent']:.1f}%")
```

## 🔍 Debugging

### Debug Mode
```bash
# Verbose output with stack traces
pytest tests/ -v -s --tb=long

# Debug specific test
pytest tests/test_authority_edge_cases_bdd.py::test_specific -v -s --pdb

# Show test durations
pytest tests/ --durations=10
```

### Performance Profiling
```bash
# Profile test execution
python -m cProfile -o profile.stats tests/stress/test_agent_scaling_stress.py

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('time').print_stats(20)"
```

## 📊 Reports and Analysis

### HTML Dashboard
```bash
# Generate interactive HTML report
pytest tests/ --html=reports/dashboard.html --self-contained-html

# Open in browser
open reports/dashboard.html
```

### JSON Analysis
```bash
# Generate JSON for analysis
pytest tests/ --json-report --json-report-file=reports/results.json

# Analyze with jq
cat reports/results.json | jq '.tests[] | select(.outcome == "failed") | .nodeid'
```

### Performance Reports
```python
# Generate performance analysis
tracker.export_metrics("performance_analysis.json")

# Load and analyze
import json
with open("performance_analysis.json") as f:
    data = json.load(f)
    
for op, stats in data["operation_stats"].items():
    print(f"{op}: avg={stats['avg']:.3f}s, p95={stats['p95']:.3f}s")
```

## 🏗️ Adding New Tests

### New BDD Scenario
1. **Add to Feature File**:
   ```gherkin
   Scenario: New edge case scenario
     Given initial system state
     When specific action occurs  
     Then verify expected outcome
   ```

2. **Implement Steps**:
   ```python
   @given("initial system state")
   def initial_state(context):
       context.system = setup_test_system()
   ```

### New Stress Test
```python
class CustomStressScenario(StressTestScenario):
    def setup(self):
        # Initialize test environment
        pass
        
    def execute_stress(self):
        # Main stress testing logic
        while self.should_continue():
            # Perform stress operations
            self.record_metric("custom_metric", value)
            
    def cleanup(self):
        # Clean up resources
        pass
```

## 🚨 Common Issues

### Test Timeouts
```bash
# Increase timeout for slow tests
pytest tests/stress/ --timeout=1800  # 30 minutes

# Skip slow tests
pytest tests/ -m "not slow"
```

### Memory Issues
```python
# Reduce agent count for limited systems
config = create_light_stress_config("test", agent_count=3, max_memory_mb=256)
```

### File Permissions
```bash
# Ensure test directories are writable
chmod -R 755 tests/
mkdir -p stress_test_results test_reports
```

## 📚 Key Files

| File | Purpose |
|------|---------|
| `pytest.ini` | Test configuration |
| `requirements-test.txt` | Test dependencies |
| `tests/utilities/bdd_assertions.py` | Custom assertions |
| `tests/utilities/bdd_performance.py` | Performance monitoring |
| `tests/utilities/bdd_test_reporter.py` | Test reporting |
| `tests/stress/stress_test_engine.py` | Stress testing framework |
| `features/edge_cases/*.feature` | BDD scenarios |

## 💡 Tips

1. **Start Small**: Begin with light stress tests and individual BDD scenarios
2. **Monitor Resources**: Watch CPU/memory usage during stress tests
3. **Use Baselines**: Establish performance baselines for regression detection
4. **Parallel Execution**: Use `pytest-xdist` for parallel test execution
5. **CI Integration**: Set up automated testing in your CI/CD pipeline

## 🆘 Getting Help

- Check test logs in `stress_test_results/` and `test_reports/`
- Use `-v` flag for verbose output
- Add `--pdb` for interactive debugging
- Review the full documentation in `TEST_SUITE_DOCUMENTATION.md`