# Comprehensive Code Review - Implementation Advice

**Purpose**: Best practices, troubleshooting, and implementation guidance for multi-phase systematic code review with OpenAI integration

**Related Command**: `.claude/commands/comprehensive-code-review.md`

---

## Overview

The comprehensive code review system uses a **hybrid approach (Option C)** combining:
1. **Native tools** (Grep, Glob, Read) for structure and pattern detection
2. **MCP Sequential** for complex architectural reasoning
3. **OpenAI API** for deep code analysis and duplication detection

This approach handles codebases too large for single-pass analysis by breaking review into systematic phases.

---

## Prerequisites

### Required Tools
```bash
# Check all required tools are available
command -v python3 >/dev/null 2>&1 || echo "❌ Python 3 required"
command -v jq >/dev/null 2>&1 || echo "❌ jq required (brew install jq)"
command -v curl >/dev/null 2>&1 || echo "✅ curl available"

# Check Python packages
pip list | grep -E "openai|numpy" || echo "❌ Install: pip install openai numpy"
```

### Environment Variables
```bash
# Required for OpenAI analysis
export OPENAI_API_KEY="sk-..."

# Required for Teams reporting
export TEAMS_WEBHOOK_URL="https://..."

# Verify configuration
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..."
echo "TEAMS_WEBHOOK_URL: ${TEAMS_WEBHOOK_URL:0:50}..."
```

### Directory Structure Setup
```bash
# Create reports directory
mkdir -p reports/code-review

# Create scripts directory (if not exists)
mkdir -p scripts

# Verify structure
ls -la reports/code-review/
ls -la scripts/
```

---

## Phase 1: Discovery & Architecture Mapping

### Implementation Best Practices

**1. Start with Structure Generation**
```bash
# Always run from project root
cd /Users/keithstegbauer/repositories/CMZ-chatbots

# Generate structure report
find backend/api/src/main/python -name "*.py" | grep -v __pycache__ | grep -v __init__ | sort > reports/code-review/backend-files.txt
find frontend/src -type f \( -name "*.tsx" -o -name "*.ts" \) | sort > reports/code-review/frontend-files.txt

# Count files by category
echo "Backend implementation: $(find backend/api/src/main/python/openapi_server/impl -name "*.py" | wc -l) files"
echo "Frontend source: $(find frontend/src -name "*.tsx" -o -name "*.ts" | wc -l) files"
echo "Test files: $(find backend/api/src/main/python/tests -name "*.py" -o -name "*.js" | wc -l) files"
```

**2. Calculate Meaningful Metrics**
```bash
# Lines of code (excluding blank lines and comments)
count_loc() {
  find "$1" -name "$2" -exec cat {} + | grep -v "^\s*#" | grep -v "^\s*$" | wc -l
}

# Usage
count_loc "backend/api/src/main/python/openapi_server/impl" "*.py"
count_loc "frontend/src" "*.tsx"
```

**3. Identify True Hot Spots**
```bash
# Find files with high cyclomatic complexity
find_complex_files() {
  find "$1" -name "*.py" -exec sh -c '
    count=$(grep -c "if \|elif \|else:\|try:\|except\|for \|while " "$1")
    if [ $count -gt 20 ]; then
      echo "$count complexity indicators: $1"
    fi
  ' _ {} \; | sort -rn
}

find_complex_files "backend/api/src/main/python/openapi_server/impl"
```

### Common Issues & Solutions

**Issue**: File counts include `__pycache__` and generated code
```bash
# ❌ Wrong: Includes all files
find backend -name "*.py" | wc -l

# ✅ Right: Excludes generated and cache
find backend/api/src/main/python/openapi_server/impl -name "*.py" | grep -v __pycache__ | wc -l
```

**Issue**: Metrics include blank lines and comments
```bash
# ❌ Wrong: Raw line count
wc -l file.py

# ✅ Right: Exclude blank lines and comments
grep -v "^\s*#" file.py | grep -v "^\s*$" | wc -l
```

