#!/bin/bash

# TDD Framework Validation Script
# Comprehensive validation of the CMZ TDD system

echo "🎯 CMZ TDD FRAMEWORK VALIDATION"
echo "================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validation results
VALIDATION_RESULTS=()

# Function to log validation result
log_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"

    VALIDATION_RESULTS+=("$test_name|$status|$message")

    if [[ "$status" == "PASS" ]]; then
        echo -e "  ✅ ${GREEN}PASS${NC}: $test_name"
    elif [[ "$status" == "FAIL" ]]; then
        echo -e "  ❌ ${RED}FAIL${NC}: $test_name - $message"
    elif [[ "$status" == "WARN" ]]; then
        echo -e "  ⚠️  ${YELLOW}WARN${NC}: $test_name - $message"
    else
        echo -e "  ℹ️  ${BLUE}INFO${NC}: $test_name - $message"
    fi
}

echo -e "\n📁 ${BLUE}1. DIRECTORY STRUCTURE VALIDATION${NC}"
echo "   Checking TDD framework directory structure..."

# Check main tests directory
if [[ -d "tests" ]]; then
    log_result "Main tests directory" "PASS" "tests/ directory exists"
else
    log_result "Main tests directory" "FAIL" "tests/ directory missing"
fi

# Check category directories
categories=("integration" "unit" "playwright" "security")
for category in "${categories[@]}"; do
    if [[ -d "tests/$category" ]]; then
        count=$(find "tests/$category" -name "PR003946-*" -type d | wc -l)
        log_result "$category directory" "PASS" "$count ticket directories found"
    else
        log_result "$category directory" "FAIL" "tests/$category directory missing"
    fi
done

# Check batch reports directory
if [[ -d "tests/batch_reports" ]]; then
    log_result "Batch reports directory" "PASS" "tests/batch_reports exists"
else
    log_result "Batch reports directory" "WARN" "tests/batch_reports not created yet"
fi

echo -e "\n🧪 ${BLUE}2. CORE SCRIPTS VALIDATION${NC}"
echo "   Checking TDD framework executables..."

# Check execute_test.py
if [[ -f "tests/execute_test.py" && -x "tests/execute_test.py" ]]; then
    log_result "Test executor script" "PASS" "execute_test.py exists and executable"
else
    log_result "Test executor script" "FAIL" "execute_test.py missing or not executable"
fi

# Check batch runner
if [[ -f "tests/run_batch_tests.py" && -x "tests/run_batch_tests.py" ]]; then
    log_result "Batch runner script" "PASS" "run_batch_tests.py exists and executable"
else
    log_result "Batch runner script" "FAIL" "run_batch_tests.py missing or not executable"
fi

# Check dashboard generator
if [[ -f "tests/tdd_dashboard.py" && -x "tests/tdd_dashboard.py" ]]; then
    log_result "Dashboard generator" "PASS" "tdd_dashboard.py exists and executable"
else
    log_result "Dashboard generator" "FAIL" "tdd_dashboard.py missing or not executable"
fi

echo -e "\n📋 ${BLUE}3. TEST SPECIFICATIONS VALIDATION${NC}"
echo "   Validating generated test specifications..."

total_tickets=0
tickets_with_specs=0
tickets_with_howto=0
tickets_with_advice=0

# Count tickets and specifications
for category in "${categories[@]}"; do
    if [[ -d "tests/$category" ]]; then
        for ticket_dir in tests/$category/PR003946-*; do
            if [[ -d "$ticket_dir" ]]; then
                total_tickets=$((total_tickets + 1))

                ticket_name=$(basename "$ticket_dir")
                howto_file="$ticket_dir/${ticket_name}-howto-test.md"
                advice_file="$ticket_dir/${ticket_name}-ADVICE.md"

                if [[ -f "$howto_file" && -f "$advice_file" ]]; then
                    tickets_with_specs=$((tickets_with_specs + 1))
                fi

                if [[ -f "$howto_file" ]]; then
                    tickets_with_howto=$((tickets_with_howto + 1))
                fi

                if [[ -f "$advice_file" ]]; then
                    tickets_with_advice=$((tickets_with_advice + 1))
                fi
            fi
        done
    fi
done

