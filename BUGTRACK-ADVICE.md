# BUGTRACK-ADVICE.md - Bug Tracking System Implementation Guide

## Overview

The bug tracking system provides systematic bug management with duplicate detection, bidirectional references, and Jira integration. All operations use sequential reasoning for safety and accuracy.

## Core Components

### 1. Bug Registry Location
**File**: `.claude/bugtrack.md`
**Purpose**: Central registry of all bugs with full details and status tracking

**Structure**:
```
.claude/
├── bugtrack.md          # Bug registry (main database)
└── commands/
    └── bugtrack.md      # Command definition
```

### 2. Command Architecture

**Primary Commands**:
- `/bugtrack add` - Single bug with reasoning
- `/bugtrack add-batch` - Multiple bugs from train-of-thought
- `/bugtrack list` - View bugs by status
- `/bugtrack create-jira` - Create Jira ticket(s)
- `/bugtrack resolve` - Mark bug as resolved
- `/bugtrack duplicate` - Mark as duplicate

**Shortcuts**:
- `/bt` - Short form for all commands

## Implementation Patterns

### Pattern 1: Adding Single Bug with Sequential Reasoning

```yaml
workflow:
  step_1: "Invoke mcp__sequential-thinking__sequentialthinking"
  step_2: "Parse bug description into structured format"
  step_3: "Compare against existing bugs for duplicates"
  step_4: "Assign severity and component"
  step_5: "Generate clear reproduction steps"
  step_6: "Update bug registry with new bug"

sequential_thoughts:
  thought_1: "Identify core symptom: What observable behavior is wrong?"
  thought_2: "Determine affected component: Backend API, Frontend UI, Database, etc."
  thought_3: "Extract steps to reproduce from description"
  thought_4: "Load existing bugs and compare for duplicates"
  thought_5: "Calculate similarity scores (symptoms, component, files)"
  thought_6: "Generate bug entry with proper format and references"
```

### Pattern 2: Batch Processing with Duplicate Detection

```yaml
workflow:
  step_1: "Parse train-of-thought input into distinct bugs"
  step_2: "For each bug, extract structured information"
  step_3: "Cross-compare new bugs with each other"
  step_4: "Compare all against existing registry"
  step_5: "Establish duplicate relationships"
  step_6: "Update bidirectional references"
  step_7: "Append all bugs to registry"

duplicate_detection:
  similarity_threshold: 0.70  # 70% similarity = potential duplicate

  factors:
    symptom_match: 0.40      # 40% weight - error messages, behavior
    component_match: 0.30    # 30% weight - affected system area
    file_overlap: 0.30       # 30% weight - related files

  bidirectional_rules:
    original_bug: "Potential Duplicates: 5, 7"
    duplicate_bug: "May Duplicate: 3"
```

### Pattern 3: Jira Integration

```yaml
workflow:
  step_1: "Load untracked bugs from registry"
  step_2: "Filter out bugs marked 'May Duplicate'"
  step_3: "For each bug, format Jira ticket"
  step_4: "Invoke mcp__jira-mcp__create-ticket"
  step_5: "Update bug registry with ticket ID"
  step_6: "Mark bug status as 'Tracked'"

jira_format:
  summary: "One-line clear description (< 80 chars)"
  description: "## Symptoms\n- List\n\n## Steps to Reproduce\n1. Step\n\n## Expected\nWhat should happen\n\n## Actual\nWhat happens"
  issue_type: "Bug"
  story_points: "1-5 based on severity"
  acceptance_criteria: "- Checklist of fix validation steps"
```

## Bug Registry Format

### Standard Bug Entry

```markdown
## Bug #<ID>: [<Status>] <Brief Description>
**Severity**: Critical | High | Medium | Low
**Component**: Backend Auth | Backend API | Frontend UI | Database | API Contract
**Status**: Untracked | Tracked (PR003946-XXX) | Resolved
**Reported**: YYYY-MM-DD
**Jira Ticket**: PR003946-XXX (if tracked)
**Potential Duplicates**: X, Y (if original bug with duplicates)
**May Duplicate**: X (if potential duplicate of another bug)

**Symptoms**:
- Observable error messages or incorrect behavior
- User-facing impact

**Steps to Reproduce**:
1. Concrete step one
2. Concrete step two
3. Expected vs actual observation

**Expected Behavior**:
What should happen in correct implementation

**Actual Behavior**:
What currently happens (incorrect)

**Root Cause** (if known):
Technical explanation of underlying issue

**Related Files**:
- path/to/file.py:123
- path/to/component.tsx:45

**Notes**:
- Additional context
- Workarounds
- Related bugs

---
```