**Issue**: Missing dependency information
```bash
# Solution: Generate import graph
grep -rh "^import \|^from " backend/api/src/main/python/openapi_server/impl --include="*.py" | sort | uniq -c | sort -rn > reports/code-review/imports.txt
```

---

## Phase 2: Module-by-Module Analysis

### OpenAI Script Implementation

**1. Create the Analysis Script**

The script provided in the command file (`scripts/openai_code_review.py`) requires:
- Python 3.8+
- OpenAI Python SDK (`pip install openai`)
- Environment variable `OPENAI_API_KEY`

**2. Handle Large Files**

OpenAI has token limits. For large files:
```python
def chunk_code(code: str, max_lines: int = 500) -> List[str]:
    """Split large files into analyzable chunks"""
    lines = code.split('\n')
    chunks = []

    for i in range(0, len(lines), max_lines):
        chunk = '\n'.join(lines[i:i+max_lines])
        chunks.append(chunk)

    return chunks

# Analyze each chunk separately
for i, chunk in enumerate(chunk_code(code)):
    result = analyze_code_chunk(chunk, f"{file_path}:part{i}")
```

**3. Cost Management**

OpenAI API calls cost money. Estimate before running:
```python
# Rough cost estimation
def estimate_cost(file_path: str) -> float:
    """Estimate API cost for analyzing a file"""
    with open(file_path) as f:
        lines = len(f.readlines())

    # GPT-4: ~$0.03 per 1K tokens
    # Average: 1 line ≈ 4 tokens
    tokens = lines * 4 * 2  # Input + Output
    cost = (tokens / 1000) * 0.03

    return cost

# Check total cost before running
total_cost = sum(estimate_cost(f) for f in files_to_analyze)
print(f"Estimated cost: ${total_cost:.2f}")
```

### Batch Processing Strategy

**Option A: Sequential (Safer)**
```bash
# Process one file at a time
for file in $(cat reports/code-review/backend-files.txt); do
  python scripts/openai_code_review.py \
    --file "$file" \
    --focus "style,security,dry,solid" \
    --output "reports/code-review/$(basename $file).json"

  # Rate limiting: 60 requests per minute
  sleep 1
done
```

**Option B: Parallel (Faster, but watch rate limits)**
```bash
# Process multiple files in parallel
cat reports/code-review/backend-files.txt | \
  xargs -P 3 -I {} python scripts/openai_code_review.py \
    --file {} \
    --focus "style,security,dry,solid" \
    --output "reports/code-review/{}.json"
```

### Common Issues & Solutions

**Issue**: OpenAI rate limit errors
```python
# Solution: Add exponential backoff
import time
from openai import RateLimitError

def analyze_with_retry(file_path: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return analyze_code(file_path)
        except RateLimitError:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Rate limit hit. Waiting {wait_time}s...")
            time.sleep(wait_time)

    raise Exception(f"Failed after {max_retries} retries")
```

**Issue**: API timeout on large files
```python
# Solution: Increase timeout and chunk code
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=60.0  # Increase from default 30s
)
```

**Issue**: JSON parsing errors in responses
```python
# Solution: Validate and handle malformed JSON
try:
    result = json.loads(response.choices[0].message.content)
except json.JSONDecodeError:
    # Fallback: Return raw text
    result = {
        "file": file_path,
        "summary": response.choices[0].message.content,
        "issues": []
    }
```

---

## Phase 3: Cross-Cutting Analysis

### Security Scanning Best Practices

