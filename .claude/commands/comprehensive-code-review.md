# Comprehensive Code Review

**Purpose**: Multi-phase systematic code review for style, security, logical correctness, DRY/SOLID principles, and code duplication detection using hybrid approach with OpenAI integration

**Usage**: `/comprehensive-code-review [--focus area] [--module path]`

## Context
This command orchestrates a complete codebase review that's too large for single-pass analysis. It combines native tool analysis, MCP Sequential reasoning, and OpenAI API evaluation to provide comprehensive insights into code quality, security, and architectural patterns.

## Hybrid Analysis Approach (Option C)

### Component Integration
```yaml
Native Tools (Structure):
  - Glob: File discovery and categorization
  - Grep: Pattern detection and security scanning
  - Read: Code analysis and context gathering

MCP Sequential (Reasoning):
  - Complex architectural decisions
  - SOLID principle evaluation
  - Multi-file dependency analysis
  - Cross-cutting concern identification

OpenAI API (Deep Analysis):
  - Style consistency validation
  - Security vulnerability detection
  - Code duplication with embeddings
  - Refactoring recommendations
```

## Phase 1: Discovery & Architecture Mapping

### Step 1: Generate Codebase Structure
```bash
# Create comprehensive file inventory
echo "=== CMZ Chatbots Codebase Structure ===" > reports/code-review/structure.md

# Backend structure
echo "\n## Backend API Structure" >> reports/code-review/structure.md
find backend/api/src/main/python -name "*.py" | grep -v __pycache__ | sort >> reports/code-review/structure.md

# Frontend structure
echo "\n## Frontend Structure" >> reports/code-review/structure.md
find frontend/src -name "*.tsx" -o -name "*.ts" | sort >> reports/code-review/structure.md

# Infrastructure
echo "\n## Infrastructure Files" >> reports/code-review/structure.md
ls -1 Makefile Dockerfile docker-compose.yml 2>/dev/null >> reports/code-review/structure.md
```

### Step 2: Calculate Code Metrics
```bash
# Lines of code by category
echo "=== Code Metrics ===" > reports/code-review/metrics.md

# Backend implementation (non-generated)
echo "\n## Backend Implementation Code" >> reports/code-review/metrics.md
find backend/api/src/main/python/openapi_server/impl -name "*.py" -exec wc -l {} + | tail -1 >> reports/code-review/metrics.md

# Frontend code
echo "\n## Frontend Code" >> reports/code-review/metrics.md
find frontend/src -name "*.tsx" -o -name "*.ts" | xargs wc -l | tail -1 >> reports/code-review/metrics.md

# Test code
echo "\n## Test Code" >> reports/code-review/metrics.md
find backend/api/src/main/python/tests -name "*.py" -exec wc -l {} + | tail -1 >> reports/code-review/metrics.md
find backend/api/src/main/python/tests/playwright -name "*.js" -exec wc -l {} + | tail -1 >> reports/code-review/metrics.md

# Generated code (for reference)
echo "\n## Generated Code (Reference)" >> reports/code-review/metrics.md
find backend/api/src/main/python/openapi_server/controllers -name "*.py" -exec wc -l {} + | tail -1 >> reports/code-review/metrics.md
find backend/api/src/main/python/openapi_server/models -name "*.py" -exec wc -l {} + | tail -1 >> reports/code-review/metrics.md
```

### Step 3: Identify Hot Spots
```bash
# Find largest/most complex files
echo "=== Code Hot Spots ===" > reports/code-review/hotspots.md

echo "\n## Largest Implementation Files" >> reports/code-review/hotspots.md
find backend/api/src/main/python/openapi_server/impl -name "*.py" -exec wc -l {} + | sort -rn | head -10 >> reports/code-review/hotspots.md

echo "\n## Largest Frontend Files" >> reports/code-review/hotspots.md
find frontend/src -name "*.tsx" -exec wc -l {} + | sort -rn | head -10 >> reports/code-review/hotspots.md

echo "\n## Most Complex Functions (cyclomatic complexity indicators)" >> reports/code-review/hotspots.md
# Look for functions with many branches (if/elif/else)
grep -rn "^\s*def\s" backend/api/src/main/python/openapi_server/impl --include="*.py" -A 50 | grep -c "if\|elif\|else\|try\|except" | sort -rn | head -10 >> reports/code-review/hotspots.md
```