## Severity Classification

### Critical
- System unavailable or data loss
- Security vulnerabilities
- Complete feature failure affecting all users

**Examples**:
- Authentication completely broken
- Database corruption
- Exposed credentials

### High
- Major feature broken for most users
- Significant functionality loss
- Workaround exists but difficult

**Examples**:
- Save operations not persisting
- Required fields not validated
- CORS blocking main workflows

### Medium
- Feature partially broken
- Affects some users or workflows
- Reasonable workaround available

**Examples**:
- UI elements not responding
- Incorrect default values
- Minor data inconsistencies

### Low
- Cosmetic issues
- Edge case bugs
- Enhancement requests

**Examples**:
- Typos or formatting issues
- Unnecessary UI elements
- Minor UX improvements

## Duplicate Detection Algorithm

### Step-by-Step Process

1. **Extract Key Features**:
```yaml
bug_signature:
  symptoms: ["error message", "behavior pattern"]
  component: "Backend API"
  files: ["path/to/file.py", "path/to/other.tsx"]
  error_codes: ["401", "CORS"]
```

2. **Calculate Similarity**:
```python
def calculate_similarity(bug_a, bug_b):
    # Symptom similarity (keyword overlap)
    symptom_score = len(set(bug_a.symptoms) & set(bug_b.symptoms)) / max(len(bug_a.symptoms), len(bug_b.symptoms))

    # Component exact match
    component_score = 1.0 if bug_a.component == bug_b.component else 0.0

    # File overlap
    file_score = len(set(bug_a.files) & set(bug_b.files)) / max(len(bug_a.files), len(bug_b.files))

    # Weighted average
    return (symptom_score * 0.4) + (component_score * 0.3) + (file_score * 0.3)

# If score >= 0.70: Potential duplicate
```

3. **Establish References**:
```yaml
if similarity_score >= 0.70:
  original_bug: "Add to 'Potential Duplicates' list"
  duplicate_bug: "Set 'May Duplicate' to original bug ID"
```

### Duplicate Resolution Workflow

```yaml
when_creating_jira_tickets:
  step_1: "Identify all bugs marked 'May Duplicate'"
  step_2: "Skip duplicate bugs (don't create tickets)"
  step_3: "Create ticket only for original bug"
  step_4: "Add comment to original ticket listing potential duplicates"

when_resolving_duplicates:
  step_1: "Review duplicate bugs manually"
  step_2: "If confirmed duplicate, update status to 'Duplicate of #X'"
  step_3: "If not duplicate, remove 'May Duplicate' field"
  step_4: "Update original bug's 'Potential Duplicates' list"
```

## Integration Patterns

### With /comprehensive-validation

```bash
# Run comprehensive validation
/comprehensive-validation

# After validation completes, capture all issues
/bugtrack add-batch

# Provide train-of-thought summary of issues found
# Agent will parse and create bug entries
```

### With /review-mr

```bash
# Review merge request
/review-mr 123

# Capture review findings as bugs
/bugtrack add-batch

# Convert critical issues to Jira tickets
/bugtrack create-jira-all
```

### With /nextfive

```bash
# Implement bug fixes
/nextfive

# Mark bugs as resolved after fixes merge
/bugtrack resolve 1
/bugtrack resolve 5
/bugtrack resolve 7
```

## Error Handling

### Duplicate Chain Resolution

**Problem**: Bug A duplicates B, but B duplicates C
```yaml
detection:
  bug_a: "May Duplicate: 2"
  bug_b: "May Duplicate: 3"
  bug_c: "Original"

resolution:
  step_1: "Use sequential reasoning to analyze chain"
  step_2: "Identify earliest bug (C) as original"
  step_3: "Update both A and B to reference C"
  step_4: "Update C's 'Potential Duplicates' to include A and B"
```

### Jira Creation Failure

**Problem**: Jira API fails during ticket creation
```yaml
handling:
  step_1: "Log error in bug registry"
  step_2: "Keep bug status as 'Untracked'"
  step_3: "Add note: 'Jira creation failed: <error>'"
  step_4: "Allow retry without creating duplicate bug entry"
```

### Missing Required Fields

**Problem**: Bug description lacks reproduction steps
```yaml
handling:
  step_1: "Use sequential reasoning to infer steps from symptoms"
  step_2: "Generate best-effort reproduction steps"
  step_3: "Mark bug with 'Needs Validation' tag"
  step_4: "Add note: 'Reproduction steps inferred - verify'"
```

