# 🧪 Testing Guide for Recall Application

This guide covers the comprehensive test suite for the Recall audio transcription application, including desktop GUI tests, web API tests, and unit tests.

## 🗂️ Test Structure

```
recall/
├── tests/                      # Unit tests directory
│   ├── __init__.py
│   ├── test_config.py         # Config class tests
│   ├── test_audio_handler.py  # Audio processing tests
│   ├── test_transcriber.py    # Transcription tests
│   └── test_web_api.py        # Web API tests
├── test_gui.py                # Desktop GUI tests
├── run_tests.py               # Main test runner
├── pytest.ini                # pytest configuration
├── debug_transcription.py     # Integration tests
├── check_audio_content.py     # Audio content tests
└── scripts/test_deployment.sh # Web deployment tests
```

## 🚀 Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py --unit

# GUI tests only
python run_tests.py --gui

# Integration tests only
python run_tests.py --integration

# Web deployment tests only
python run_tests.py --web
```

### Run Tests with Verbose Output
```bash
python run_tests.py --verbose
```

## 📦 Test Dependencies

Install testing dependencies:
```bash
pip install -r requirements.txt
```

### Required Testing Packages
- **pytest**: Unit testing framework
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Code coverage reporting
- **customtkinter**: GUI framework (for GUI tests)
- **flask**: Web framework (for web API tests)

## 🧪 Test Categories

### 1. Unit Tests (`tests/` directory)

#### Config Tests (`test_config.py`)
- ✅ Configuration loading
- ✅ Environment variable handling
- ✅ API key management
- ✅ Output directory validation
- ✅ Supported file formats
- ✅ Default values
- ✅ Configuration updates

#### Audio Handler Tests (`test_audio_handler.py`)
- ✅ Audio file processing
- ✅ Format validation
- ✅ File existence checks
- ✅ AMR format handling
- ✅ Temporary file cleanup
- ✅ Error handling
- ✅ Path handling
- ✅ Unicode filename support
- ✅ Concurrent access
- ✅ Memory management

#### Transcriber Tests (`test_transcriber.py`)
- ✅ Transcription initialization
- ✅ API key configuration
- ✅ Successful transcription
- ✅ Error handling
- ✅ Empty result handling
- ✅ Speaker identification
- ✅ Network error handling
- ✅ Rate limit handling
- ✅ Timeout handling
- ✅ Large file processing
- ✅ Status handling

#### Web API Tests (`test_web_api.py`)
- ✅ Flask app initialization
- ✅ Route testing
- ✅ File upload handling
- ✅ API endpoints
- ✅ Error responses
- ✅ File format validation
- ✅ Security headers
- ✅ Rate limiting
- ✅ Memory management
- ✅ Concurrent requests

### 2. GUI Tests (`test_gui.py`)

#### Desktop Application Tests
- ✅ Application initialization
- ✅ Window creation
- ✅ Menu system
- ✅ File selection components
- ✅ Progress tracking
- ✅ Output directory selection
- ✅ Configuration loading
- ✅ Dialog functionality
- ✅ Error handling
- ✅ Threading safety
- ✅ Transcription workflow

### 3. Integration Tests

#### Core Functionality (`debug_transcription.py`)
- ✅ End-to-end transcription
- ✅ API connectivity
- ✅ Audio processing pipeline
- ✅ Error diagnosis
- ✅ Configuration validation

#### Audio Content Analysis (`check_audio_content.py`)
- ✅ Audio content detection
- ✅ Volume analysis
- ✅ Speech detection
- ✅ File format support
- ✅ Quality assessment

### 4. Web Deployment Tests (`scripts/test_deployment.sh`)

#### Production Deployment
- ✅ Docker container health
- ✅ API endpoint testing
- ✅ SSL certificate generation
- ✅ nginx configuration
- ✅ Production deployment
- ✅ Load balancing
- ✅ Security validation
- ✅ Kubernetes deployment

## 📊 Test Coverage

### Current Coverage Areas

| Component | Unit Tests | Integration Tests | GUI Tests | Web Tests |
|-----------|------------|------------------|-----------|-----------|
| **Config** | ✅ | ✅ | ✅ | ✅ |
| **Audio Handler** | ✅ | ✅ | ✅ | ✅ |
| **Transcriber** | ✅ | ✅ | ✅ | ✅ |
| **GUI Application** | ❌ | ✅ | ✅ | ❌ |
| **Web API** | ✅ | ✅ | ❌ | ✅ |
| **Deployment** | ❌ | ✅ | ❌ | ✅ |

### Coverage Goals
- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: Full workflow coverage
- **GUI Tests**: Complete UI interaction coverage
- **Web Tests**: All endpoints and deployment scenarios

## 🔧 Running Tests

### Method 1: Main Test Runner (Recommended)

```bash
# Run all tests with comprehensive reporting
python run_tests.py

