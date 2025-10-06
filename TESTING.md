# 🧪 Testing Guide

## Overview

Comprehensive testing strategy for the professional trading platform.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_monthly_signals.py
│   ├── test_risk_manager.py
│   ├── test_portfolio_tracker.py
│   ├── test_sentiment_analyzer.py
│   └── test_technical_indicators.py
└── integration/             # Integration tests
    ├── test_trading_flow.py
    └── test_data_pipeline.py
```

## Running Tests

### Quick Test

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Run specific test file
pytest tests/unit/test_monthly_signals.py

# Run specific test
pytest tests/unit/test_monthly_signals.py::TestMonthlySignals::test_calculate_score_valid_data
```

### Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=modules --cov-report=html
open htmlcov/index.html

# Terminal coverage report
pytest --cov=modules --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=modules --cov-report=xml
```

### Verbose Output

```bash
# Detailed output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```bash
# Monthly signals
pytest tests/unit/test_monthly_signals.py -v

# Risk manager
pytest tests/unit/test_risk_manager.py -v

# Portfolio tracker
pytest tests/unit/test_portfolio_tracker.py -v
```

### Integration Tests

Test component interactions:

```bash
pytest tests/integration/ -v
```

### Professional Mode Tests

```bash
# Validate professional configuration
python validate_pro_config.py

# System integration test
python test_system.py
```

## Writing Tests

### Test Template

```python
import pytest
from modules.your_module import YourClass

class TestYourClass:
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test environment"""
        self.instance = YourClass(config)
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.instance.method()
        assert result is not None
    
    def test_edge_cases(self):
        """Test edge cases"""
        with pytest.raises(ValueError):
            self.instance.method(invalid_param)
```

### Using Fixtures

Available fixtures in `conftest.py`:

- `config` - Application configuration
- `test_db` - In-memory database
- `sample_price_data` - Mock stock data
- `sample_signal` - Mock trading signal
- `sample_news_articles` - Mock news data
- `sample_portfolio_positions` - Mock portfolio

## Code Quality

### Linting

```bash
# Flake8
flake8 modules/ tests/ --max-line-length=120

# Pylint
pylint modules/*.py --disable=C0111,R0913
```

### Formatting

```bash
# Check formatting
black --check modules/ tests/ --line-length=120

# Auto-format
black modules/ tests/ --line-length=120

# Import sorting
isort modules/ tests/ --profile black
```

### Type Checking

```bash
# MyPy
mypy modules/ --ignore-missing-imports
```

## Continuous Integration

Tests run automatically on:

- Every push to `main` or `develop`
- Every pull request
- Before deployment

### GitHub Actions

See `.github/workflows/ci.yml` for full CI pipeline:

1. Code formatting check (Black)
2. Import sorting check (isort)
3. Linting (Flake8)
4. Type checking (MyPy)
5. Unit tests with coverage
6. Professional mode validation
7. Security scanning

## Test Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| monthly_signals | ~70% | 80%+ |
| risk_manager | ~65% | 80%+ |
| portfolio_tracker | ~60% | 80%+ |
| technical_indicators | ~75% | 85%+ |
| sentiment_analyzer | ~55% | 75%+ |
| **Overall** | **~65%** | **80%+** |

## Mocking External Services

### yfinance

```python
@pytest.fixture
def mock_yfinance(mocker):
    mock_ticker = mocker.patch('yfinance.Ticker')
    mock_ticker.return_value.history.return_value = sample_price_data
    return mock_ticker
```

### Reddit API

```python
@pytest.fixture
def mock_reddit(mocker):
    mock_praw = mocker.patch('praw.Reddit')
    # Configure mock
    return mock_praw
```

## Performance Testing

```bash
# Benchmark tests
pytest tests/ --benchmark-only

# Profile tests
pytest tests/ --profile
```

## Test Environment

### Environment Variables

```bash
# Set test environment
export TESTING=true
export DATABASE_PATH=:memory:
export PROFESSIONAL_MODE=true

# Run tests
pytest
```

### Test Configuration

Tests use in-memory database by default:

```python
db = DatabaseManager({'path': ':memory:'})
```

## Debugging Tests

### VS Code

`.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "-v",
                "--tb=short",
                "${file}"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### pytest Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start
pytest --trace
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Speed**: Unit tests should be fast (<100ms)
4. **Coverage**: Aim for 80%+ code coverage
5. **Fixtures**: Use fixtures for common setup
6. **Assertions**: One logical assertion per test
7. **Mocking**: Mock external dependencies
8. **Documentation**: Document complex test scenarios

## Common Issues

### Import Errors

```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Locked

```bash
# Use in-memory database for tests
# Already configured in conftest.py
```

### Slow Tests

```bash
# Run tests in parallel
pytest -n auto
```

---

**Last Updated:** 2025-10-06  
**Test Framework:** pytest 7.4+  
**Coverage Tool:** pytest-cov 4.1+
