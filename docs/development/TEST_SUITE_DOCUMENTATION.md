# Multi-Agent Coordination System - Test Suite Documentation

## Overview

This document provides comprehensive documentation for the Phase 3 Advanced Test Coverage implementation, including BDD edge case testing, stress testing framework, and comprehensive testing utilities.

## Table of Contents

1. [Test Architecture](#test-architecture)
2. [BDD Testing Infrastructure](#bdd-testing-infrastructure)
3. [Stress Testing Framework](#stress-testing-framework)
4. [Testing Utilities](#testing-utilities)
5. [Running Tests](#running-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Extending the Test Suite](#extending-the-test-suite)

## Test Architecture

The test suite is organized into three main layers:

```
tests/
├── features/                    # BDD Gherkin feature files
│   └── edge_cases/
├── stress/                      # Stress testing scenarios  
├── utilities/                   # Shared testing utilities
├── test_*_bdd.py               # BDD step definitions
└── integration/                 # Integration tests (future)
```

### Key Components

- **BDD Layer**: Behavior-driven tests using Gherkin syntax
- **Stress Layer**: Performance and load testing scenarios
- **Utilities Layer**: Shared testing infrastructure and helpers
- **Integration Layer**: End-to-end system tests

## BDD Testing Infrastructure

### Feature Files

Located in `features/edge_cases/`, these Gherkin files define edge case scenarios:

#### 1. Authority Edge Cases (`authority_edge_cases.feature`)
- **15 scenarios** covering authority conflicts and edge cases
- Tests simultaneous requests, emergency authority, backup failures
- Validates authority delegation and conflict resolution

#### 2. Conflict Edge Cases (`conflict_edge_cases.feature`)  
- **15 scenarios** for conflict resolution testing
- Covers cascading conflicts, resolution failures, priority conflicts
- Tests mediation processes and escalation procedures

#### 3. Load Balancing Edge Cases (`load_balancing_edge_cases.feature`)
- **14 scenarios** for load distribution testing
- Tests agent failures, strategy switching, uneven loads
- Validates task redistribution and performance optimization

#### 4. Communication Edge Cases (`communication_edge_cases.feature`)
- **16 scenarios** for communication system testing
- Covers network failures, message ordering, timeout handling
- Tests bidirectional communication and message integrity

### Step Definitions

Located in `tests/test_*_bdd.py`, these files implement the Gherkin steps:

```python
# Example from test_authority_edge_cases_bdd.py
@given("multiple agents request the same authority simultaneously")
def multiple_agents_request_same_authority(context):
    # Implementation with custom parsers and validators
    pass

@when("the authority system processes the requests")  
def authority_system_processes_requests(context):
    # Authority processing logic
    pass

@then("only one agent should receive the authority")
def verify_single_authority_holder(context):
    # Validation with custom assertions
    pass
```

### Custom Parsers

Each BDD module includes specialized parsers:

```python
class ConflictTypeParser(parsers.StepParser):
    """Parser for conflict types and severities."""
    
    def parse_arguments(self, name):
        # Convert strings to enums and validate
        pass
```

## Stress Testing Framework

### Core Engine (`stress_test_engine.py`)

The foundation for all stress testing scenarios:

```python
class StressTestScenario(ABC):
    """Base class for stress test scenarios."""
    
    @abstractmethod
    def setup(self): pass
    
    @abstractmethod  
    def execute_stress(self): pass
    
    @abstractmethod
    def cleanup(self): pass
```

#### Key Features:
- **Resource Monitoring**: Real-time CPU, memory, disk I/O tracking
- **Performance Profiling**: Detailed metrics collection
- **Graceful Shutdown**: Signal handling and cleanup
- **Comprehensive Reporting**: JSON, HTML, and summary reports

### Stress Test Levels

Four intensity levels with different configurations:

| Level | Duration | Agents | Memory Limit | CPU Limit |
|-------|----------|--------|--------------|-----------|
| Light | 60s | 3 | 500MB | 50% |
| Medium | 300s | 6 | 1GB | 70% |
| Heavy | 600s | 12 | 2GB | 85% |
| Extreme | 1200s | 24 | 4GB | 95% |

### Agent Scaling Tests (`test_agent_scaling_stress.py`)

Tests system behavior with increasing agent counts:

```python
class AgentScalingStressScenario(StressTestScenario):
    """Tests 1→24 agent scaling with performance analysis."""
    
    def execute_stress(self):
        agent_counts = [1, 3, 6, 9, 12, 15, 18, 21, 24]
        for count in agent_counts:
            metrics = self._test_agent_count(count)
            self._check_performance_degradation(metrics)
```

#### Metrics Collected:
- Startup time scaling
- Memory usage per agent  
- Communication latency
- Authority assignment time
- File operations throughput
- Coordination overhead

## Testing Utilities

### 1. Edge Case Generators (`edge_case_generators.py`)

Generates test data using Hypothesis strategies:

```python
@composite
def agent_configurations(draw, edge_case_type=EdgeCaseType.NORMAL):
    """Generate agent configurations with edge cases."""
    return draw(lists(agent_config_strategy(), min_size=1, max_size=24))
```

#### Supported Edge Cases:
- **BOUNDARY**: Min/max values, edge boundaries
- **STRESS**: High load, resource limits
- **FAULT**: Error conditions, failures  
- **RACE**: Concurrent operations, timing issues

### 2. Scenario Validators (`scenario_validators.py`)

Validates test scenarios and results:

```python
class AuthorityValidator(ScenarioValidator):
    """Validates authority-related scenarios."""
    
    def validate(self, scenario_data):
        # Check authority assignments
        # Validate backup chains
        # Verify conflict resolution
        pass
```

### 3. BDD Assertions (`bdd_assertions.py`)

Context-aware assertions with enhanced error reporting:

```python
def assert_agent_status(self, agent_data, expected_status):
    """Assert agent has expected status with detailed context."""
    if not condition:
        raise BDDAssertionError(
            message="Agent status mismatch",
            context=self.context,
            additional_data={'agent_data': agent_data}
        )
```

#### Features:
- **Soft Assertions**: Collect multiple failures
- **Rich Context**: Detailed error messages
- **Performance Integration**: Automatic metric recording

### 4. Performance Monitoring (`bdd_performance.py`)

Real-time performance tracking:

```python
@measure_performance("authority_request")
def request_authority(agent_id, authority_type):
    # Function automatically tracked
    pass

with tracker.measure_scenario("Authority Assignment Test"):
    # Scenario automatically monitored
    pass
```

#### Capabilities:
- **Real-time Monitoring**: CPU, memory, I/O tracking
- **Regression Detection**: Baseline comparison
- **Throughput Analysis**: Operations per second
- **Resource Alerting**: Threshold-based notifications

### 5. Test Reporting (`bdd_test_reporter.py`)

Professional test reporting with multiple formats:

```python
class BDDTestReporter:
    """Comprehensive test reporting."""
    
    def generate_html_report(self): pass    # Interactive HTML dashboard
    def generate_json_report(self): pass    # CI/CD integration
    def generate_junit_xml(self): pass      # Jenkins/TeamCity support
```

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements-test.txt

# Verify pytest-bdd installation  
pytest --version
```

### BDD Tests

```bash
# Run all BDD edge case tests
pytest tests/test_*_bdd.py -v

# Run specific feature
pytest tests/test_authority_edge_cases_bdd.py

# Run with detailed reporting
pytest tests/test_*_bdd.py --html=reports/bdd_report.html
```

### Stress Tests

```bash
# Run light stress tests
pytest tests/stress/ -m "not slow"

# Run all stress tests (including heavy/extreme)
pytest tests/stress/ -v

# Run specific stress scenario
python tests/stress/test_agent_scaling_stress.py
```

### Custom Test Execution

```bash
# Run with performance monitoring
pytest tests/ --capture=no --tb=short

# Run edge cases only
pytest -m "edge_case"

# Run with specific stress level
pytest tests/stress/ -k "light"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Phase 3 Test Suite

on: [push, pull_request]

jobs:
  bdd-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run BDD tests
        run: |
          pytest tests/test_*_bdd.py --junit-xml=results/bdd-results.xml
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: bdd-test-results
          path: results/

  stress-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run stress tests
        run: |
          pytest tests/stress/ -m "not extreme" --junit-xml=results/stress-results.xml
        timeout-minutes: 30
```

### Test Reports

The test suite generates multiple report formats:

1. **HTML Reports**: Interactive dashboards with charts
2. **JSON Reports**: Machine-readable for CI/CD integration  
3. **JUnit XML**: Compatible with most CI systems
4. **Performance Reports**: Detailed performance analysis

## Extending the Test Suite

### Adding New BDD Scenarios

1. **Create Feature File**:
   ```gherkin
   # features/edge_cases/new_edge_cases.feature
   Feature: New Edge Cases
     Scenario: Test new functionality
       Given some initial state
       When some action occurs
       Then verify expected outcome
   ```

2. **Implement Step Definitions**:
   ```python
   # tests/test_new_edge_cases_bdd.py
   @given("some initial state")
   def initial_state(context):
       pass
   ```

3. **Add Validation**:
   ```python
   # tests/utilities/scenario_validators.py
   class NewValidator(ScenarioValidator):
       def validate(self, scenario_data):
           pass
   ```

### Creating New Stress Tests

1. **Inherit from Base Class**:
   ```python
   class NewStressScenario(StressTestScenario):
       def setup(self): pass
       def execute_stress(self): pass  
       def cleanup(self): pass
   ```

2. **Add Performance Metrics**:
   ```python
   self.record_metric("custom_metric", value, "unit")
   ```

3. **Create Test Cases**:
   ```python
   @pytest.mark.stress
   def test_new_stress_scenario(self):
       config = create_medium_stress_config("new_test")
       scenario = NewStressScenario(config)
       result = runner.run_scenario(scenario)
       assert result.success
   ```

### Custom Assertions

```python
# Add to bdd_assertions.py
def assert_custom_condition(self, data, expected):
    """Custom assertion with context."""
    self._assert_with_context(
        condition,
        f"Custom condition failed: {data}",
        additional_data={'data': data}
    )
```

### Performance Monitoring

```python
# Add custom performance tracking
@measure_performance("custom_operation")
def custom_function():
    pass

# Add custom metrics
tracker.add_metric("custom_throughput", operations_per_second, "ops/sec")
```

## Best Practices

### Test Organization

1. **One Feature per File**: Keep feature files focused
2. **Descriptive Scenarios**: Use clear, business-readable language
3. **Reusable Steps**: Create common step definitions
4. **Proper Cleanup**: Always clean up test resources

### Performance Testing

1. **Baseline Establishment**: Create performance baselines
2. **Resource Monitoring**: Monitor system resources during tests
3. **Gradual Scaling**: Test with increasing loads
4. **Failure Analysis**: Analyze failure patterns

### Assertions and Validation

1. **Context-Rich Errors**: Provide detailed error context
2. **Soft Assertions**: Use for collecting multiple failures
3. **Data Validation**: Validate all test data
4. **Performance Assertions**: Include performance checks

## Troubleshooting

### Common Issues

1. **Test Timeouts**: Increase timeout values for heavy tests
2. **Resource Limits**: Adjust memory/CPU limits for your system
3. **File Permissions**: Ensure test directories are writable
4. **Dependencies**: Verify all test dependencies are installed

### Debug Mode

```bash
# Run with debug output
pytest tests/ -v -s --tb=long

# Run specific test with debugging
pytest tests/test_authority_edge_cases_bdd.py::test_specific_scenario -v -s
```

### Performance Issues

```bash
# Profile test performance
python -m cProfile -o profile.stats tests/stress/test_agent_scaling_stress.py

# Monitor resource usage
htop  # or similar monitoring tool
```

## Conclusion

The Phase 3 test suite provides comprehensive coverage for the multi-agent coordination system with:

- **60+ BDD Edge Case Scenarios**
- **Professional Stress Testing Framework**  
- **Advanced Performance Monitoring**
- **Comprehensive Reporting and CI/CD Integration**
- **Extensible Architecture for Future Enhancements**

This test infrastructure ensures the coordination system can handle complex edge cases, scale effectively, and maintain performance under stress conditions.

For questions or contributions, please refer to the project's contributing guidelines and issue tracker.