### Step 4: Dependency Mapping
**Use Sequential MCP for dependency analysis:**
```python
# This will be analyzed using mcp__sequential-thinking
"""
Analyze import patterns across backend implementation:
1. What are the core utility dependencies?
2. Which modules have circular dependencies?
3. What external libraries are most used?
4. Are there any missing abstractions?
"""
```

## Phase 2: Module-by-Module Analysis

### Backend Implementation Deep Dive

#### Step 1: Business Logic Modules
```bash
# Priority modules for review
MODULES=(
  "backend/api/src/main/python/openapi_server/impl/animals.py"
  "backend/api/src/main/python/openapi_server/impl/family.py"
  "backend/api/src/main/python/openapi_server/impl/auth.py"
  "backend/api/src/main/python/openapi_server/impl/conversation.py"
  "backend/api/src/main/python/openapi_server/impl/chatgpt_integration.py"
)

for module in "${MODULES[@]}"; do
  echo "Analyzing: $module"

  # Extract module for OpenAI analysis
  python scripts/openai_code_review.py \
    --file "$module" \
    --focus "style,security,dry,solid" \
    --output "reports/code-review/$(basename $module).analysis.json"
done
```

#### Step 2: Utility & Infrastructure
```bash
# Review utility modules
UTIL_MODULES=(
  "backend/api/src/main/python/openapi_server/impl/utils/dynamo.py"
  "backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py"
  "backend/api/src/main/python/openapi_server/impl/handlers.py"
)

for module in "${UTIL_MODULES[@]}"; do
  python scripts/openai_code_review.py \
    --file "$module" \
    --focus "dry,solid,security" \
    --output "reports/code-review/$(basename $module).analysis.json"
done
```

### Frontend Analysis

#### Step 1: Core Pages
```bash
FRONTEND_MODULES=(
  "frontend/src/pages/Chat.tsx"
  "frontend/src/pages/Dashboard.tsx"
  "frontend/src/pages/Login.tsx"
  "frontend/src/config/api.ts"
)

for module in "${FRONTEND_MODULES[@]}"; do
  python scripts/openai_code_review.py \
    --file "$module" \
    --focus "style,security,dry,react-best-practices" \
    --output "reports/code-review/$(basename $module).analysis.json"
done
```

## Phase 3: Cross-Cutting Analysis

### Security Scan
```bash
echo "=== Security Analysis ===" > reports/code-review/security.md

# SQL injection patterns (should find none - using DynamoDB)
echo "\n## SQL Injection Risk" >> reports/code-review/security.md
grep -rn "execute.*%\|format.*sql\|f\".*SELECT" backend/api/src/main/python/openapi_server/impl --include="*.py" >> reports/code-review/security.md || echo "✅ No SQL injection patterns found" >> reports/code-review/security.md

# Secrets in code
echo "\n## Hardcoded Secrets" >> reports/code-review/security.md
grep -rn "password\s*=\s*['\"].*['\"]|api_key\s*=\s*['\"].*['\"]|secret\s*=\s*['\"].*['\"]" backend frontend --include="*.py" --include="*.ts" --include="*.tsx" >> reports/code-review/security.md || echo "✅ No hardcoded secrets found" >> reports/code-review/security.md

# Authentication checks
echo "\n## Authentication Validation" >> reports/code-review/security.md
grep -rn "X-User-Id\|auth.*required\|@require_auth" backend/api/src/main/python/openapi_server --include="*.py" >> reports/code-review/security.md

# CORS configuration review
echo "\n## CORS Configuration" >> reports/code-review/security.md
grep -rn "CORS\|Access-Control" backend/api --include="*.py" >> reports/code-review/security.md

# XSS prevention in frontend
echo "\n## XSS Prevention (React)" >> reports/code-review/security.md
grep -rn "dangerouslySetInnerHTML\|innerHTML" frontend/src --include="*.tsx" --include="*.ts" >> reports/code-review/security.md || echo "✅ No dangerous HTML injection found" >> reports/code-review/security.md
```

### Code Duplication Detection

