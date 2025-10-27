# Frontend Agent Playwright MCP Usage - Advice and Best Practices

## The Problem

Frontend verification agents can easily fall into the trap of **static code analysis instead of actual browser testing**. This creates false positives where features appear to work (code exists) but are actually broken in the browser.

### Example from 2025-10-12 Session

**What Happened:**
- frontend-feature-verifier agent completed and reported all features as "IMPLEMENTED (HIGH confidence)"
- Agent only read files, searched for patterns, analyzed code structure
- Agent never used Playwright MCP to actually open a browser or test functionality
- User caught this: "How did the frontend feature verifier complete without ever using tools like the Playwright MCP?"

**Impact:**
- False sense of security
- Hidden bugs not discovered until production
- Wasted time investigating why "tested" features don't work

## The Solution

### 1. Explicit Playwright MCP Requirements in Delegation Prompt

**BAD Delegation** (Static Analysis):
```python
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend implementation",
    prompt="""Verify frontend implementation for {feature_name}.

    VERIFICATION REQUIREMENTS:
    1. Verify components render correctly
    2. Check routing configuration
    3. Validate API integration
    4. Test user interactions
    """
)
```

**GOOD Delegation** (Browser Testing):
```python
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend implementation",
    prompt="""Verify frontend implementation for {feature_name} using ACTUAL browser testing.

CRITICAL REQUIREMENT: You MUST use Playwright MCP tools for ALL testing.
NEVER rely on static code analysis alone. Code existing ≠ code working.

REQUIRED PLAYWRIGHT MCP TOOLS:
- mcp__playwright__browser_navigate: Navigate to pages
- mcp__playwright__browser_snapshot: Capture page state
- mcp__playwright__browser_click: Click buttons/links
- mcp__playwright__browser_type: Enter text in inputs
- mcp__playwright__browser_evaluate: Execute JavaScript
- mcp__playwright__browser_console_messages: Check for errors

BROWSER TESTING WORKFLOW:
1. browser_navigate to http://localhost:3001
2. Type credentials: parent1@test.cmz.org / testpass123
3. Click sign in button
4. browser_snapshot to verify dashboard loaded
5. Navigate to feature pages (click links/buttons)
6. Test all interactive elements
7. Check console_messages for errors
8. Verify DynamoDB persistence (if applicable)

VERIFICATION REQUIREMENTS:
1. **Authenticate** - Use Playwright to login with test credentials
2. **Navigate** - Actually navigate to component pages in browser
3. **Interact** - Click buttons, type in inputs, submit forms
4. **Verify API Calls** - Check network requests succeed (200/201)
5. **Check Console** - Verify no errors in browser console

CRITICAL: You MUST actually use Playwright MCP. Static code analysis is NOT sufficient.
If you complete without using browser_navigate, browser_click, or browser_type tools, you did it WRONG.
"""
)
```

### 2. Required Tool Usage Validation

**After agent completes**, validate it actually used Playwright:

```python
# Check agent's tool usage in report
required_tools = [
    "mcp__playwright__browser_navigate",
    "mcp__playwright__browser_click",
    "mcp__playwright__browser_type"
]

tools_used = agent_report["tools_used"]

if not any(tool in tools_used for tool in required_tools):
    raise ValidationError(
        "Agent completed without using Playwright MCP! "
        "This is static analysis, not browser testing. "
        "Results are INVALID."
    )
```

### 3. Frontend URL Specification

Always provide the exact frontend URL in the delegation prompt:

```python
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend implementation",
    prompt=f"""Verify frontend implementation for {feature_name}.

FRONTEND_URL: http://localhost:3001
BACKEND_URL: http://localhost:8080

TEST CREDENTIALS:
- parent1@test.cmz.org / testpass123 (parent role)
- student1@test.cmz.org / testpass123 (student role)
- test@cmz.org / testpass123 (admin role)

START HERE:
1. Navigate to {FRONTEND_URL}
2. If not logged in, go to login page
3. Type email: parent1@test.cmz.org
4. Type password: testpass123
5. Click "Sign In" button
6. Verify dashboard loads
...
"""
)
```

### 4. Step-by-Step Browser Actions

Provide explicit step-by-step browser actions:

```python
BROWSER TESTING WORKFLOW:

STEP 1: Authentication
1. browser_navigate to http://localhost:3001
2. browser_snapshot (should see login page)
3. browser_type in email field: parent1@test.cmz.org
4. browser_type in password field: testpass123
5. browser_click on "Sign In" button
6. browser_snapshot (should see dashboard)

STEP 2: Navigate to Feature
7. browser_click on "Families" link
8. browser_snapshot (should see families page)
9. browser_click on "Add Family" button
10. browser_snapshot (should see family dialog)

STEP 3: Test Feature
11. browser_type in "Family Name" input: "Test Family"
12. browser_type in "Parent Email" input: "testparent@example.com"
13. browser_click on "Add Student" button
14. browser_type in student name: "Test Student"
15. browser_click on "Save" button
16. browser_snapshot (should see success message)

STEP 4: Verify Persistence
17. Check console for errors: browser_console_messages
18. Verify API call succeeded: check network logs
19. Query DynamoDB to confirm data persisted
```

## Common Pitfalls

### Pitfall 1: Agent Interprets "Verify" as "Check Code Exists"

**Problem:** Agent reads files, sees component code, declares it "verified"

**Solution:** Use "Test in browser" language instead of "Verify"
```python
description="Test frontend in browser"  # Better
description="Verify frontend implementation"  # Too vague
```

### Pitfall 2: Agent Uses Read Tool Instead of Playwright

**Problem:** Agent defaults to familiar Read tool, avoids learning new Playwright tools

**Solution:** Explicitly list Playwright tools with examples
```python
REQUIRED TOOLS (YOU MUST USE THESE):
- mcp__playwright__browser_navigate(url="http://localhost:3001")
- mcp__playwright__browser_type(element="email input", ref="e123", text="test@example.com")
- mcp__playwright__browser_click(element="sign in button", ref="e456")
```

### Pitfall 3: Agent Skips Browser Testing Due to Complexity

**Problem:** Browser testing is harder than file reading, agent takes easy path

**Solution:** Add validation requirement in deliverables
```python
DELIVERABLES:
1. Browser test execution log (MUST show Playwright tool usage)
2. Screenshots of each tested page (from browser_snapshot)
3. Console error report (from browser_console_messages)
4. Network request validation (API calls succeeded)

VALIDATION: If you complete without screenshots from browser_snapshot, your testing is INVALID.
```

### Pitfall 4: No Test Credentials Provided

**Problem:** Agent doesn't know how to authenticate

**Solution:** Always provide test user credentials in prompt
```python
TEST USERS (USE THESE FOR AUTHENTICATION):
- Admin: test@cmz.org / testpass123
- Parent: parent1@test.cmz.org / testpass123
- Student: student1@test.cmz.org / testpass123
- Zookeeper: zookeeper1@test.cmz.org / testpass123

START WITH: parent1@test.cmz.org / testpass123 (most common test user)
```

## Validation Checklist

Before accepting frontend agent results, verify:

- [ ] Agent used `mcp__playwright__browser_navigate` at least once
- [ ] Agent used `mcp__playwright__browser_click` to interact with UI
- [ ] Agent used `mcp__playwright__browser_type` to enter text
- [ ] Agent used `mcp__playwright__browser_snapshot` to verify pages
- [ ] Agent checked `mcp__playwright__browser_console_messages` for errors
- [ ] Agent actually logged in with test credentials
- [ ] Agent tested interactive elements (buttons, forms, dialogs)
- [ ] Agent verified API calls succeeded (not just code exists)
- [ ] Report includes screenshots or page snapshots
- [ ] Report includes console error analysis

**If any checklist item is missing, agent did static analysis instead of browser testing.**

## Updated Agent Templates

The following files have been updated with Playwright MCP requirements:

1. **`.claude/AGENT-DELEGATION-TEMPLATES.md`**
   - `frontend-feature-verifier` template now requires Playwright MCP
   - Explicit tool usage requirements
   - Step-by-step browser workflow
   - Validation criteria

2. **`.claude/commands/frontend-comprehensive-testing.md`**
   - Should be updated to require Playwright MCP (if not already)

3. **`FRONTEND-COMPREHENSIVE-TESTING-ADVICE.md`**
   - Should reference Playwright MCP requirements

## Example: Correct Frontend Verification