if [[ $total_tickets -gt 0 ]]; then
    coverage_percentage=$(( (tickets_with_specs * 100) / total_tickets ))
    log_result "Test specifications coverage" "INFO" "$tickets_with_specs/$total_tickets tickets ($coverage_percentage%)"

    if [[ $coverage_percentage -ge 90 ]]; then
        log_result "Specification completeness" "PASS" "Excellent coverage (≥90%)"
    elif [[ $coverage_percentage -ge 70 ]]; then
        log_result "Specification completeness" "PASS" "Good coverage (≥70%)"
    elif [[ $coverage_percentage -ge 50 ]]; then
        log_result "Specification completeness" "WARN" "Moderate coverage (≥50%)"
    else
        log_result "Specification completeness" "FAIL" "Low coverage (<50%)"
    fi
else
    log_result "Test specifications" "FAIL" "No ticket directories found"
fi

echo -e "\n🔗 ${BLUE}4. JIRA INTEGRATION VALIDATION${NC}"
echo "   Checking Jira data and integration..."

# Check Jira data files
if [[ -f "jira_data/all_tickets_complete.txt" ]]; then
    jira_ticket_count=$(wc -l < "jira_data/all_tickets_complete.txt")
    log_result "Jira ticket list" "PASS" "$jira_ticket_count tickets in all_tickets_complete.txt"
else
    log_result "Jira ticket list" "FAIL" "jira_data/all_tickets_complete.txt missing"
fi

if [[ -f "jira_data/all_tickets_consolidated.json" ]]; then
    log_result "Jira ticket data" "PASS" "all_tickets_consolidated.json exists"
else
    log_result "Jira ticket data" "FAIL" "jira_data/all_tickets_consolidated.json missing"
fi

# Check NORTAL-JIRA-ADVICE.md
if [[ -f "NORTAL-JIRA-ADVICE.md" ]]; then
    log_result "Jira integration guide" "PASS" "NORTAL-JIRA-ADVICE.md exists"
else
    log_result "Jira integration guide" "WARN" "NORTAL-JIRA-ADVICE.md missing"
fi

echo -e "\n⚙️ ${BLUE}5. FUNCTIONAL VALIDATION${NC}"
echo "   Testing core TDD framework functionality..."

# Test execute_test.py help
if [[ -f "tests/execute_test.py" ]]; then
    if python3 tests/execute_test.py --help &>/dev/null; then
        log_result "Test executor help" "PASS" "execute_test.py responds to --help"
    else
        if python3 tests/execute_test.py 2>&1 | grep -q "Usage:"; then
            log_result "Test executor help" "PASS" "execute_test.py shows usage information"
        else
            log_result "Test executor help" "WARN" "execute_test.py may have execution issues"
        fi
    fi
fi

# Test batch runner help
if [[ -f "tests/run_batch_tests.py" ]]; then
    if python3 tests/run_batch_tests.py --help &>/dev/null; then
        log_result "Batch runner help" "PASS" "run_batch_tests.py responds to --help"
    else
        log_result "Batch runner help" "WARN" "run_batch_tests.py help may not work"
    fi
fi

# Test dashboard generator
if [[ -f "tests/tdd_dashboard.py" ]]; then
    if python3 tests/tdd_dashboard.py --help &>/dev/null || python3 -c "import sys; sys.path.append('tests'); import tdd_dashboard" &>/dev/null; then
        log_result "Dashboard generator" "PASS" "tdd_dashboard.py can be imported/executed"
    else
        log_result "Dashboard generator" "WARN" "tdd_dashboard.py may have import issues"
    fi
fi

echo -e "\n🎭 ${BLUE}6. SAMPLE TEST VALIDATION${NC}"
echo "   Attempting sample test execution..."

# Find a test ticket to validate
sample_ticket=""
for category in "${categories[@]}"; do
    if [[ -d "tests/$category" ]]; then
        for ticket_dir in tests/$category/PR003946-*; do
            if [[ -d "$ticket_dir" ]]; then
                ticket_name=$(basename "$ticket_dir")
                howto_file="$ticket_dir/${ticket_name}-howto-test.md"
                if [[ -f "$howto_file" ]]; then
                    sample_ticket="$ticket_name"
                    break 2
                fi
            fi
        done
    fi
done

if [[ -n "$sample_ticket" ]]; then
    log_result "Sample ticket found" "PASS" "$sample_ticket available for testing"

    # Try to run a dry validation (without actually executing)
    echo "   🔍 Attempting dry validation of $sample_ticket..."

    # Check if prerequisites would be testable
    if command -v curl >/dev/null 2>&1; then
        log_result "Prerequisites check" "PASS" "curl available for API testing"
    else
        log_result "Prerequisites check" "WARN" "curl not available - API tests may fail"
    fi

    if [[ -f ".env.local" ]]; then
        log_result "Environment configuration" "PASS" ".env.local exists"
    else
        log_result "Environment configuration" "WARN" ".env.local missing - may affect testing"
    fi
