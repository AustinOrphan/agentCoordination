# Phase 3 Advanced Test Suite

## 🎯 Overview

The Phase 3 Advanced Test Suite provides comprehensive testing capabilities for the Multi-Agent Coordination System, featuring 60+ BDD edge case scenarios, stress testing framework, and professional-grade testing utilities.

## ✨ Key Features

- **🧪 60+ BDD Edge Case Scenarios** - Comprehensive behavior-driven testing
- **🔥 Stress Testing Framework** - Performance testing with 1→24 agent scaling  
- **📊 Real-time Performance Monitoring** - Resource tracking and regression detection
- **📈 Professional Reporting** - HTML dashboards, JSON exports, CI/CD integration
- **🛠️ Advanced Testing Utilities** - Custom assertions, validators, and data generators

## 📁 Test Structure

```
tests/
├── features/edge_cases/          # 🌟 BDD Gherkin scenarios (60+ tests)
│   ├── authority_edge_cases.feature     # Authority conflicts & edge cases
│   ├── conflict_edge_cases.feature      # Conflict resolution testing  
│   ├── load_balancing_edge_cases.feature # Load distribution testing
│   └── communication_edge_cases.feature # Communication system testing
├── stress/                       # 🔥 Stress testing scenarios
│   ├── stress_test_engine.py           # Core stress testing framework
│   └── test_agent_scaling_stress.py    # Agent scaling tests (1→24)
├── utilities/                    # 🛠️ Testing infrastructure
│   ├── bdd_assertions.py              # Context-aware assertions
│   ├── bdd_performance.py             # Performance monitoring
│   ├── bdd_test_reporter.py           # Multi-format reporting  
│   ├── edge_case_generators.py        # Test data generation
│   └── scenario_validators.py         # Scenario validation
└── test_*_bdd.py                # 📝 BDD step definitions
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements-test.txt
```

### Run Tests
```bash
# All BDD edge case tests (60+ scenarios)
pytest tests/test_*_bdd.py -v

# Light stress tests (quick validation)
pytest tests/stress/ -m "not slow" -v

# Generate HTML report
pytest tests/ --html=reports/test_report.html
```

## 🧪 BDD Edge Case Testing

### Coverage Areas

| Feature | Scenarios | Description |
|---------|-----------|-------------|
| **Authority Edge Cases** | 15 | Authority conflicts, simultaneous requests, emergency scenarios |
| **Conflict Resolution** | 15 | Cascading conflicts, resolution failures, priority conflicts |  
| **Load Balancing** | 14 | Agent failures, strategy switching, uneven distribution |
| **Communication** | 16 | Network failures, message ordering, timeout handling |

### Example Scenarios
```gherkin
Scenario: Multiple agents request same authority simultaneously
  Given multiple agents are active in the system
  When they all request the "critical_path" authority at the same time
  Then only one agent should receive the authority
  And the others should be queued or receive alternative assignments
```

## 🔥 Stress Testing

### Stress Levels

| Level | Duration | Agents | Memory | CPU | Use Case |
|-------|----------|--------|--------|-----|----------|
| **Light** | 60s | 3 | 500MB | 50% | Quick validation |
| **Medium** | 300s | 6 | 1GB | 70% | Standard testing |
| **Heavy** | 600s | 12 | 2GB | 85% | Load testing |
| **Extreme** | 1200s | 24 | 4GB | 95% | Stress limits |

### Agent Scaling Analysis

The stress testing framework tests system behavior with increasing agent counts:

```python
# Automatic scaling analysis
agent_counts = [1, 3, 6, 9, 12, 15, 18, 21, 24]
for count in agent_counts:
    metrics = test_agent_count(count)
    analyze_performance_degradation(metrics)
```

**Metrics Collected:**
- Startup time scaling
- Memory usage per agent
- Communication latency  
- Authority assignment time
- File operations throughput
- Coordination overhead

## 📊 Performance Monitoring

### Real-time Tracking
```python
# Automatic performance monitoring
@measure_performance("authority_request")
def request_authority(agent_id, authority_type):
    pass

# Scenario-level monitoring  
with tracker.measure_scenario("Authority Assignment"):
    # Test operations automatically tracked
    pass
```

### Resource Monitoring
- **CPU Usage**: Process and system-wide monitoring
- **Memory Consumption**: RSS, virtual memory tracking  
- **Disk I/O**: Read/write operations monitoring
- **Network I/O**: Bytes sent/received tracking
- **File Descriptors**: Open file handle monitoring

## 🛠️ Testing Utilities

### Custom Assertions
```python
# Context-aware assertions with rich error messages
assertions = bdd_assert("Test Scenario", "Verification Step")
assertions.assert_agent_status(agent_data, "active")
assertions.assert_authority_assignment("agent_1", "critical_path", pool)
```

