# /bugtrack - Systematic Bug Tracking with Jira Integration

**Purpose**: Manage bugs systematically with duplicate detection, bidirectional references, and Jira ticket creation.

**Usage**:
```bash
/bugtrack add "<bug description>"           # Add single bug with reasoning
/bugtrack add-batch                          # Add multiple bugs from train-of-thought
/bugtrack list [--status untracked|tracked|resolved]  # List bugs
/bugtrack create-jira <bug-id>              # Create Jira ticket for specific bug
/bugtrack create-jira-all                   # Create Jira tickets for all untracked bugs
/bugtrack resolve <bug-id>                  # Mark bug as resolved
/bugtrack duplicate <bug-id> <duplicate-of> # Mark bug as duplicate
```

## Core Workflow

### Phase 1: Bug Analysis (Sequential MCP)
Use sequential thinking to:
1. Parse train-of-thought input into distinct bugs
2. Extract key information: symptoms, steps to reproduce, expected vs actual behavior
3. Identify potential duplicates by comparing symptoms and root causes
4. Generate clear, testable bug descriptions
5. Assign severity and priority

### Phase 2: Duplicate Detection
1. Compare new bug against existing bugs in `.claude/bugtrack.md`
2. Use similarity scoring for:
   - Symptom overlap (error messages, UI behavior)
   - Affected components (file paths, functions)
   - Root cause patterns
3. Establish bidirectional references:
   - Original bug: "Potential Duplicates: 5, 7"
   - Duplicate bug: "May duplicate: 3"

### Phase 3: Bug Registry Update
1. Append new bugs to `.claude/bugtrack.md`
2. Update duplicate references bidirectionally
3. Maintain bug metadata: ID, status, severity, Jira ticket link

### Phase 4: Jira Integration
1. Convert bug to Jira ticket format:
   - Summary: Clear one-line description
   - Description: Full details with reproduction steps
   - Issue Type: Bug
   - Priority: Based on severity
2. Use Jira MCP to create ticket
3. Update bug registry with Jira ticket ID
4. Mark bug status as "tracked"

## Sequential Reasoning Pattern

For each operation, use mcp__sequential-thinking__sequentialthinking with these phases:

**Bug Analysis Phase**:
```yaml
thought_1: "Parse input to identify distinct bug instances"
thought_2: "Extract symptoms, reproduction steps, expected behavior"
thought_3: "Identify affected components and error messages"
thought_4: "Compare against existing bugs for duplicates"
thought_5: "Generate clear bug description and classification"
```

**Duplicate Detection Phase**:
```yaml
thought_1: "Load existing bugs from .claude/bugtrack.md"
thought_2: "Calculate similarity scores for symptoms"
thought_3: "Calculate similarity scores for affected components"
thought_4: "Identify potential duplicates (score > 70%)"
thought_5: "Establish bidirectional references"
```

**Jira Creation Phase**:
```yaml
thought_1: "Verify bug is untracked and not a duplicate"
thought_2: "Format bug for Jira (summary, description, priority)"
thought_3: "Create Jira ticket using mcp__jira-mcp__create-ticket"
thought_4: "Update bug registry with Jira ticket ID"
thought_5: "Mark bug status as tracked"
```

## Bug Registry Format (.claude/bugtrack.md)

```markdown
# CMZ Chatbots Bug Registry

## Bug #1: [Status] Brief Description
**Severity**: Critical | High | Medium | Low
**Component**: Backend Auth | Frontend UI | API Contract | Database
**Status**: Untracked | Tracked (PR003946-XXX) | Resolved
**Reported**: YYYY-MM-DD
**Jira Ticket**: PR003946-XXX (if tracked)
**Potential Duplicates**: 5, 7 (if original)
**May Duplicate**: 3 (if potential duplicate)

**Symptoms**:
- Observed error messages or incorrect behavior

**Steps to Reproduce**:
1. Step one
2. Step two

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Root Cause** (if known):
Technical explanation

**Related Files**:
- path/to/file.py:123
- path/to/other.tsx:45

---
```

## Examples

### Example 1: Add Single Bug
```bash
/bugtrack add "Login fails with CORS error when frontend runs on port 3002"
```

**Sequential Reasoning Output**:
1. Parse: Single bug identified - CORS configuration issue
2. Extract: Error "ERR_FAILED", affected file `__main__.py`, login flow
3. Compare: No similar CORS bugs in registry
4. Classification: High severity, Backend Auth component
5. Generate: Clear bug description with reproduction steps

**Bug Registry Update**:
```markdown
## Bug #12: [Untracked] CORS Error Blocks Login on Port 3002
**Severity**: High
**Component**: Backend Auth
**Status**: Untracked
**Reported**: 2025-10-12

**Symptoms**:
- Login POST request fails with CORS error
- Console shows "Access to fetch at 'http://localhost:8080/auth' has been blocked"

**Steps to Reproduce**:
1. Start frontend on port 3002
2. Attempt login with valid credentials
3. Observe CORS error in browser console

**Expected Behavior**:
Login should succeed regardless of frontend port

**Actual Behavior**:
CORS policy rejects request, login fails

**Root Cause**:
`__main__.py` CORS configuration only allows ports 3000, 3001

**Related Files**:
- backend/api/src/main/python/openapi_server/__main__.py:14-21
```

### Example 2: Batch Add with Duplicate Detection
```bash
/bugtrack add-batch
```