else
    log_result "Sample validation" "FAIL" "No complete test specifications found"
fi

echo -e "\n📊 ${BLUE}7. SUMMARY AND RECOMMENDATIONS${NC}"
echo "   Analyzing validation results..."

# Count results by status
pass_count=0
fail_count=0
warn_count=0
info_count=0

for result in "${VALIDATION_RESULTS[@]}"; do
    status=$(echo "$result" | cut -d'|' -f2)
    case "$status" in
        "PASS") pass_count=$((pass_count + 1)) ;;
        "FAIL") fail_count=$((fail_count + 1)) ;;
        "WARN") warn_count=$((warn_count + 1)) ;;
        "INFO") info_count=$((info_count + 1)) ;;
    esac
done

total_count=${#VALIDATION_RESULTS[@]}
pass_percentage=$(( (pass_count * 100) / total_count ))

echo
echo "📈 VALIDATION SUMMARY:"
echo "   ✅ Passed: $pass_count"
echo "   ❌ Failed: $fail_count"
echo "   ⚠️  Warnings: $warn_count"
echo "   ℹ️  Info: $info_count"
echo "   📊 Pass Rate: $pass_percentage% ($pass_count/$total_count)"

echo
echo "🎯 SEQUENTIAL REASONING ASSESSMENT:"

if [[ $fail_count -eq 0 ]] && [[ $pass_percentage -ge 80 ]]; then
    echo "   ✅ TDD Framework Status: EXCELLENT"
    echo "   📋 Assessment: Framework is ready for systematic testing"
    echo "   🚀 Recommendation: Begin comprehensive test execution"
elif [[ $fail_count -le 2 ]] && [[ $pass_percentage -ge 70 ]]; then
    echo "   ✅ TDD Framework Status: GOOD"
    echo "   📋 Assessment: Framework is operational with minor issues"
    echo "   🔧 Recommendation: Address warnings and begin selective testing"
elif [[ $fail_count -le 5 ]] && [[ $pass_percentage -ge 50 ]]; then
    echo "   ⚠️  TDD Framework Status: FUNCTIONAL"
    echo "   📋 Assessment: Framework has basic functionality but needs improvements"
    echo "   🛠️  Recommendation: Fix critical failures before systematic testing"
else
    echo "   ❌ TDD Framework Status: NEEDS ATTENTION"
    echo "   📋 Assessment: Framework requires significant fixes"
    echo "   🚨 Recommendation: Address all failures before proceeding"
fi

echo
echo "🔄 NEXT STEPS:"
if [[ $fail_count -eq 0 ]]; then
    echo "   1. Execute sample test: python3 tests/execute_test.py $sample_ticket"
    echo "   2. Run batch tests: python3 tests/run_batch_tests.py --max 5"
    echo "   3. Generate dashboard: python3 tests/tdd_dashboard.py"
else
    echo "   1. Address failed validation items above"
    echo "   2. Re-run validation: ./tests/run_tdd_validation.sh"
    echo "   3. Once passing, begin systematic testing"
fi

# Save validation report
timestamp=$(date '+%Y-%m-%d_%H%M%S')
report_file="tests/validation_report_${timestamp}.txt"

{
    echo "CMZ TDD FRAMEWORK VALIDATION REPORT"
    echo "Generated: $(date)"
    echo "=================================="
    echo
    for result in "${VALIDATION_RESULTS[@]}"; do
        name=$(echo "$result" | cut -d'|' -f1)
        status=$(echo "$result" | cut -d'|' -f2)
        message=$(echo "$result" | cut -d'|' -f3)
        echo "$status: $name - $message"
    done
    echo
    echo "SUMMARY:"
    echo "Passed: $pass_count, Failed: $fail_count, Warnings: $warn_count, Info: $info_count"
    echo "Pass Rate: $pass_percentage%"
} > "$report_file"

echo
echo "💾 Validation report saved: $report_file"

# Exit with appropriate code
if [[ $fail_count -eq 0 ]]; then
    exit 0  # All passed
elif [[ $fail_count -le 2 ]]; then
    exit 1  # Minor issues
else
    exit 2  # Major issues
fi