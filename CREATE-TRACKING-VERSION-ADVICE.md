# Version Tracking System - Best Practices & Troubleshooting

## Overview
This advice file provides best practices, common pitfalls, and troubleshooting guidance for the CMZ API version tracking system using UUIDs.

## When to Generate New UUIDs

### ✅ ALWAYS Generate New UUID When:
- **Major API Changes**: New endpoints, breaking changes to existing endpoints
- **Deployment to Production**: Every production deployment should have unique UUID
- **Significant Architecture Changes**: Database schema changes, authentication updates
- **Frontend Compatibility Changes**: Updates that affect frontend integration requirements
- **After Merging Feature Branches**: Major feature merges that change API behavior
- **Security Updates**: Any security-related changes to the API

### ⚠️ CONSIDER Generating New UUID When:
- **Bug Fixes**: If the fix changes API behavior or responses significantly
- **Performance Improvements**: Major optimizations that could affect response timing
- **Configuration Changes**: Environment or deployment configuration updates
- **Dependency Updates**: Major library or framework updates

### ❌ DON'T Generate New UUID For:
- **Documentation Updates**: README, comment changes, documentation files
- **Test-Only Changes**: Adding or modifying tests without code changes
- **Code Style Changes**: Linting, formatting, variable renaming (non-functional)
- **Development Experiments**: Temporary changes not intended for production

## Best Practices

### UUID Management
- **One UUID per Feature Branch**: Generate UUID when creating significant feature branches
- **Descriptive commit messages**: Always include UUID in commit message when updating version.json
- **Team Communication**: Notify team when generating new UUIDs for shared environments
- **Backup UUIDs**: Keep version_history.md updated as backup reference

### Version.json Maintenance
```json
{
  "description": "Use clear, descriptive messages like 'Add animal details endpoint with validation'"
}
```
- **Clear Descriptions**: Always provide meaningful description of what changed
- **Accurate Git Hashes**: Ensure git_commit_hash matches the actual commit
- **Frontend Versioning**: Keep frontend compatibility versions current and accurate

### Validation Workflow
```bash
# ALWAYS validate before testing
scripts/validate_version.py || exit 1

# ALWAYS validate after API changes
make generate-api && make build-api && scripts/validate_version.py

# ALWAYS validate in CI/CD pipeline
scripts/validate_version.py && npm test
```

## Common Pitfalls & Solutions

### 1. UUID Mismatch Errors
**Symptom**: Validation fails with "UUID mismatch" error

**Common Causes:**
- Old API server still running (different UUID)
- version.json not updated after git pull
- Docker container using cached version

**Solutions:**
```bash
# Stop and rebuild API server
make stop-api && make clean-api
make build-api && make run-api

# Verify version.json is current
git pull origin dev
cat version.json

# Clear Docker cache if necessary
docker system prune -f
```

### 2. Missing version.json
**Symptom**: "version.json not found" error

**Solutions:**
```bash
# Check if file exists
ls -la version.json

# If missing, run the creation command
/create-tracking-version

# If in wrong directory
cd /path/to/cmz-chatbots/
```

### 3. Healthcheck Endpoint Not Responding
**Symptom**: Connection errors when validating

**Troubleshooting Steps:**
```bash
# Check if API server is running
curl http://localhost:8080/system_health

# Check Docker container status
docker ps | grep cmz

# Check logs for errors
make logs-api

# Restart API server
make stop-api && make run-api
```

### 4. Frontend Version Compatibility Issues
**Symptom**: Frontend fails to work with API despite validation passing

**Solutions:**
- Update frontend_min_version/max_version in version.json
- Check frontend package.json version matches compatibility range
- Test frontend against API manually before updating compatibility versions

### 5. Git Merge Conflicts in version.json
**Symptom**: Merge conflicts when pulling/merging branches

**Resolution Strategy:**
```bash
# Accept YOUR version if you generated new UUID
git checkout --ours version.json

# Accept THEIR version if they generated newer UUID
git checkout --theirs version.json

# Always verify which UUID is newer using version_history.md
cat version_history.md | tail -5

# Update version_history.md after resolving conflict
```

## Troubleshooting Commands

