# Resolve Comments Command

## Usage

```
/resolve-comments
```

Use this command after receiving review feedback to systematically address all comments and ensure proper resolution documentation.

## Overview

This command guides you through the systematic resolution of all review comments (both general PR comments and inline code comments), ensuring each is properly addressed and documented according to CMZ project standards.

## Prerequisites

- You have received review feedback on your MR
- You are ready to address the feedback systematically
- You have the MR number available

## Process

### 1. Get Comment Overview

First, understand what feedback you've received:

```bash
# Get your current PR number
PR_NUMBER=$(gh pr list --head $(git branch --show-current) --json number --jq '.[0].number')
echo "Working with PR #$PR_NUMBER"

# View all comments and reviews
gh pr view $PR_NUMBER --json comments,reviews

# Get a simple view of comments
gh pr view $PR_NUMBER --comments
```

### 2. Address Each Inline Comment Systematically

For each inline comment in your code:

#### Step 1: Identify the Issue
- Read the comment carefully
- Understand what the reviewer is asking for
- Note the file and line number

#### Step 2: Make the Required Changes
```bash
# Open the file and make the necessary changes
code path/to/file.py  # or your preferred editor

# Example changes based on common feedback:
# - Add input validation
# - Improve error messages
# - Add missing docstrings
# - Fix security issues
# - Remove unused imports
```

#### Step 3: Test Your Changes
```bash
# Run relevant tests to ensure your changes work
pytest tests/test_specific_functionality.py -v

# Run the function/endpoint manually to verify
python -c "from module import function; print(function(test_input))"
```

#### Step 4: Commit the Changes
```bash
# Commit with descriptive message referencing the feedback
git add path/to/file.py
git commit -m "Address review feedback: improve input validation in user creation"
```

#### Step 5: Document the Resolution
```bash
# Get the comment ID from the GitHub web interface
# Comment IDs appear in URLs like: #issuecomment-1234567890
# The ID is the number after "issuecomment-"

# Document how you resolved the issue
gh pr comment <COMMENT_ID> --body "✅ Resolved: Added email format validation using regex pattern and improved error message to provide clear guidance to users"
```

### 3. Address General PR Comments

For overall PR feedback:

#### Step 1: Make All Requested Changes
Address each point mentioned in the general comment:

```bash
# Example: "Please add error handling and improve test coverage"

# Add error handling
git add error_handling_improvements.py
git commit -m "Add comprehensive error handling for edge cases"

# Improve test coverage
git add new_tests.py
git commit -m "Add unit tests for error scenarios and edge cases"
```

#### Step 2: Provide Comprehensive Response
```bash
# After addressing all points, provide detailed response
gh pr comment $PR_NUMBER --body "All review feedback has been addressed:

✅ **Error Handling**: Added try-catch blocks for DynamoDB operations with proper error responses
✅ **Test Coverage**: Added 8 new unit tests covering edge cases and error scenarios (lines 45-120)
✅ **Input Validation**: Implemented validation for all required fields with clear error messages
✅ **Code Documentation**: Added docstrings to all public methods following project standards
✅ **Security Issues**: Resolved CodeQL findings - removed unused imports and improved error message security

**Files Modified:**
- \`impl/animals.py\`: Core logic improvements
- \`test/test_animals.py\`: Extended test coverage
- \`models/animal.py\`: Enhanced validation

All changes have been tested locally and are ready for re-review."
```

### 4. Final Verification

Before requesting re-review:

```bash
# Run complete test suite to ensure nothing broke
python -m pytest tests/integration/test_api_validation_epic.py -v

# Check for any new linting issues
flake8 backend/api/src/main/python/openapi_server/impl/

# Verify your changes work as expected
curl -X POST "http://localhost:8080/api/your-endpoint" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Push all changes
git push origin $(git branch --show-current)
```

### 5. Request Re-review

After all feedback is addressed:

```bash
# Add a final comment to request re-review
gh pr comment $PR_NUMBER --body "🔄 **Ready for Re-review**

All feedback has been addressed and documented. Key improvements:

- Enhanced error handling with proper HTTP status codes
- Improved input validation with clear user messages
- Extended test coverage for edge cases
- Resolved all CodeQL security findings
- Added comprehensive documentation

All tests passing locally. Please re-review when convenient."

# Optional: Request specific re-review if needed
gh pr edit $PR_NUMBER --add-reviewer SpecificReviewer
```

## Comment Resolution Templates

### For Input Validation Issues
```bash
gh pr comment <COMMENT_ID> --body "✅ Resolved: Added comprehensive input validation including:
- Email format validation using regex pattern
- Required field checks with clear error messages
- Data type validation for numeric fields
- Field length limits to prevent overflow

Updated tests to verify all validation scenarios work correctly."
```

