# /report-bugs Command Template

**Use this prompt after a validation test that finds issues - analyzes validation results using sequential reasoning and presents comprehensive bug tickets for creation:**

### Basic Usage
```
/report-bugs
# Analyzes most recent validation results and generates bug tickets
```

### Implementation Template
```
Analyze the results from the most recent validation test using sequential reasoning and create comprehensive Jira bug tickets for all identified issues.

**MANDATORY FIRST STEP**: Read NORTAL-JIRA-ADVICE.md to understand ticket creation requirements and patterns.

## Context
- Recently completed validation test with mixed/failed results
- Need to convert validation findings into actionable bug tickets
- Must follow Nortal Jira project standards and custom field requirements
- Focus on issues that block production deployment or user functionality

## Required Process - Sequential Reasoning Analysis

### Step 1: Sequential Reasoning Assessment
Use sequential reasoning MCP to systematically analyze validation results:
- **Root Cause Analysis**: Identify underlying technical causes for each issue
- **Impact Assessment**: Determine business and technical impact severity
- **Bug Classification**: Categorize issues by type (integration, validation, implementation, etc.)
- **Priority Ranking**: Order by severity and blocking potential
- **Reproducibility Validation**: Confirm issues can be consistently reproduced

### Step 2: NORTAL-JIRA-ADVICE Integration
- **CRITICAL**: All bug tickets MUST include `"customfield_10225": {"value": "Billable"}`
- **Project**: PR003946 (CMZ - AI-Based Animal Interaction)
- **Issue Type**: Bug (for validation failures)
- **Authentication**: Use .env.local Basic auth credentials
- **API Version**: REST API v3 endpoints (`/rest/api/3/issue`)

### Step 3: Comprehensive Bug Ticket Structure

For each identified bug, create tickets with:

#### **Required Ticket Elements**
- **Summary**: Clear, specific bug title indicating impact and component
- **Description**: Atlassian Document Format with structured sections
- **Priority**: High/Medium/Low based on blocking severity
- **Issue Type**: Bug
- **Custom Field**: Billable = true (customfield_10225)

#### **Description Structure Template**
```
## Problem Statement
[Clear description of the bug and its manifestation]

## Impact Analysis
[Business and technical impact, user experience effects]
- **Severity**: Critical/High/Medium/Low
- **Scope**: Which components/users affected
- **Blocking**: What functionality is prevented

## Reproduction Steps
1. [Exact step-by-step instructions]
2. [Include environment setup requirements]
3. [Specific commands, URLs, or actions]
4. [Expected vs actual results at each step]

## Expected vs Actual Behavior
**Expected**: [What should happen when working correctly]
**Actual**: [What actually happens, including error messages]

## Technical Analysis
**Root Cause**: [Technical explanation of underlying issue]
**Evidence**: [Log entries, error messages, HTTP responses]
**Component**: [Which system component contains the bug]
**Dependencies**: [Related systems or issues]

## Acceptance Criteria
- [ ] [Specific, testable condition 1]
- [ ] [Specific, testable condition 2]
- [ ] [Verification method specified]
- [ ] [Performance/quality requirements]
- [ ] [Integration test passing criteria]

## Story Points Estimate (in comments)
**Complexity**: [2-3 for simple fixes, 5-8 for integration issues, 8-13 for major rework]
**Rationale**: [Brief explanation of effort estimation]
```

### Step 4: Bug Categorization

**Critical Bugs (Priority: High)**:
- Authentication/security failures
- Complete feature blockages
- Data corruption or loss
- Service unavailability

**Major Bugs (Priority: Medium)**:
- Partial feature failures
- Performance degradation
- User experience issues
- Integration inconsistencies

**Minor Bugs (Priority: Low)**:
- UI inconsistencies
- Non-blocking validation errors
- Edge case handling
- Documentation gaps

### Step 5: Ticket Presentation and Creation

Present each ticket for user confirmation, then create in Jira:

```
## 🔴 BUG TICKET [X]: [Summary]
**Priority**: High/Medium/Low
**Story Points**: [Estimate]
**Component**: [Frontend/Backend/Integration]

[Full ticket description preview]

---
```

### Step 6: Jira Ticket Creation

After presenting all tickets for user review:

1. **Ask for Confirmation**: "Shall I create these [X] bug tickets in the CMZ Jira project (PR003946)?"

2. **Upon User Confirmation**: Use Jira MCP to create each ticket:
   - **Project**: PR003946
   - **Issue Type**: Bug
   - **Required Custom Field**: `customfield_10225: {"value": "Billable"}`
   - **Authentication**: Uses .env.local credentials automatically

3. **Creation Results**: Report ticket keys and URLs:
   ```
   ✅ Created PR003946-XXX: [Bug Summary]
   🔗 https://nortal.atlassian.net/browse/PR003946-XXX
   📊 Story Points: [Estimate]
   ```

4. **Summary Report**: Provide final count and links to all created tickets

## Success Criteria

- **Complete Coverage**: All validation failures converted to tickets
- **Technical Accuracy**: Root causes correctly identified and explained
- **Reproducible**: Clear reproduction steps that consistently demonstrate issues
- **Actionable**: Acceptance criteria are specific and testable
- **NORTAL Standards**: All tickets follow project conventions and include required fields
- **Priority Appropriate**: Critical bugs blocking production identified as High priority

## Quality Validation

Before presenting tickets:
- **Sequential Reasoning Verification**: Confirm root cause analysis is sound
- **Reproduction Testing**: Verify steps actually reproduce the issues
- **Acceptance Criteria Review**: Ensure criteria are measurable and complete
- **Custom Fields Check**: Confirm Billable field will be included
- **Priority Validation**: High priority reserved for production blockers

**Output**:
1. Present 3-5 comprehensive bug tickets for user review
2. Upon confirmation, create all tickets in Jira project PR003946
3. Provide summary with ticket keys, URLs, and story point totals
```