### Diagnostic Commands
```bash
# Check current system state
cat version.json | jq '.'
curl -s http://localhost:8080/system_health | jq '.'
docker ps | grep cmz
git rev-parse HEAD

# Test version validation
python scripts/validate_version.py --verbose

# Check version history
cat version_history.md | tail -10
```

### Recovery Commands
```bash
# Full system reset
make stop-api && make clean-api
git pull origin dev
make generate-api && make build-api && make run-api
scripts/validate_version.py

# Generate new UUID if needed
NEW_UUID=$(python3 -c "import uuid; print(str(uuid.uuid4()))")
echo "New UUID: $NEW_UUID"
```

## Performance Considerations

### Validation Speed
- **Target Time**: < 2 seconds for complete validation
- **Timeout Settings**: Set reasonable timeouts for API calls (5-10 seconds)
- **Caching**: Consider caching validation results for repeated test runs

### Docker Performance
- **Layer Caching**: Ensure version.json changes don't invalidate entire Docker cache
- **Health Check**: Use Docker health checks with version validation
- **Container Restart**: Fast restart strategy when version changes

## Integration Patterns

### CI/CD Integration
```yaml
# Example GitHub Actions step
- name: Validate API Version
  run: |
    scripts/validate_version.py
    if [ $? -ne 0 ]; then
      echo "Version validation failed"
      exit 1
    fi
```

### Pre-commit Hooks
```bash
#!/bin/sh
# .git/hooks/pre-commit
scripts/validate_version.py || {
  echo "Version validation failed - commit blocked"
  exit 1
}
```

### Test Integration
```bash
# Always validate before running test suites
validate_and_test() {
  scripts/validate_version.py || return 1
  python -m pytest tests/
}
```

## Team Collaboration Guidelines

### UUID Coordination
1. **Communicate**: Notify team before generating UUIDs for shared branches
2. **Document**: Always update version_history.md with clear descriptions
3. **Review**: Include UUID changes in code review process
4. **Merge Strategy**: Handle UUID conflicts carefully during merges

### Environment Management
- **Development**: Each developer can use their own UUIDs
- **Staging**: Coordinate UUID changes for shared staging environment
- **Production**: Strict control over production UUID generation

## Monitoring & Alerting

### Key Metrics to Track
- Version validation success rate
- Time between UUID generation and deployment
- Frequency of UUID mismatches
- Frontend compatibility failures

### Alert Scenarios
- Version validation failures in CI/CD
- UUID mismatches in production
- Extended periods without UUID updates (potential stale deployments)

## Emergency Procedures

### Production Version Mismatch
1. **Immediate**: Stop problematic deployments
2. **Validate**: Check version.json against deployed code
3. **Fix**: Update version or redeploy correct version
4. **Verify**: Run full validation suite
5. **Document**: Update incident log with root cause

### UUID History Corruption
1. **Backup**: Check git history for version_history.md
2. **Reconstruct**: Use git log and commit messages to rebuild history
3. **Validate**: Cross-reference with deployment logs
4. **Update**: Restore complete version_history.md

## Advanced Usage

### Multiple Environment UUIDs
```json
{
  "api_version_uuid": "primary-uuid",
  "environment_uuids": {
    "development": "dev-specific-uuid",
    "staging": "staging-specific-uuid",
    "production": "prod-specific-uuid"
  }
}
```

### Automated UUID Generation
```bash
# Script for automated UUID generation on deployment
generate_deployment_uuid() {
  local description="$1"
  local new_uuid=$(python3 -c "import uuid; print(str(uuid.uuid4()))")

  jq --arg uuid "$new_uuid" \
     --arg desc "$description" \
     --arg date "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --arg hash "$(git rev-parse HEAD)" \
     '.api_version_uuid = $uuid | .description = $desc | .created_date = $date | .git_commit_hash = $hash' \
     version.json > version.json.tmp

  mv version.json.tmp version.json
  echo "Generated UUID: $new_uuid"
}
```

## Related Documentation
- `.claude/commands/create_tracking_version.md` - Implementation command
- `version_history.md` - Historical UUID record
- CMZ API documentation for healthcheck endpoints