### For Error Handling Issues
```bash
gh pr comment <COMMENT_ID> --body "✅ Resolved: Implemented robust error handling:
- Added try-catch blocks for all DynamoDB operations
- Using centralized error_response utility for consistent formatting
- Proper HTTP status codes (400 for validation, 500 for server errors)
- Sensitive error details logged but not exposed to users

Tested error scenarios manually and via unit tests."
```

### For Security Issues
```bash
gh pr comment <COMMENT_ID> --body "✅ Resolved: Addressed security concerns:
- Removed unused imports that triggered CodeQL warnings
- Improved error messages to avoid information disclosure
- Added input sanitization for user-provided data
- Verified no hardcoded secrets or credentials in code

Security scan now passes without warnings."
```

### For Performance Issues
```bash
gh pr comment <COMMENT_ID> --body "✅ Resolved: Optimized performance:
- Reduced database queries from N+1 to single batch operation
- Added response caching for frequently accessed data
- Implemented pagination for large result sets
- Measured 60% improvement in response time for typical requests

Load tested with 100 concurrent requests - all within acceptable limits."
```

### For Documentation Issues
```bash
gh pr comment <COMMENT_ID> --body "✅ Resolved: Enhanced documentation:
- Added comprehensive docstrings to all public methods
- Included parameter types and return value descriptions
- Added usage examples in docstrings
- Updated API documentation with new endpoint details

Documentation now follows project standards and provides clear guidance."
```

## Learning Integration

### Capture Learnings from Review Process

After resolving all comments:

```bash
# Document key learnings for future reference
echo "## Review Learnings - $(date +%Y-%m-%d)

### Feedback Themes
- [Most common type of feedback received]
- [Specific patterns that needed improvement]

### Effective Solutions
- [What worked well in addressing feedback]
- [Patterns that should be reused]

### Prevention Strategies
- [How to avoid similar issues in future MRs]
- [Process improvements identified]

### Reviewer Communication
- [What communication strategies worked best]
- [How to better explain technical decisions]
" >> learning_notes.md
```

### Update MR-ADVICE.md

Add new patterns discovered during the review process:

```bash
# Example addition to MR-ADVICE.md
echo "
### New Pattern: [Date]
**Issue**: [Description of common issue]
**Solution**: [Specific solution that worked]
**Prevention**: [How to avoid in future]
**Code Example**:
\`\`\`python
[Example implementation]
\`\`\`
" >> MR-ADVICE.md
```

## Troubleshooting

### Comment ID Issues

**Problem**: Can't find comment ID to resolve
**Solution**:
```bash
# Method 1: Check PR view for comment IDs
gh pr view $PR_NUMBER --json comments --jq '.comments[] | {id: .id, body: .body}'

# Method 2: Use GitHub web interface
# Navigate to PR → Find comment → Right-click → "Copy link address"
# URL format: https://github.com/owner/repo/pull/123#issuecomment-1234567890
# Use the number: 1234567890
```

### Changes Don't Resolve Issue

**Problem**: Reviewer says issue isn't fully resolved
**Solution**:
1. Ask for specific clarification in a new comment
2. Provide explanation of what you implemented
3. Offer to schedule a brief call to discuss if complex
4. Be open to different approaches

```bash
gh pr comment <COMMENT_ID> --body "I've implemented [specific change], but I want to make sure this fully addresses your concern.

What I changed:
- [Specific detail 1]
- [Specific detail 2]

Could you clarify if this meets your expectations, or if you had a different approach in mind? Happy to adjust further."
```

### Multiple Conflicting Reviewers

**Problem**: Two reviewers give conflicting feedback
**Solution**:
```bash
gh pr comment $PR_NUMBER --body "@reviewer1 @reviewer2 I've received conflicting guidance on [specific issue]:

**Reviewer 1 suggested**: [Approach A]
**Reviewer 2 suggested**: [Approach B]

Both approaches have merit. Could you help me understand:
- Which approach better fits our project standards?
- Are there specific concerns with either approach?
- Is there a hybrid solution that addresses both perspectives?

I'm happy to implement whichever direction you prefer."
```

## Success Criteria

Comments are properly resolved when:

- [ ] **All inline comments addressed** with specific code changes
- [ ] **All general PR comments addressed** with comprehensive responses
- [ ] **Each resolution documented** with clear explanation of what was changed
- [ ] **All changes tested** and working correctly
- [ ] **No new issues introduced** by the changes
- [ ] **Reviewer feedback acknowledged** and appreciated
- [ ] **Learning captured** for future improvement

## Integration with Other Workflows

This command works with:
- `/prepare-mr` - Use before initial MR creation
- `/nextfive` - Address feedback on implementation work
- Standard development workflow in CMZ project

After comment resolution is complete, your MR should be ready for final approval and merge.