**1. Pattern-Based Detection**
```bash
# Create comprehensive security scan
security_scan() {
  echo "=== Security Scan Results ===" > reports/code-review/security.md

  # Secrets detection
  echo "\n## Hardcoded Secrets" >> reports/code-review/security.md
  grep -rn "password\s*=\s*['\"]" \
       -E "api[_-]?key\s*=\s*['\"]" \
       -E "secret\s*=\s*['\"]" \
       backend frontend --include="*.py" --include="*.ts" --include="*.tsx" \
       --exclude="*test*" --exclude="*.md" >> reports/code-review/security.md

  # SQL injection patterns (should be none - using DynamoDB)
  echo "\n## SQL Injection Risks" >> reports/code-review/security.md
  grep -rn "execute.*format\|%s.*SELECT\|f\".*SELECT" \
       backend/api/src/main/python --include="*.py" >> reports/code-review/security.md || \
       echo "✅ No SQL injection patterns found" >> reports/code-review/security.md

  # XSS vulnerabilities
  echo "\n## XSS Vulnerabilities" >> reports/code-review/security.md
  grep -rn "dangerouslySetInnerHTML\|innerHTML\|eval(" \
       frontend/src --include="*.tsx" --include="*.ts" >> reports/code-review/security.md || \
       echo "✅ No XSS patterns found" >> reports/code-review/security.md
}
```

**2. Authentication Review**
```bash
# Check for proper auth patterns
echo "\n## Authentication Implementation" >> reports/code-review/security.md

# Find endpoints without auth
grep -rn "def.*post\|def.*get\|def.*put\|def.*delete" \
  backend/api/src/main/python/openapi_server/controllers --include="*.py" -A 10 | \
  grep -v "X-User-Id\|auth.*required\|@require" >> reports/code-review/security.md
```

### Code Duplication Detection

**1. Function Extraction Strategy**
```python
# Improved function extraction with context
def extract_functions_with_context(file_path: str) -> List[Dict]:
    """Extract functions with surrounding context"""
    import ast

    with open(file_path) as f:
        tree = ast.parse(f.read())

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'line': node.lineno,
                'args': [arg.arg for arg in node.args.args],
                'decorators': [d.id for d in node.decorator_list if hasattr(d, 'id')],
                'code': ast.get_source_segment(code, node)
            })

    return functions
```

**2. Similarity Thresholds**
```python
# Different thresholds for different purposes
THRESHOLDS = {
    'exact_duplicate': 0.95,    # Nearly identical (immediate refactor)
    'high_similarity': 0.85,    # Very similar (review for refactor)
    'moderate_similarity': 0.70, # Some overlap (potential shared utility)
    'low_similarity': 0.50       # Minimal overlap (probably OK)
}

def categorize_similarity(score: float) -> str:
    """Categorize similarity score"""
    if score >= THRESHOLDS['exact_duplicate']:
        return 'CRITICAL: Exact duplicate'
    elif score >= THRESHOLDS['high_similarity']:
        return 'HIGH: High similarity'
    elif score >= THRESHOLDS['moderate_similarity']:
        return 'MEDIUM: Moderate similarity'
    else:
        return 'LOW: Low similarity'
```

**3. False Positive Filtering**
```python
# Exclude common patterns from duplication detection
def should_skip_function(func: Dict) -> bool:
    """Skip functions that are expected to be similar"""
    skip_patterns = [
        'test_',           # Test functions often similar
        '__init__',        # Constructors
        'get_',            # Simple getters
        'set_',            # Simple setters
        'serialize',       # Serialization methods
        'to_dict',         # Conversion methods
    ]

    return any(pattern in func['name'] for pattern in skip_patterns)
```

### DRY Violation Detection

**1. Pattern-Based Detection**
```bash
# Find repeated error handling
find_repeated_patterns() {
  pattern="$1"
  description="$2"

  echo "\n## $description" >> reports/code-review/dry-violations.md
  grep -rn "$pattern" backend/api/src/main/python/openapi_server/impl --include="*.py" -B 2 -A 5 | \
    grep -v "^--$" | head -50 >> reports/code-review/dry-violations.md
}

# Common DRY violations
find_repeated_patterns "try:.*except.*ClientError" "Repeated DynamoDB Error Handling"
find_repeated_patterns "table()\.put_item" "Repeated DynamoDB Put Operations"
find_repeated_patterns "JWT.*encode\|jwt\.encode" "Repeated JWT Token Generation"
```