## Best Practices

### 1. Clear Bug Descriptions

**Good**:
```
Symptoms: Login POST returns 401 with valid credentials
Steps: 1. Start backend, 2. Attempt login with test@cmz.org/testpass123
Expected: 200 OK with JWT token
Actual: 401 Unauthorized
```

**Bad**:
```
Login doesn't work
```

### 2. Component Classification

**Components**:
- **Backend Auth**: Authentication, authorization, JWT
- **Backend API**: Endpoint logic, data validation
- **Frontend UI**: React components, user interface
- **Database**: DynamoDB, data persistence
- **API Contract**: OpenAPI spec, request/response formats
- **Infrastructure**: CORS, deployment, environment config

### 3. Severity Assignment

**Critical**: Data loss, security, complete system failure
**High**: Major feature broken, blocks workflows
**Medium**: Partial feature failure, workaround available
**Low**: Cosmetic, edge cases, enhancements

### 4. Bidirectional Reference Integrity

**Always maintain both sides**:
```markdown
## Bug #3: Original Bug
**Potential Duplicates**: 5, 7

## Bug #5: Potential Duplicate
**May Duplicate**: 3

## Bug #7: Potential Duplicate
**May Duplicate**: 3
```

## Troubleshooting

### Issue: Duplicate Not Detected

**Symptoms**: Similar bugs not marked as duplicates

**Solution**:
1. Review similarity scoring algorithm
2. Check if symptoms use different terminology
3. Manually mark with `/bugtrack duplicate <id> <original-id>`

### Issue: Jira Ticket Creation Fails

**Symptoms**: `mcp__jira-mcp__create-ticket` returns error

**Solution**:
1. Verify Jira credentials in environment
2. Check ticket format (summary < 255 chars)
3. Verify project permissions
4. Review error message in bug registry

### Issue: Bug Registry Corrupted

**Symptoms**: Parse errors when reading `.claude/bugtrack.md`

**Solution**:
1. Validate markdown format
2. Check for missing required fields
3. Verify bug ID sequence
4. Restore from git history if needed

## Testing Strategy

### Unit Testing Duplicate Detection

```yaml
test_cases:
  case_1:
    bug_a: "CORS error on port 3002"
    bug_b: "CORS blocking port 3002 requests"
    expected: similarity > 0.70 (duplicate)

  case_2:
    bug_a: "Animal config not saving"
    bug_b: "Family dialog validation missing"
    expected: similarity < 0.70 (not duplicate)
```

### Integration Testing Jira Creation

```yaml
test_workflow:
  step_1: "Add test bug with /bugtrack add"
  step_2: "Create Jira ticket with /bugtrack create-jira <id>"
  step_3: "Verify ticket created in Jira UI"
  step_4: "Verify bug status updated to 'Tracked'"
  step_5: "Verify Jira ticket ID in bug registry"
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load bug registry only when needed
2. **Caching**: Cache parsed bugs during multi-bug operations
3. **Batch Operations**: Process multiple bugs in single sequential reasoning session
4. **Index Building**: Maintain symptom keyword index for faster duplicate detection

### Resource Usage

```yaml
typical_operations:
  add_single_bug: "~2000 tokens"
  add_batch_5_bugs: "~8000 tokens"
  create_jira_single: "~1500 tokens"
  create_jira_all_10_bugs: "~12000 tokens"
```

## Success Metrics

### Quality Indicators

✅ **Bug Clarity**: >95% of bugs have clear reproduction steps
✅ **Duplicate Detection**: >90% accuracy in identifying duplicates
✅ **Jira Integration**: >98% success rate for ticket creation
✅ **Bidirectional Integrity**: 100% consistency in duplicate references
✅ **Status Tracking**: 100% accuracy in tracked vs untracked

### Process Metrics

- **Time to Track**: < 2 minutes per bug
- **Duplicate Detection**: < 5 minutes for batch of 10 bugs
- **Jira Creation**: < 1 minute per ticket
- **Bug Resolution**: < 30 seconds to mark resolved

## Future Enhancements

### Planned Features

1. **Auto-linking**: Automatically link bugs to related code changes
2. **Trend Analysis**: Identify bug patterns by component/timeframe
3. **Priority Scoring**: ML-based priority assignment
4. **Resolution Tracking**: Link bugs to merge requests
5. **Notification System**: Alert on new bugs, Jira updates

---

**Version**: 1.0.0
**Last Updated**: 2025-10-12
**Author**: KC Stegbauer
**Related Commands**: /comprehensive-validation, /review-mr, /nextfive
