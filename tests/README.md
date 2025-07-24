# Multi-Agent Coordination System Test Suite

This directory contains comprehensive tests for the Multi-Agent Coordination System, covering unit tests, integration tests, end-to-end scenarios, performance testing, and error handling.

## 📁 Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_dynamic_authority_manager.py  # Unit tests for authority management
├── test_conflict_resolution.py     # Unit tests for conflict resolution
├── test_load_balancer.py          # Unit tests for load balancing
├── test_integration.py            # Integration tests for component interaction
├── test_end_to_end.py             # End-to-end workflow tests
├── test_performance.py            # Performance and scalability tests
├── test_error_handling.py         # Error handling and edge case tests
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Or install minimal requirements:
```bash
pip install pytest pytest-cov psutil
```

### Running Tests

Use the convenient test runner:
```bash
# Run all tests
python run_tests.py all

# Run fast tests (unit + integration)
python run_tests.py fast

# Run specific test suites
python run_tests.py unit --verbose --coverage
python run_tests.py integration
python run_tests.py e2e
python run_tests.py performance
python run_tests.py error

# Run smoke tests for quick verification
python run_tests.py smoke

# Run specific tests
python run_tests.py specific -k "authority"
```

### Direct Pytest Usage

You can also use pytest directly:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=coordination_system --cov=. --cov-report=html

# Run specific test files
pytest tests/test_load_balancer.py -v

# Run tests with specific markers
pytest -m "unit" -v
pytest -m "not slow" -v
```

## 🧪 Test Categories

### Unit Tests
Test individual components in isolation:
- **Dynamic Authority Manager**: Authority assignment, transfers, emergency protocols
- **Conflict Resolution System**: Conflict reporting, mediation, resolution strategies
- **Load Balancer**: Task assignment, queue management, various balancing strategies

**Run with:** `python run_tests.py unit`

### Integration Tests
Test interaction between components:
- Authority and conflict resolution integration
- Load balancer with authority system
- Multi-component workflows
- Data persistence across systems

**Run with:** `python run_tests.py integration`

### End-to-End Tests
Test complete real-world scenarios:
- Complete project development workflow
- Multi-agent collaboration scenarios
- System resilience under stress
- Real-world deployment scenarios

**Run with:** `python run_tests.py e2e`

### Performance Tests
Test system performance and scalability:
- Authority assignment performance
- Task assignment throughput
- Conflict resolution speed
- System scalability with increasing load
- Memory usage patterns
- Concurrent load performance

**Run with:** `python run_tests.py performance`

### Error Handling Tests
Test system robustness:
- File system errors
- Invalid input handling
- Concurrency errors
- Resource exhaustion
- Data corruption recovery
- Network simulation errors

**Run with:** `python run_tests.py error`

## 📊 Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.error_handling` - Error handling tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.flaky` - Tests that may be timing-sensitive

Run specific categories:
```bash
pytest -m "unit"
pytest -m "not slow"
pytest -m "performance or error_handling"
```

## 🔧 Test Configuration

### Pytest Configuration
Configuration is in `pytest.ini`:
- Test discovery patterns
- Marker definitions
- Output formatting
- Warning filters

### Shared Fixtures
Common fixtures in `conftest.py`:
- Temporary directories
- Mock agent lists
- Performance monitoring
- Error injection
- Test data generators

### Custom Assertions
Helper assertions for better test readability:
- `assert_authority_result_valid()`
- `assert_task_assignment_valid()`
- `assert_conflict_id_valid()`
- `assert_load_status_valid()`

## 📈 Coverage Reports

Generate coverage reports:
```bash
# HTML report
python run_tests.py unit --coverage
open htmlcov/index.html

# Terminal report
pytest --cov=coordination_system --cov-report=term