**2. Refactoring Suggestions**
```python
# Generate automated refactoring suggestions
def suggest_refactoring(duplicates: List[Dict]) -> List[Dict]:
    """Generate refactoring suggestions for duplicates"""
    suggestions = []

    for dup in duplicates:
        if dup['similarity'] >= 0.95:
            suggestions.append({
                'type': 'extract_function',
                'files': [dup['function1']['file'], dup['function2']['file']],
                'suggestion': f"Extract common logic to shared utility function",
                'estimated_loc_saved': estimate_saved_lines(dup)
            })

    return suggestions
```

---

## Phase 4: Report Generation

### Markdown Report Structure

**Best Practice Template:**
```markdown
# Comprehensive Code Review Report
**Generated**: 2025-10-10 | **Reviewer**: OpenAI GPT-4 + Claude Code

## Executive Summary
- **Total Files Analyzed**: 127
- **Lines of Code**: 15,234
- **Critical Issues**: 0
- **High Priority Issues**: 3
- **Code Duplication**: 8.2% (target: <15%)
- **Overall Grade**: B+

## Key Findings

### Security
- ✅ No hardcoded secrets found
- ✅ No SQL injection patterns
- ✅ Proper authentication on all endpoints
- ⚠️ 2 CORS configuration improvements needed

### Code Quality
- ✅ Good separation of concerns (impl/ vs controllers/)
- ✅ Consistent error handling patterns
- ⚠️ Some DRY violations in DynamoDB operations (3 locations)
- ⚠️ Missing type hints in 15% of functions

### Architecture
- ✅ Strong adherence to SOLID principles
- ✅ Clear dependency management
- ⚠️ Potential circular dependency between animals.py and handlers.py

## Detailed Findings by Module

[Per-module analysis...]

## Action Items
1. [CRITICAL] None identified
2. [HIGH] Refactor DynamoDB operations to utility function (DRY violation)
3. [HIGH] Add type hints to impl/chatgpt_integration.py
4. [MEDIUM] Review circular dependency in animals.py <-> handlers.py

## Code Duplication Matrix
[Similarity matrix with refactoring suggestions...]

## Metrics
[Detailed metrics and trends...]
```

### Teams Card Generation

**Key Sections for Teams Report:**
```json
{
  "summary_facts": [
    {"title": "Files Analyzed", "value": "127"},
    {"title": "Critical Issues", "value": "0 ✅"},
    {"title": "Code Quality", "value": "B+"},
    {"title": "Duplication", "value": "8.2%"}
  ],
  "top_issues": [
    "Refactor DynamoDB operations (3 locations)",
    "Add type hints to chatgpt_integration.py",
    "Review circular dependency"
  ],
  "strengths": [
    "Strong SOLID principles",
    "No security vulnerabilities",
    "Good test coverage"
  ]
}
```

---

## Troubleshooting

### OpenAI API Issues

**Problem**: `AuthenticationError: Incorrect API key`
```bash
# Solution: Verify API key format
echo $OPENAI_API_KEY | cut -c1-7  # Should be "sk-proj"

# Re-export with correct key
export OPENAI_API_KEY="sk-proj-..."
```

**Problem**: `RateLimitError: Rate limit exceeded`
```bash
# Solution: Add delays between requests
# Edit script to include:
time.sleep(1)  # 1 second between requests

# Or reduce parallelism:
xargs -P 1  # Sequential processing
```

**Problem**: Token limit exceeded
```bash
# Solution: Split large files
# Files over 500 lines should be chunked
find backend -name "*.py" -exec wc -l {} + | awk '$1 > 500 {print $2}'
```

### Report Generation Issues

**Problem**: JSON files not found
```bash
# Solution: Verify all analyses completed
ls -la reports/code-review/*.json

# Re-run missing analyses
for file in $(cat reports/code-review/backend-files.txt); do
  if [ ! -f "reports/code-review/$(basename $file).json" ]; then
    echo "Missing: $file"
  fi
done
```