```python
# Delegation with explicit Playwright requirements
Task(
    subagent_type="frontend-feature-verifier",
    description="Test Family Dialog in browser",
    prompt="""Test Family Dialog feature using Playwright MCP browser automation.

FEATURE: Family Dialog (Add/Edit/Delete families)
FRONTEND_URL: http://localhost:3001
TEST USER: parent1@test.cmz.org / testpass123

REQUIRED TOOLS (YOU MUST USE):
1. browser_navigate - Go to frontend URL
2. browser_type - Enter credentials and form data
3. browser_click - Click buttons and links
4. browser_snapshot - Capture page state for verification
5. browser_console_messages - Check for JavaScript errors

BROWSER TEST WORKFLOW:

Phase 1: Authentication
1. Navigate to http://localhost:3001
2. Type email: parent1@test.cmz.org
3. Type password: testpass123
4. Click "Sign In" button
5. Verify dashboard loads (snapshot)

Phase 2: Open Family Dialog
6. Click "Families" navigation link
7. Verify families page loads (snapshot)
8. Click "Add Family" button
9. Verify dialog opens (snapshot)

Phase 3: Test Form Inputs
10. Type family name: "Test Family Browser"
11. Type parent email: "testparent@example.com"
12. Click "Add Student" button
13. Type student name: "Test Student 1"
14. Verify student added to list (snapshot)

Phase 4: Save and Verify
15. Click "Save" button
16. Verify success message (snapshot)
17. Check console for errors
18. Verify family appears in table
19. Query DynamoDB to confirm persistence

VALIDATION REQUIREMENTS:
- Must use ALL 5 required Playwright tools
- Must include page snapshots for each phase
- Must check console for errors
- Must verify DynamoDB persistence
- Must test in actual browser (not code analysis)

DELIVERABLES:
1. Phase-by-phase test execution log
2. Page snapshots (4+ screenshots)
3. Console error report (should be empty)
4. DynamoDB verification results
5. Test summary (PASS/FAIL with evidence)

CRITICAL: This is BROWSER TESTING not code review.
You MUST actually open a browser and test the feature.
"""
)
```

## Integration with Test Orchestrator

When test orchestrator delegates to frontend-feature-verifier:

```python
# In orchestrate-tests.md Phase 2
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend features",
    prompt="""Verify ALL frontend features with Playwright MCP browser automation.

CRITICAL REQUIREMENT: You MUST use Playwright MCP tools for ALL testing.
NEVER rely on static code analysis alone. Code existing ≠ code working.

See .claude/AGENT-DELEGATION-TEMPLATES.md for complete Playwright workflow.
See FRONTEND-AGENT-PLAYWRIGHT-ADVICE.md for best practices.

FRONTEND_URL: http://localhost:3001
TEST USERS: parent1@test.cmz.org / testpass123

FEATURES TO TEST:
- Authentication (login, logout, role detection)
- Dashboard (statistics, quick actions, navigation)
- Family Dialog (add, edit, delete operations)
- Animal Config Dialog (all 30 fields)
- Chat (send messages, view history)
- Backend Health Detection (error messages)

For each feature:
1. Use Playwright to navigate and interact
2. Verify UI renders correctly (snapshots)
3. Test user interactions (clicks, typing)
4. Check API calls succeed
5. Verify DynamoDB persistence
6. Check console for errors

VALIDATION: Your report MUST include evidence of Playwright usage:
- Page snapshots from each feature
- Console messages analysis
- Network request validation
- Browser interaction logs

If you complete without using browser_navigate, browser_click, browser_type tools,
you did STATIC ANALYSIS not BROWSER TESTING. Results will be REJECTED.
"""
)
```

## Summary

**Key Lesson:** Always explicitly require Playwright MCP usage in frontend agent delegation prompts.

**Golden Rule:** Code existing ≠ code working. Only browser testing proves functionality.

**Validation:** Check agent tool usage before accepting results. If no Playwright tools used, results are invalid.

**Documentation Updated:**
- `.claude/AGENT-DELEGATION-TEMPLATES.md` - frontend-feature-verifier template
- `FRONTEND-AGENT-PLAYWRIGHT-ADVICE.md` - This document

**Next Steps:**
1. Update any remaining frontend testing documentation
2. Add validation checks to test orchestrator
3. Create automated tool usage verification
4. Document this pattern for other testing agents (backend, persistence)