**Use OpenAI Embeddings API for similarity detection:**
```python
# scripts/detect_code_duplication.py
"""
Generate embeddings for each function/class
Compare similarity scores
Identify refactoring candidates
"""
```

```bash
# Run duplication detection
python scripts/detect_code_duplication.py \
  --threshold 0.85 \
  --paths "backend/api/src/main/python/openapi_server/impl" \
  --output "reports/code-review/duplication.json"
```

### SOLID Principle Evaluation

**Use Sequential MCP for each principle:**

```yaml
Single Responsibility:
  question: "Does each module/class have exactly one reason to change?"
  analyze: impl/*.py files

Open/Closed:
  question: "Can we extend behavior without modifying existing code?"
  analyze: Base classes and extension patterns

Liskov Substitution:
  question: "Are derived classes substitutable for base classes?"
  analyze: Inheritance hierarchies

Interface Segregation:
  question: "Are interfaces focused and minimal?"
  analyze: Abstract base classes and protocols

Dependency Inversion:
  question: "Do high-level modules depend on abstractions?"
  analyze: Import statements and coupling
```

### DRY Violations
```bash
echo "=== DRY Violations ===" > reports/code-review/dry-violations.md

# Find repeated code patterns
echo "\n## Repeated Error Handling Patterns" >> reports/code-review/dry-violations.md
grep -rn "try:.*except.*ClientError" backend/api/src/main/python/openapi_server/impl --include="*.py" -B 2 -A 5 >> reports/code-review/dry-violations.md

echo "\n## Repeated DynamoDB Operations" >> reports/code-review/dry-violations.md
grep -rn "table()\.put_item\|table()\.get_item\|table()\.query" backend/api/src/main/python/openapi_server/impl --include="*.py" >> reports/code-review/dry-violations.md

echo "\n## Repeated API Endpoint Patterns" >> reports/code-review/dry-violations.md
grep -rn "fetch.*localhost:8080\|API_BASE_URL" frontend/src --include="*.tsx" --include="*.ts" >> reports/code-review/dry-violations.md
```

## Phase 4: OpenAI Analysis Scripts

### Generate OpenAI Review Script
```python
# scripts/openai_code_review.py
#!/usr/bin/env python3
"""
Comprehensive code review using OpenAI API
Analyzes code for style, security, DRY, SOLID, and duplication
"""

import argparse
import json
import os
from pathlib import Path
from openai import OpenAI

def analyze_code(file_path: str, focus_areas: list[str]) -> dict:
    """Analyze a single code file using OpenAI API"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    with open(file_path, 'r') as f:
        code = f.read()

    focus_prompt = {
        'style': 'PEP 8 compliance, naming conventions, code organization',
        'security': 'SQL injection, XSS, secrets exposure, authentication gaps',
        'dry': 'Code duplication, repeated patterns, missing abstractions',
        'solid': 'Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion',
        'react-best-practices': 'Hooks usage, component structure, state management'
    }

    focus_text = '\n'.join([f"- {focus_prompt.get(f, f)}" for f in focus_areas])

    prompt = f"""
You are a senior software engineer reviewing code for a production system.

Analyze the following code file and provide detailed findings for:
{focus_text}

For each issue found, provide:
1. Severity (CRITICAL, HIGH, MEDIUM, LOW)
2. Line number (if applicable)
3. Description of the issue
4. Recommended fix
5. Example of corrected code (if applicable)

Code File: {file_path}

```
{code}
```

Return your analysis as a JSON object with this structure:
{{
  "file": "{file_path}",
  "language": "python" or "typescript",
  "summary": "Brief overview of code quality",
  "issues": [
    {{
      "severity": "HIGH",
      "category": "security" or "style" or "dry" or "solid",
      "line": 42,
      "description": "Hardcoded secret in code",
      "recommendation": "Use environment variables",
      "example": "api_key = os.getenv('API_KEY')"
    }}
  ],
  "strengths": ["Well-documented functions", "Good error handling"],
  "metrics": {{
    "lines_of_code": 250,
    "complexity_estimate": "medium",
    "test_coverage": "unknown"
  }}
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior code reviewer focused on production quality."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

def main():
    parser = argparse.ArgumentParser(description='OpenAI Code Review')
    parser.add_argument('--file', required=True, help='File to analyze')
    parser.add_argument('--focus', required=True, help='Comma-separated focus areas')
    parser.add_argument('--output', required=True, help='Output JSON file')

    args = parser.parse_args()
    focus_areas = args.focus.split(',')

    print(f"Analyzing {args.file} for: {', '.join(focus_areas)}")

    result = analyze_code(args.file, focus_areas)

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Analysis complete: {args.output}")

    # Print summary
    issues_by_severity = {}
    for issue in result.get('issues', []):
        severity = issue['severity']
        issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1

    print("\n📊 Issue Summary:")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = issues_by_severity.get(severity, 0)
        if count > 0:
            print(f"  {severity}: {count}")

if __name__ == '__main__':
    main()
```

