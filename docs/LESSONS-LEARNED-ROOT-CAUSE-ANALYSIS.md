# Lessons Learned: Root Cause Analysis Process

## Date: 2025-10-12
## Session: Bug #8 Investigation Correction

### Critical Oversight Identified

**Issue**: Root-cause-analyst made inference about DynamoDB table state without actual verification

**What Happened**:
1. Bug #8 was reported as "Family Management page shows 'No families found'"
2. Root-cause-analyst examined backend code
3. Found that code looks correct and would return `[]` if table empty
4. **INCORRECTLY INFERRED** that table must be empty
5. Concluded "Not a bug - missing test data"

**Reality** (after actual DynamoDB query):
- quest-dev-family table contains **33 families**
- **4+ active families** with `softDelete: false`
- Table is **NOT empty** - conclusion was wrong
- Real root cause is user-specific filtering or association issue

### Why This Matters

**Impact of Wrong Conclusion**:
- Bug classified as "Not a bug - needs seed data"
- Would have wasted time creating seed data
- Real bug (user-family association or filtering) would remain unfixed
- Users continue seeing empty list despite data existing

**Core Problem**:
Code inspection alone cannot verify database state. Must query actual database.

### Mandatory Process Changes

**For ALL "empty database" claims, root-cause-analyst MUST:**

1. **Actually Query DynamoDB**:
   ```bash
   aws dynamodb scan \
     --table-name [table_name] \
     --region us-west-2 \
     --profile cmz \
     --max-items 10
   ```

2. **Verify Table Exists**:
   ```bash
   aws dynamodb list-tables \
     --region us-west-2 \
     --profile cmz | grep [table_name]
   ```

3. **Check Item Count**:
   ```bash
   aws dynamodb scan \
     --table-name [table_name] \
     --region us-west-2 \
     --profile cmz \
     --select "COUNT"
   ```

4. **Document Findings**:
   - Include actual query output
   - Show item count
   - Show sample items (sanitized if needed)
   - State "VERIFIED via DynamoDB query" not "inferred from code"

### Updated Agent Instructions

**Added to `.claude/agents/AGENT_IDEAS.md`:**

```markdown
### Database State Verification

When investigating bugs involving "empty lists" or "missing data":

❌ **NEVER** conclude "empty database" from code inspection alone
✅ **ALWAYS** query actual database to verify state

**Verification Steps**:
1. Run `aws dynamodb scan` to check actual table contents
2. Document query results with item counts
3. Distinguish between:
   - Table doesn't exist (infrastructure)
   - Table exists but empty (seed data)
   - Table has data but query returns empty (filtering/association bug)
```

### Comparison: Wrong vs Correct Analysis

**WRONG Analysis** (inference-based):
```
Evidence:
1. Backend code looks correct ✅
2. Would return [] if table empty ✅
3. [INFERRED] Table must be empty
Conclusion: Not a bug, needs seed data
```

**CORRECT Analysis** (verification-based):
```
Evidence:
1. Backend code looks correct ✅
2. aws dynamodb scan shows 33 families ✅
3. 4+ families have softDelete: false ✅
4. API returns [] despite data existing ✅
Conclusion: Real bug - user filtering or association issue
```

### Tools Available for Verification

Root-cause-analyst agents have access to Bash tool and can run:
- `aws dynamodb scan` - Check table contents
- `aws dynamodb list-tables` - Verify table exists
- `aws dynamodb describe-table` - Get table metadata
- `aws dynamodb query` - Test specific queries

**No Excuse for Skipping Verification**: All tools needed are available.

### Similar Bugs to Re-Check

Based on this finding, we should re-verify ANY bug where root-cause-analyst concluded:
- "Empty database"
- "Missing seed data"
- "No test data"
- "Table is empty"

**Unless the agent provides actual DynamoDB query output, the conclusion is suspect.**

### Action Items

1. ✅ Add database verification to agent instructions
2. ✅ Document this lesson in project docs
3. ⏳ Re-investigate Bug #8 with actual DynamoDB state
4. ⏳ Add DynamoDB verification to E2E test strategy
5. ⏳ Update quality-engineer strategy to include database state validation

### Acknowledgment

**Credit**: User identified this oversight by asking "did it actually interrogate the DynamoDB backend?" - excellent question that revealed flawed investigation process.

**Takeaway**: Always verify data state, never infer it. Code tells you what SHOULD happen, database tells you what DID happen.
