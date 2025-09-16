# Create API Version Tracking System

**Purpose**: Implement a comprehensive version tracking system using random UUIDs to ensure we're running the expected version of both API and frontend components before testing and deployment.

## Context
This system addresses the critical need to validate that:
- The running API server corresponds to the current codebase version
- Frontend compatibility requirements are met
- Test environments are using expected versions
- Version history is maintained for troubleshooting and rollbacks

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically plan and implement this version tracking system:

### Phase 1: Analysis & Planning (Required)
**Use Sequential Reasoning to:**
1. **Analyze Current State**: Examine existing healthcheck endpoint and system architecture
2. **Plan UUID Strategy**: Design how UUIDs will be generated, stored, and validated
3. **Frontend Integration Planning**: Determine how frontend version compatibility will be handled
4. **Validation Strategy**: Plan comprehensive validation workflow before test execution

**Key Questions for Sequential Analysis:**
- What information should be tracked in version.json?
- How will the healthcheck endpoint be enhanced without breaking existing functionality?
- What validation steps are needed before running tests?
- How should version history be maintained?

### Phase 2: Implementation (Systematic)
**Implementation Order (Follow Exactly):**

#### Step 1: Create Version Infrastructure
```bash
# Generate new UUID for this version
NEW_UUID=$(python3 -c "import uuid; print(str(uuid.uuid4()))")
echo "Generated UUID: $NEW_UUID"

# Create version.json in project root
cat > version.json << EOF
{
  "api_version_uuid": "$NEW_UUID",
  "created_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "description": "Initial version tracking implementation",
  "git_commit_hash": "$(git rev-parse HEAD)",
  "frontend_compatibility_version": "1.0",
  "frontend_min_version": "1.0",
  "frontend_max_version": "1.1"
}
EOF
```

#### Step 2: Enhance Healthcheck Endpoint
```bash
# Modify backend/api/src/main/python/openapi_server/impl/system.py
# Add version information to healthcheck response
```

#### Step 3: Update OpenAPI Specification
```bash
# Update backend/api/openapi_spec.yaml
# Add version fields to healthcheck response schema
```

#### Step 4: Create Validation Script
```bash
# Create scripts/validate_version.py
# Implement version validation logic
```

#### Step 5: Regenerate API Code
```bash
# Regenerate API server with updated specification
make generate-api
make build-api
```

### Phase 3: Validation & Testing (Comprehensive)
**Validation Checklist:**
1. **Version File Validation**: Verify version.json exists and contains valid UUID
2. **API Server Testing**: Start server and query healthcheck endpoint
3. **UUID Consistency**: Confirm returned UUID matches version.json
4. **Frontend Compatibility**: Validate frontend version information is returned
5. **Validation Script Testing**: Ensure validation script works correctly
6. **Integration Testing**: Run full test suite with version validation

**Required Commands:**
```bash
# Start API server
make run-api

# Test healthcheck endpoint
curl http://localhost:8080/system/health | jq '.'

# Run version validation
python scripts/validate_version.py

# Run tests with version validation
python scripts/validate_version.py && python -m pytest tests/
```

### Phase 4: Documentation & History (Essential)
1. **Update Version History**: Add entry to version_history.md
2. **Document Changes**: Update relevant documentation
3. **Commit Changes**: Commit version.json and all related changes to git
4. **Verify End-to-End**: Final validation that entire system works

## Implementation Details

### Version.json Schema
```json
{
  "api_version_uuid": "uuid-string",
  "created_date": "ISO-8601-timestamp",
  "description": "human-readable-description",
  "git_commit_hash": "git-commit-hash",
  "frontend_compatibility_version": "semantic-version",
  "frontend_min_version": "minimum-compatible-version",
  "frontend_max_version": "maximum-compatible-version"
}
```

### Enhanced Healthcheck Response
```json
{
  "status": "healthy",
  "timestamp": "current-timestamp",
  "api_version_uuid": "from-version-json",
  "frontend_compatibility": {
    "version": "current-compatibility-version",
    "min_version": "minimum-supported",
    "max_version": "maximum-supported"
  },
  "git_commit_hash": "current-commit"
}
```

### Validation Script Requirements
The validation script must:
- Read version.json from project root
- Query API healthcheck endpoint
- Compare UUIDs for exact match
- Validate frontend compatibility information
- Return clear success/failure status with detailed error messages
- Exit with appropriate status codes (0 = success, 1 = failure)

## Integration Points

### Pre-Test Validation Pattern
```bash
# Always run before tests
scripts/validate_version.py || { echo "Version validation failed - aborting tests"; exit 1; }

# Integrated test command
scripts/validate_version.py && python -m pytest tests/integration/
```

### Docker Integration
```bash
# Ensure version.json is copied to Docker container
# Update Dockerfile if necessary
```

### Git Workflow Integration
```bash
# Version.json should be committed to git
git add version.json version_history.md
git commit -m "Add version tracking system with UUID: $NEW_UUID"
```

## Quality Gates

### Mandatory Validation Before Completion
- [ ] version.json exists and contains valid UUID
- [ ] Healthcheck endpoint returns version information
- [ ] UUID returned by API matches version.json exactly
- [ ] Frontend compatibility information is complete
- [ ] Validation script executes successfully
- [ ] All existing tests continue to pass
- [ ] Version history is updated
- [ ] Changes are committed to git

### Error Scenarios to Test
1. **Missing version.json**: Script should fail gracefully with clear error
2. **API server not running**: Should provide clear connection error
3. **UUID mismatch**: Should identify specific mismatch and provide both UUIDs
4. **Malformed version.json**: Should validate JSON structure
5. **Frontend version issues**: Should validate frontend compatibility fields

## Success Criteria
1. **Deterministic Validation**: Same version.json + same codebase = validation success
2. **Clear Error Messages**: All failure scenarios provide actionable feedback
3. **Performance**: Validation completes in < 2 seconds
4. **Integration**: Works seamlessly with existing development workflow
5. **History Tracking**: All version changes are documented and traceable

## Next Steps After Implementation
1. Integrate validation into CI/CD pipeline
2. Add version validation to all test scripts
3. Create documentation for team on when to generate new UUIDs
4. Consider automating UUID generation for major deployments

## References
- `CREATE-TRACKING-VERSION-ADVICE.md` - Best practices and troubleshooting
- `version_history.md` - Historical record of all UUIDs used
- CMZ API documentation for existing healthcheck patterns