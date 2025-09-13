
# Comprehensive TDD Analysis Framework

## Step 1: Jira Integration Fix
```python
# Fix API endpoint (use v3 instead of deprecated v2)
jira_url = "https://nortal.atlassian.net/rest/api/3/search"

# Correct project identification
project_query = "project = 'CMZ' OR project = 'Cougar Mountain Zoo'"

# Get ALL tickets with pagination
for page in range(0, total_pages):
    tickets = get_jira_tickets(start_at=page*50, max_results=50)
```

## Step 2: Acceptance Criteria Extraction
```python
for ticket in all_tickets:
    # Parse description for AC patterns:
    # - "Given/When/Then" scenarios
    # - Bullet points with acceptance criteria
    # - "As a user" stories
    # - Numbered requirements
    acs = extract_all_acceptance_criteria(ticket.description)
```

## Step 3: Test-to-AC Mapping
```python
for ac in all_acceptance_criteria:
    # Find tests that validate this AC:
    # - Keyword matching in test names
    # - Test description analysis
    # - Ticket reference tracing
    covering_tests = find_tests_for_ac(ac)
```

## Step 4: True Coverage Calculation
```python
true_coverage = {
    'total_tickets': len(all_cmz_tickets),
    'total_acs': len(all_acceptance_criteria),
    'tested_acs': len([ac for ac in all_acs if ac.has_tests]),
    'coverage_percentage': (tested_acs / total_acs) * 100,
    'gaps': [ac for ac in all_acs if not ac.has_tests]
}
```

## Expected Results for CMZ Project:
- **100+ tickets** (not 27)
- **500+ acceptance criteria** (estimate 3-5 ACs per ticket)
- **True coverage percentage** (likely 15-30% initially)
- **400+ untested ACs** requiring test creation
