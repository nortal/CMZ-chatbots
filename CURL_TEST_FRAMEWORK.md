# 🧪 cURL Test Framework - Ready for Use

**Branch**: `kcs/curl-test-framework`  
**Status**: ✅ **Committed and Ready**  
**GitHub**: https://github.com/nortal/CMZ-chatbots/tree/kcs/curl-test-framework

## 🎯 Quick Commands for Claude

### Run Tests
```bash
# Start here (ensure API is running first)
cd /Users/keithstegbauer/repositories/CMZ-chatbots
make run-api

# Run integration tests
cd backend/api/src/main/python
python run_integration_tests.py --html-report
```

### View Results
- **Main Report**: `backend/api/src/main/python/reports/integration_test_report.html`
- **cURL Logs**: `backend/api/src/main/python/reports/curl_api_logs.json`
- **API Analysis**: `backend/api/src/main/python/reports/API_TESTING_SUMMARY.md`

### Detailed Usage Notes
See: `backend/api/src/main/python/CLAUDE_TEST_NOTES.md`

## 📊 Framework Value

### ✅ What It Provides
- **Real cURL commands** against running API (not mock testing)
- **Complete request/response logging** for every test
- **Professional HTML reports** ready for stakeholder sharing
- **Jira ticket validation** mapping to 26 specific requirements
- **Actual API behavior analysis** showing what works vs what's broken

### 🎯 Key Discoveries
- **`/animal_list`** endpoint working with 2 sample animals
- **Error schema** completely non-compliant with PR003946-90 requirements
- **`/user`** endpoints returning 500 errors (implementation broken)
- **Authentication** missing password policy enforcement
- **43% test pass rate** (20/47 tests passing)

### 📋 Reports Generated
1. **HTML Test Report** - Visual pass/fail with cURL commands
2. **cURL Command Log** - JSON file with all HTTP requests/responses  
3. **API Analysis Summary** - Executive summary with implementation priorities
4. **Coverage Report** - Code coverage analysis

## 🚀 Usage Scenarios

### For Project Status Updates
```bash
python run_integration_tests.py --html-report
# Share: reports/integration_test_report.html
```

### For API Behavior Analysis
```bash
python -m pytest tests/integration/test_curl_demo.py -v -s
# Shows: Real cURL commands + responses
```

### For Jira Ticket Validation
```bash
python run_integration_tests.py --ticket PR003946-90
# Tests: Specific requirement implementation
```

### For Debugging
```bash
cat reports/curl_api_logs.json
# Contains: Every cURL command executed with full output
```

## 🎯 Next Steps

1. **Immediate**: Use framework for current development status
2. **Short-term**: Fix error schema compliance (PR003946-90)
3. **Medium-term**: Implement missing user endpoints  
4. **Long-term**: Achieve >80% test pass rate

---

**Created**: September 10, 2025  
**Purpose**: Enable comprehensive API testing with real HTTP commands  
**Value**: Shows actual vs expected API behavior for informed development decisions  

Ready to use! Just run the commands above when you need to test the API. 🧪✨