# Coverage badge
coverage-badge -o coverage.svg
```

## 🚨 CI/CD Integration

### GitHub Actions
The test suite integrates with GitHub Actions (`.github/workflows/test.yml`):
- **Code Quality**: Linting, formatting, type checking
- **Multi-platform Testing**: Ubuntu, Windows, macOS
- **Multi-version Testing**: Python 3.8-3.11
- **Performance Testing**: Automated performance benchmarks
- **Security Scanning**: Vulnerability checks
- **Coverage Reporting**: Automated coverage tracking

### Test Matrix
The CI runs tests across:
- Operating systems: Ubuntu, Windows, macOS
- Python versions: 3.8, 3.9, 3.10, 3.11
- Test categories: Unit, integration, e2e, performance, error handling

## 🎯 Test Development Guidelines

### Writing New Tests

1. **Choose the Right Category**:
   - Unit tests for isolated component testing
   - Integration tests for component interaction
   - E2E tests for complete workflows

2. **Use Descriptive Names**:
   ```python
   def test_authority_assignment_with_preferred_agent():
   def test_load_balancer_handles_resource_exhaustion():
   def test_conflict_resolution_timeout_escalation():
   ```

3. **Follow the AAA Pattern**:
   ```python
   def test_example():
       # Arrange
       authority_manager = DynamicAuthorityManager(temp_dir)
       
       # Act
       result = authority_manager.assign_authority("Test task")
       
       # Assert
       assert result["success"] is True
   ```

4. **Use Appropriate Fixtures**:
   ```python
   def test_with_temp_environment(temp_test_dir, test_assertions):
       # Use temp_test_dir for file operations
       # Use test_assertions for better error messages
   ```

5. **Add Proper Markers**:
   ```python
   @pytest.mark.unit
   def test_unit_functionality():
       pass
   
   @pytest.mark.slow
   @pytest.mark.e2e
   def test_complete_workflow():
       pass
   ```

### Test Data Management

Use the test data generator:
```python
def test_with_generated_data(test_data_generator):
    task = test_data_generator.create_task_request(
        domain="security",
        priority=TaskPriority.HIGH.value
    )
    parties = test_data_generator.create_conflict_parties(3)
```

### Performance Testing

Use the performance monitor:
```python
def test_performance_critical_operation(performance_monitor):
    # Test runs automatically within performance monitoring
    result = expensive_operation()
    assert result is not None
    # Performance metrics logged automatically
```

## 🔍 Debugging Tests

### Running Individual Tests
```bash
# Run single test
pytest tests/test_load_balancer.py::TestLoadBalancer::test_assign_task_round_robin -v

# Run with debugging
pytest tests/test_load_balancer.py -v -s --tb=long

# Run with pdb
pytest tests/test_load_balancer.py --pdb
```

### Test Output
```bash
# Show print statements
pytest -s

# Verbose output
pytest -v

# Show local variables in tracebacks
pytest --tb=long
```

### Common Issues

1. **Import Errors**: Check that project root is in PYTHONPATH
2. **File Permissions**: Tests create temporary files, ensure write permissions
3. **Concurrency Issues**: Some tests involve threading, may be timing-sensitive
4. **Resource Cleanup**: Tests clean up automatically, but manual cleanup may be needed for interrupted runs

## 📚 Dependencies

### Required
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting

### Optional (Enhanced Functionality)
- `psutil` - System monitoring for performance tests
- `pytest-xdist` - Parallel test execution
- `pytest-mock` - Enhanced mocking capabilities

### Development Tools
- `flake8` - Code linting
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking
- `bandit` - Security scanning

## 🤝 Contributing

When adding new features:

1. **Write Tests First** (TDD approach)
2. **Ensure Coverage** - Aim for >90% coverage on new code
3. **Test Edge Cases** - Include error conditions and boundary cases
4. **Performance Considerations** - Add performance tests for critical paths
5. **Documentation** - Update test documentation for new test patterns

### Test Review Checklist

- [ ] Tests are properly categorized with markers
- [ ] Test names are descriptive
- [ ] Tests follow AAA pattern
- [ ] Edge cases and error conditions tested
- [ ] Performance implications considered
- [ ] CI/CD pipeline passes
- [ ] Coverage requirements met

## 📞 Support

For test-related issues:

1. Check this README first
2. Review test output and error messages
3. Check CI/CD logs for additional context
4. Verify all dependencies are installed
5. Consider temporary file permissions and cleanup

The test suite is designed to be comprehensive, maintainable, and reliable. It provides confidence in system changes and helps catch issues early in development.