### Data Generation
```python
# Edge case data generation with Hypothesis
agents = generate_edge_case_data("agents", EdgeCaseType.BOUNDARY, count=10)
conflicts = generate_edge_case_data("conflicts", EdgeCaseType.STRESS, count=5)
```

### Scenario Validation
```python
# Comprehensive scenario validation
validator = AuthorityValidator()
result = validator.validate(scenario_data)
assert result.is_valid, result.error_message
```

## 📈 Reporting & Analysis

### Report Formats

1. **HTML Dashboard** - Interactive web-based reports with charts
2. **JSON Export** - Machine-readable data for CI/CD integration
3. **JUnit XML** - Compatible with Jenkins, TeamCity, GitHub Actions
4. **Performance Analysis** - Detailed performance metrics and trends

### Example Reports
```bash
# Generate comprehensive HTML report
pytest tests/ --html=reports/dashboard.html --self-contained-html

# JSON for CI/CD integration  
pytest tests/ --json-report --json-report-file=reports/results.json

# Performance analysis
python tests/utilities/bdd_performance.py --export performance_report.json
```

## 🔧 Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v
    --strict-markers
    --tb=short
    --html=reports/report.html
    --self-contained-html
markers =
    edge_case: Edge case scenarios
    stress: Stress testing scenarios  
    slow: Long-running tests
    authority: Authority system tests
    conflict: Conflict resolution tests
    communication: Communication tests
    load_balancing: Load balancing tests
```

### Dependencies (requirements-test.txt)
```
pytest>=7.0.0
pytest-bdd>=6.0.0
pytest-html>=3.1.0
pytest-json-report>=1.5.0
pytest-timeout>=2.1.0
hypothesis>=6.0.0
psutil>=5.8.0
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Phase 3 Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run BDD tests
        run: pytest tests/test_*_bdd.py --junit-xml=results/bdd.xml
      - name: Run stress tests  
        run: pytest tests/stress/ -m "not extreme" --junit-xml=results/stress.xml
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: results/
```

## 🔍 Test Execution Examples

### BDD Testing
```bash
# Run all BDD tests
pytest tests/test_*_bdd.py -v

# Run specific edge case category
pytest tests/test_authority_edge_cases_bdd.py

# Run with markers
pytest -m "authority and edge_case" -v

# Debug specific scenario
pytest tests/test_conflict_edge_cases_bdd.py::test_cascading_conflicts -v -s
```

### Stress Testing
```bash
# Quick stress validation
pytest tests/stress/ -m "not slow"

# Full stress test suite
pytest tests/stress/ -v

# Specific stress level
python tests/stress/test_agent_scaling_stress.py --level=medium

# With performance monitoring
pytest tests/stress/ --capture=no --tb=short
```

### Custom Execution
```bash
# Run with timeout (30 minutes)
pytest tests/stress/ --timeout=1800

# Parallel execution
pytest tests/ -n auto

# With coverage
pytest tests/ --cov=coordination_system --cov-report=html
```

## 📚 Documentation

- **[Complete Documentation](TEST_SUITE_DOCUMENTATION.md)** - Comprehensive guide
- **[Quick Reference](TESTING_QUICK_REFERENCE.md)** - Developer cheat sheet
- **[Architecture Overview](../ARCHITECTURE.md)** - System architecture
- **[Contributing Guide](../CONTRIBUTING.md)** - Contribution guidelines

## 🎯 Test Results Summary

### Phase 3 Test Coverage

✅ **BDD Edge Cases**: 60+ scenarios across 4 categories  
✅ **Stress Testing**: Agent scaling 1→24 with performance analysis  
✅ **Performance Monitoring**: Real-time resource tracking  
✅ **Professional Reporting**: Multi-format output with CI/CD integration  
✅ **Testing Infrastructure**: Custom assertions, validators, generators  

### Success Criteria

- **100% BDD Scenario Coverage** for identified edge cases
- **Successful Agent Scaling** from 1 to 24 agents  
- **Performance Baseline** establishment and regression detection
- **Comprehensive Documentation** with examples and best practices
- **CI/CD Integration** with automated reporting

## 🤝 Contributing

To extend the test suite:

1. **Add BDD Scenarios**: Create new `.feature` files and implement step definitions
2. **Create Stress Tests**: Inherit from `StressTestScenario` base class
3. **Extend Utilities**: Add custom assertions, validators, or generators
4. **Improve Reporting**: Enhance report formats or add new analysis capabilities

## 🆘 Support

- **Documentation**: See full documentation in `TEST_SUITE_DOCUMENTATION.md`
- **Quick Help**: Check `TESTING_QUICK_REFERENCE.md` for common commands
- **Issues**: Report issues with detailed error logs and reproduction steps
- **Debug**: Use `-v -s --tb=long` flags for detailed debugging output

---

**Phase 3 Test Suite** - Ensuring reliability, performance, and quality for the Multi-Agent Coordination System. 🚀