### Generate Duplication Detection Script
```python
# scripts/detect_code_duplication.py
#!/usr/bin/env python3
"""
Detect code duplication using OpenAI embeddings API
Generates similarity matrix and identifies refactoring candidates
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from openai import OpenAI
import numpy as np

def extract_functions(file_path: str) -> List[Dict]:
    """Extract function definitions from Python/TypeScript files"""
    functions = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_function = None
    current_lines = []

    for i, line in enumerate(lines):
        # Python function detection
        if line.strip().startswith('def ') or line.strip().startswith('async def '):
            if current_function:
                functions.append({
                    'file': str(file_path),
                    'name': current_function,
                    'start_line': current_lines[0] if current_lines else i,
                    'end_line': i,
                    'code': ''.join(lines[current_lines[0]:i]) if current_lines else ''
                })
            current_function = line.strip().split('(')[0].replace('def ', '').replace('async def ', '')
            current_lines = [i]
        # TypeScript function detection
        elif 'function ' in line or '=>' in line:
            if current_function:
                functions.append({
                    'file': str(file_path),
                    'name': current_function,
                    'start_line': current_lines[0] if current_lines else i,
                    'end_line': i,
                    'code': ''.join(lines[current_lines[0]:i]) if current_lines else ''
                })
            current_function = line.strip().split('(')[0].split()[-1] if 'function' in line else 'arrow_func'
            current_lines = [i]
        elif current_function and line.strip():
            current_lines.append(i)

    return functions

def get_embedding(client: OpenAI, text: str) -> List[float]:
    """Get embedding vector for code text"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def calculate_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Calculate cosine similarity between embeddings"""
    a = np.array(emb1)
    b = np.array(emb2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def detect_duplicates(paths: List[str], threshold: float = 0.85) -> Dict:
    """Detect duplicate code across files"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Extract all functions
    all_functions = []
    for path in paths:
        for file_path in Path(path).rglob('*.py'):
            all_functions.extend(extract_functions(file_path))
        for file_path in Path(path).rglob('*.ts'):
            all_functions.extend(extract_functions(file_path))
        for file_path in Path(path).rglob('*.tsx'):
            all_functions.extend(extract_functions(file_path))

    print(f"Found {len(all_functions)} functions to analyze")

    # Generate embeddings
    print("Generating embeddings...")
    for func in all_functions:
        func['embedding'] = get_embedding(client, func['code'])

    # Find similar pairs
    print("Detecting duplicates...")
    duplicates = []

    for i in range(len(all_functions)):
        for j in range(i + 1, len(all_functions)):
            similarity = calculate_similarity(
                all_functions[i]['embedding'],
                all_functions[j]['embedding']
            )

            if similarity >= threshold:
                duplicates.append({
                    'function1': {
                        'file': all_functions[i]['file'],
                        'name': all_functions[i]['name'],
                        'line': all_functions[i]['start_line']
                    },
                    'function2': {
                        'file': all_functions[j]['file'],
                        'name': all_functions[j]['name'],
                        'line': all_functions[j]['start_line']
                    },
                    'similarity': round(similarity, 3)
                })

    return {
        'total_functions': len(all_functions),
        'threshold': threshold,
        'duplicates_found': len(duplicates),
        'duplicates': sorted(duplicates, key=lambda x: x['similarity'], reverse=True)
    }

def main():
    parser = argparse.ArgumentParser(description='Detect code duplication')
    parser.add_argument('--paths', required=True, help='Comma-separated paths to analyze')
    parser.add_argument('--threshold', type=float, default=0.85, help='Similarity threshold (0-1)')
    parser.add_argument('--output', required=True, help='Output JSON file')

    args = parser.parse_args()
    paths = args.paths.split(',')

    result = detect_duplicates(paths, args.threshold)

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Duplication analysis complete: {args.output}")
    print(f"📊 Found {result['duplicates_found']} duplicate pairs")

    if result['duplicates_found'] > 0:
        print("\n🔍 Top 5 duplicates:")
        for dup in result['duplicates'][:5]:
            print(f"  {dup['similarity']:.1%} similarity:")
            print(f"    {dup['function1']['file']}:{dup['function1']['line']} - {dup['function1']['name']}")
            print(f"    {dup['function2']['file']}:{dup['function2']['line']} - {dup['function2']['name']}")

if __name__ == '__main__':
    main()
```

