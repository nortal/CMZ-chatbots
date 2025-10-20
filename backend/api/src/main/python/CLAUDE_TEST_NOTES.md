# Claude Test Framework Usage Notes

**Branch**: `kcs/curl-test-framework`  
**Created**: September 10, 2025  
**Purpose**: Complete cURL-based integration test framework for CMZ API

## 🎯 Quick Start Commands for Claude

When asked to run tests, use these exact commands:

### 1. Start API Server (if not running)
```bash
cd /Users/keithstegbauer/repositories/CMZ-chatbots
make run-api
# Verify API is running: curl -I http://localhost:8080
```

### 2. Run cURL Integration Tests
```bash
cd backend/api/src/main/python

# Run all tests with cURL logging
python run_integration_tests.py --html-report

# Run just cURL demo tests to see API behavior
python -m pytest tests/integration/test_curl_demo.py -v -s

# Generate comprehensive report with coverage
python run_integration_tests.py --report
```

### 3. View Results
- **HTML Report**: `reports/integration_test_report.html`
- **cURL Logs**: `reports/curl_api_logs.json` 
- **Coverage**: `reports/coverage/index.html`
- **Summary**: `reports/API_TESTING_SUMMARY.md`

## 🔧 Test Framework Components

### Core Files Added
```
backend/api/src/main/python/
├── tests/
│   ├── conftest.py                    # cURL client + logging fixtures
│   ├── integration/
│   │   ├── test_curl_demo.py          # Real API behavior tests
│   │   ├── test_api_validation_epic.py # Jira ticket validation
│   │   └── test_endpoints.py          # Endpoint integration tests
│   ├── pytest.ini                    # Test configuration
│   └── README.md                      # Framework documentation
├── run_integration_tests.py          # Test runner with options
├── requirements-test.txt              # Test dependencies
└── reports/                           # Generated test reports
```

### New Fixtures Available
- **`curl_client`**: Real cURL-based HTTP client
- **`api_logger`**: Logs all cURL commands and responses
- **`validation_helper`**: Validates responses against Jira requirements

## 📊 Test Categories

### cURL Demo Tests (`test_curl_demo.py`)
Real API behavior analysis:
- Root endpoint connectivity
- Error response format analysis 
- Working vs broken endpoints
- Authentication behavior
- Health check discovery

### Jira Validation Tests (`test_api_validation_epic.py`) 
Direct mapping to 26 Jira tickets:
- PR003946-66-68: Soft-delete semantics
- PR003946-69-70: Server-generated IDs
- PR003946-71,72,87,88: Authentication
- PR003946-73-75: Data integrity
- PR003946-79-80: Family management
- PR003946-81-82: Pagination
- PR003946-83-85: Analytics
- PR003946-86: Billing validation
- PR003946-89,91: Input validation
- PR003946-90: Error schema consistency

### Endpoint Tests (`test_endpoints.py`)
Integration testing by functional area:
- Authentication endpoints
- User management
- Animal configuration
- Family management
- Analytics and reporting
- System health

## 🎯 Common Usage Scenarios

### Scenario 1: "Run the tests"
```bash
cd backend/api/src/main/python
python run_integration_tests.py --html-report
```
**Result**: HTML report showing pass/fail with cURL commands

### Scenario 2: "Show me what's working in the API"
```bash
python -m pytest tests/integration/test_curl_demo.py::TestCurlApiDemo::test_animal_endpoints -v -s
```
**Result**: Console output showing successful `/animal_list` cURL

### Scenario 3: "Test against Jira requirements"
```bash
python run_integration_tests.py --validation --ticket PR003946-90
```
**Result**: Specific ticket validation with cURL logging

### Scenario 4: "Generate comprehensive status report"
```bash
python run_integration_tests.py --report
open reports/integration_report.html
```
**Result**: Full HTML + coverage + cURL logs + summary

### Scenario 5: "Debug specific endpoint"
```bash
python -m pytest tests/integration/test_curl_demo.py::TestCurlApiDemo::test_user_endpoint_structure -v -s
```
**Result**: Real cURL command + response for `/user` endpoint

## 📋 Test Execution Patterns

### Development Workflow
1. **TDD Mode**: `python run_integration_tests.py --tdd`
2. **Fix Implementation**: Code changes
3. **Verify**: `python -m pytest tests/integration/test_curl_demo.py -v -s`
4. **Report**: `python run_integration_tests.py --html-report`

### Status Reporting
1. **Quick Check**: `curl -I http://localhost:8080` (API health)
2. **Full Test**: `python run_integration_tests.py --html-report`
3. **Share Results**: Open `reports/integration_test_report.html`

### Debugging
1. **View Logs**: `cat reports/curl_api_logs.json`
2. **Single Test**: `python -m pytest <test_path> -v -s`
3. **Error Analysis**: Check `reports/API_TESTING_SUMMARY.md`

## 🔍 Key Test Insights (as of Sep 10, 2025)

### ✅ Working Endpoints
- **`GET /`**: Returns `"do some magic!"`
- **`GET /animal_list`**: Returns 2 sample animals with proper structure
- **Basic Error Handling**: Consistent format (but wrong schema)

### ❌ Critical Issues
- **Error Schema**: Uses Flask default, not PR003946-90 requirements
- **`GET /user`**: Returns 500 Internal Server Error
- **Authentication**: Missing password policy enforcement
- **Validation**: Input validation gaps across multiple tickets

### 📊 Current Metrics
- **Total Tests**: 47 integration tests
- **Passing**: ~20 (43%)
- **Critical Path**: Error schema compliance, user endpoints, authentication

## 💡 Pro Tips for Claude

### When Running Tests
1. **Always check API first**: `curl -I http://localhost:8080`
2. **Use `-s` flag**: Shows cURL output in real-time
3. **Check reports dir**: Results auto-generate with timestamps
4. **Read logs**: `curl_api_logs.json` has exact commands to replicate

### When Analyzing Results
1. **Focus on cURL output**: Shows real API behavior
2. **Check status codes**: 200 = working, 500 = broken, 404 = missing
3. **Compare error formats**: Current vs required (PR003946-90)
4. **Track progress**: Pass rate improvements over time

### When Reporting
1. **Use HTML reports**: Professional, shareable format
2. **Include cURL examples**: Concrete evidence of behavior
3. **Reference Jira tickets**: Direct mapping to requirements
4. **Show before/after**: Progress demonstration

## 🚀 Future Enhancements

### Planned Additions
- [ ] Performance testing with cURL timing
- [ ] Authentication token testing
- [ ] Database state validation
- [ ] CI/CD integration scripts

### Test Coverage Goals
- [ ] All 26 Jira tickets validated
- [ ] >80% pass rate target  
- [ ] Zero 500 errors on core endpoints
- [ ] Error schema compliance across all endpoints

---

**Created for**: Keith "KC" Stegbauer  
**Branch**: `kcs/curl-test-framework`  
**Purpose**: Enable Claude to effectively run and analyze CMZ API integration tests  
**Key Value**: Real cURL commands show actual API behavior vs theoretical requirements