# Run specific test categories
python run_tests.py --unit --verbose
python run_tests.py --gui
python run_tests.py --integration
python run_tests.py --web

# Skip dependency check
python run_tests.py --skip-deps
```

### Method 2: Direct pytest

```bash
# Run unit tests only
pytest tests/

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with verbose output
pytest tests/ -v
```

### Method 3: Individual Test Scripts

```bash
# GUI tests
python test_gui.py

# Integration tests
python debug_transcription.py
python check_audio_content.py

# Web deployment tests
bash scripts/test_deployment.sh
```

## 📋 Test Configuration

### pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
addopts = --strict-markers --tb=short --cov=src --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    gui: marks tests as GUI tests
    web: marks tests as web API tests
    network: marks tests that require network access
```

### Environment Variables for Testing
```bash
# Optional: Set test API key
export ASSEMBLYAI_API_KEY=test_key_here

# Optional: Set test output directory
export OUTPUT_DIRECTORY=/tmp/test_output

# Optional: Enable test mode
export TESTING=true
```

## 🎯 Test Execution Examples

### Complete Test Suite
```bash
# Run everything
python run_tests.py

# Expected output:
# 🚀 Recall Application Test Suite
# 🔍 Checking test dependencies...
# 🧪 RUNNING UNIT TESTS
# 🖥️  RUNNING GUI TESTS
# 🔗 RUNNING INTEGRATION TESTS
# 🌐 RUNNING WEB DEPLOYMENT TESTS
# 📊 TEST REPORT
# 🎉 All tests completed successfully!
```

### Unit Tests Only
```bash
# Fast unit tests
python run_tests.py --unit --verbose

# Or directly with pytest
pytest tests/ -v
```

### GUI Tests Only
```bash
# Desktop GUI tests
python run_tests.py --gui

# Or directly
python test_gui.py
```

### Integration Tests Only
```bash
# Core functionality tests
python run_tests.py --integration

# Or run individually
python debug_transcription.py
python check_audio_content.py
```

### Web Deployment Tests Only
```bash
# Production deployment validation
python run_tests.py --web

# Or directly (requires Docker)
bash scripts/test_deployment.sh
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Missing Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or skip dependency check
python run_tests.py --skip-deps
```

#### 2. GUI Tests Fail on Headless Systems
```bash
# Set display variable (Linux)
export DISPLAY=:0

# Or use virtual display
xvfb-run python test_gui.py
```

#### 3. Web Tests Fail Without Docker
```bash
# Install Docker first
# Then run web tests
python run_tests.py --web
```

#### 4. Permission Issues
```bash
# Make scripts executable
chmod +x scripts/test_deployment.sh
```

### Debug Mode
```bash
# Run tests with maximum verbosity
python run_tests.py --verbose

# Run specific test with debug info
pytest tests/test_config.py -v -s
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
```

### Local Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
python run_tests.py --unit
```

## 🔍 Writing New Tests

### Adding Unit Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures and assertions
4. Add appropriate markers

### Adding GUI Tests
1. Add test methods to `test_gui.py`
2. Use mocking for external dependencies
3. Test user interactions and workflows

### Adding Integration Tests
1. Create new script or add to existing ones
2. Test complete workflows
3. Include in `run_tests.py`

## 📚 Best Practices

### Test Organization
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **GUI tests**: Test user interface interactions
- **Web tests**: Test API endpoints and deployment

### Test Naming
- Use descriptive test names
- Follow pattern: `test_<what_is_being_tested>`
- Include expected behavior in name

### Mocking
- Mock external dependencies (APIs, file system)
- Use `pytest-mock` for clean mocking
- Mock at appropriate abstraction level

### Assertions
- Use specific assertions
- Include helpful error messages
- Test both success and failure cases

## 🏆 Test Quality Metrics

### Success Criteria
- **All tests pass**: 100% test suite success
- **Code coverage**: >80% line coverage
- **Performance**: Tests complete in <5 minutes
- **Reliability**: Tests pass consistently

### Monitoring
- Track test execution time
- Monitor code coverage trends
- Identify flaky tests
- Regular test maintenance

---

## 📞 Support

For testing-related questions:
1. Check existing test files for examples
2. Review this documentation
3. Run tests with `--verbose` for detailed output
4. Use `pytest --help` for pytest options

Happy testing! 🎉 