**User provides train-of-thought**:
```
Issues observed during testing:
1. Animal config save doesn't persist systemPrompt changes
2. DynamoDB returns old systemPrompt value after PATCH
3. SystemPrompt field shows previous value after save
4. Family dialog doesn't validate required fields
5. Animal configuration persistence failing for systemPrompt
```

**Sequential Reasoning**:
- Bugs 1, 2, 3, 5 are all the same issue (systemPrompt persistence)
- Bug 4 is distinct (family validation)
- Original: Bug 1
- Duplicates: Bugs 2, 3, 5

**Bug Registry Update**:
```markdown
## Bug #13: [Untracked] Animal Config systemPrompt Not Persisting
**Severity**: High
**Component**: Backend API
**Status**: Untracked
**Reported**: 2025-10-12
**Potential Duplicates**: (references to bugs 2, 3, 5 if they're added)

**Symptoms**:
- PATCH /animal_config succeeds (200) but changes don't persist
- GET /animal_config returns old systemPrompt value
- Frontend shows previous value after save

**Steps to Reproduce**:
1. Edit animal systemPrompt in UI
2. Save changes
3. Refresh or re-fetch animal config
4. Observe old value still present

## Bug #14: [Untracked] Family Dialog Lacks Required Field Validation
**Severity**: Medium
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
```

### Example 3: Create Jira Tickets
```bash
/bugtrack create-jira-all
```

**Sequential Reasoning**:
1. Load all untracked bugs from registry
2. Filter out duplicates (don't create tickets for "May Duplicate" bugs)
3. For each bug, create Jira ticket with proper formatting
4. Update registry with Jira ticket IDs
5. Mark bugs as tracked

**Jira Ticket Creation** (using mcp__jira-mcp__create-ticket):
```json
{
  "summary": "Animal Config systemPrompt Not Persisting to DynamoDB",
  "description": "## Symptoms\n- PATCH /animal_config succeeds but changes don't persist...",
  "issue_type": "Bug",
  "story_points": 3,
  "acceptance_criteria": "- systemPrompt changes persist after PATCH\n- GET returns updated value\n- Frontend displays saved changes"
}
```

## Duplicate Detection Algorithm

### Similarity Scoring
```python
def calculate_similarity(bug_new, bug_existing):
    # Symptom similarity (40% weight)
    symptom_score = compare_symptoms(bug_new.symptoms, bug_existing.symptoms)

    # Component similarity (30% weight)
    component_score = 1.0 if bug_new.component == bug_existing.component else 0.0

    # File overlap (30% weight)
    file_score = calculate_file_overlap(bug_new.files, bug_existing.files)

    return (symptom_score * 0.4) + (component_score * 0.3) + (file_score * 0.3)

# Threshold for duplicate: 0.70 (70% similarity)
```

### Bidirectional Reference Rules
1. **Original Bug** (first occurrence):
   - Add "Potential Duplicates: X, Y, Z" field
   - List all bugs that may be duplicates

2. **Duplicate Bug** (later occurrence):
   - Add "May Duplicate: X" field (reference to original)
   - Do NOT add "Potential Duplicates" field
   - Include note: "Review against Bug X before creating Jira ticket"

3. **When Creating Jira Tickets**:
   - Skip bugs marked "May Duplicate"
   - Create ticket only for original bug
   - Link duplicate bugs to original Jira ticket

## Integration with Existing Commands

### With /comprehensive-validation
After validation runs, use `/bugtrack add-batch` to process all discovered issues.

### With /review-mr
Use `/bugtrack add-batch` to capture issues from code review comments.

### With /nextfive
When implementing fixes, use `/bugtrack resolve <bug-id>` to mark bugs as fixed.

## Safety Features

1. **Sequential Reasoning Required**: All operations must use sequential-thinking MCP
2. **Duplicate Prevention**: Never create Jira tickets for bugs marked "May Duplicate"
3. **Bidirectional Integrity**: Always update both original and duplicate bug references
4. **Status Tracking**: Prevent re-creating tickets for already tracked bugs
5. **Validation**: Verify bug format and required fields before Jira creation

## Error Handling

**Duplicate Detection Conflicts**:
```
If bug A references bug B as duplicate, but bug B references bug C:
→ Use sequential reasoning to resolve chain
→ Update all references to point to earliest bug (A or C)
→ Maintain bidirectional consistency
```

**Jira Creation Failures**:
```
If Jira ticket creation fails:
→ Keep bug status as "Untracked"
→ Log error in bug registry
→ Allow retry without duplication
```

## Success Criteria

✅ **Bug Clarity**: Each bug has clear symptoms, reproduction steps, expected vs actual behavior
✅ **Duplicate Detection**: >90% accuracy in identifying duplicate bugs
✅ **Bidirectional Integrity**: All duplicate references are consistent
✅ **Jira Integration**: Bugs successfully created as Jira tickets with proper formatting
✅ **Status Tracking**: Bug registry accurately reflects tracked vs untracked status

## Command Shortcuts

```bash
/bt add "<description>"           # Short form
/bt list                          # List all bugs
/bt list untracked                # List only untracked
/bt jira <id>                     # Create single Jira ticket
/bt jira-all                      # Create all untracked Jira tickets
```

---

**See BUGTRACK-ADVICE.md for implementation guidance and troubleshooting.**