## Phase 5: Report Generation

### Aggregate Results
```bash
# Create comprehensive report
python scripts/generate_code_review_report.py \
  --structure reports/code-review/structure.md \
  --metrics reports/code-review/metrics.md \
  --hotspots reports/code-review/hotspots.md \
  --security reports/code-review/security.md \
  --dry reports/code-review/dry-violations.md \
  --duplication reports/code-review/duplication.json \
  --analyses reports/code-review/*.analysis.json \
  --output reports/code-review/COMPREHENSIVE_REVIEW.md
```

### Generate Teams Report
```bash
python scripts/generate_code_review_teams_card.py \
  --input reports/code-review/COMPREHENSIVE_REVIEW.md \
  --output reports/code-review/teams-report.json

curl -X POST "$TEAMS_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d @reports/code-review/teams-report.json
```

## Execution Order

**Full Review (All Phases):**
```bash
# Phase 1: Discovery
./scripts/run_code_review.sh --phase 1

# Phase 2: Module Analysis (requires OPENAI_API_KEY)
./scripts/run_code_review.sh --phase 2

# Phase 3: Cross-Cutting Analysis
./scripts/run_code_review.sh --phase 3

# Phase 4: Generate Reports
./scripts/run_code_review.sh --phase 4

# All phases
./scripts/run_code_review.sh --all
```

**Targeted Review:**
```bash
# Single module
/comprehensive-code-review --module backend/api/src/main/python/openapi_server/impl/animals.py --focus security,dry

# Single area
/comprehensive-code-review --focus security

# Frontend only
/comprehensive-code-review --module frontend/src --focus style,react-best-practices
```

## Output Structure

```
reports/code-review/
├── structure.md                  # Codebase structure
├── metrics.md                    # LOC and complexity metrics
├── hotspots.md                   # Largest/most complex files
├── security.md                   # Security scan results
├── dry-violations.md             # DRY principle violations
├── duplication.json              # Code similarity analysis
├── animals.py.analysis.json      # Per-module OpenAI analysis
├── family.py.analysis.json
├── ...
├── COMPREHENSIVE_REVIEW.md       # Aggregated findings
└── teams-report.json             # Teams webhook payload
```

## Success Criteria

- ✅ All implementation modules analyzed by OpenAI
- ✅ Security scan shows no CRITICAL issues
- ✅ Code duplication below 15% threshold
- ✅ SOLID principles evaluated with recommendations
- ✅ DRY violations identified with refactoring suggestions
- ✅ Comprehensive report generated with actionable items
- ✅ Teams notification sent with executive summary

## Integration Points

- **Sequential MCP**: Complex reasoning for SOLID/architecture evaluation
- **OpenAI API**: Deep code analysis and duplication detection
- **Native Tools**: Structure discovery, pattern detection, metrics
- **Teams Webhook**: Notification and reporting
- **Git**: Track review results and improvement PRs

## Quality Gates

- No CRITICAL security issues allowed
- HIGH issues must have mitigation plan
- Duplication above 85% similarity requires refactoring
- SOLID violations in core modules must be addressed
- All findings documented with file:line references

## References

- `COMPREHENSIVE-CODE-REVIEW-ADVICE.md` - Implementation guidance and troubleshooting
- OpenAI API documentation for embeddings and chat completions
- PEP 8 style guide for Python
- React best practices and TypeScript guidelines
- OWASP security standards