**Problem**: Teams webhook returns 400
```bash
# Solution: Validate JSON payload
cat reports/code-review/teams-report.json | jq '.'

# Common issues:
# - Invalid adaptive card schema
# - Missing required fields
# - Malformed JSON
```

### Performance Issues

**Problem**: Analysis takes too long
```bash
# Solution: Prioritize critical files
# Only analyze impl/ and src/pages/ initially
python scripts/openai_code_review.py --file "backend/api/src/main/python/openapi_server/impl/*.py"

# Skip generated code entirely
find backend -name "*.py" | grep -v "controllers\|models\|test" > priority-files.txt
```

**Problem**: High OpenAI API costs
```bash
# Solution: Use cheaper models for initial pass
# In script, use gpt-3.5-turbo for structure
# Reserve gpt-4 for security/complex analysis

# Cost comparison:
# gpt-4: $0.03/1K input tokens
# gpt-3.5-turbo: $0.0015/1K tokens (20x cheaper)
```

---

## Best Practices

### 1. Incremental Review
- Start with Phase 1 (Discovery) to understand scope
- Run Phase 2 on critical modules first
- Expand to full codebase only if needed

### 2. Version Control Integration
```bash
# Tag before review
git tag -a code-review-2025-10-10 -m "Pre-review snapshot"

# Track improvements
git checkout -b code-review-improvements
# Make fixes...
git commit -m "fix: Refactor DynamoDB operations per code review"
```

### 3. Continuous Monitoring
```bash
# Run lightweight checks in CI/CD
# .github/workflows/code-quality.yml
- name: Security Scan
  run: |
    grep -r "password\s*=" backend || exit 0
    test $? -eq 1  # Fail if secrets found
```

### 4. Team Collaboration
- Share comprehensive report in Teams
- Create Jira tickets for HIGH issues
- Schedule follow-up review after fixes

---

## Cost Optimization

### OpenAI API Usage
```python
# Estimated costs for typical CMZ codebase review:
ESTIMATES = {
    'phase_1_discovery': 0,           # Native tools only
    'phase_2_module_analysis': 15.00, # ~50 files × $0.30/file
    'phase_3_duplication': 8.00,      # Embeddings API
    'phase_4_reporting': 0,           # Local processing
}

# Total: ~$23 per full review
# Run monthly for production codebases
# Run quarterly for stable projects
```

### Selective Analysis Strategy
```bash
# High-value targets (analyze first):
# 1. Business logic (impl/)
# 2. Authentication/security code
# 3. API endpoints with sensitive data
# 4. Recently modified files (git diff)

# Skip (unless specific need):
# - Generated code (controllers/, models/)
# - Test files (covered by test runners)
# - Documentation
# - Configuration files
```

---

## Success Metrics

Track these KPIs across reviews:
- **Critical Issues**: Target 0
- **Code Duplication**: Target <15%
- **Test Coverage**: Target >80%
- **Security Vulnerabilities**: Target 0
- **SOLID Violations**: Decreasing trend
- **Code Quality Grade**: B+ or higher

---

## Integration with CI/CD

### Pre-Commit Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Run security scan before commit
grep -r "password\s*=\s*['\"]" $(git diff --name-only --staged) && exit 1
```

### GitHub Actions
```yaml
# .github/workflows/code-review.yml
name: Monthly Code Review
on:
  schedule:
    - cron: '0 0 1 * *'  # 1st of month
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Phase 1
        run: ./scripts/run_code_review.sh --phase 1
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: code-review
          path: reports/code-review/
```

---

## References

- OpenAI API Documentation: https://platform.openai.com/docs
- Python AST Module: https://docs.python.org/3/library/ast.html
- PEP 8 Style Guide: https://pep8.org
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID
- Microsoft Teams Adaptive Cards: https://adaptivecards.io/
