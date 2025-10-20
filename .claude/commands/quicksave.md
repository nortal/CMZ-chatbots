# Quick Save Command

Save session state with Serena MCP and generate a session history file for long-term record keeping.

## Tasks

1. **Run /sc:save** to checkpoint session memory via Serena MCP
2. **Gather session context**:
   - Current timestamp and session duration estimate
   - Git status (changed files, branch)
   - Recent commits (last 5 with timestamps)
   - Active Jira tickets (grep history and recent commits for PR003946-*)
   - TodoWrite status if active
3. **Generate session history file** in `history/` directory
   - Format: `kc.stegbauer_YYYY-MM-DD_HHh-HHh.md`
   - Include: Tickets worked, prompts given, files changed, decisions made, next steps
4. **Confirm completion** with file path and summary

## Session History File Format

Use this template:

```markdown
# Session: [Date] [Start Time] - [End Time]

**Duration**: [X hours]
**Branch**: [current git branch]

## Jira Tickets Worked

- **[TICKET-ID]**: [Brief description of work done]

## Work Summary

### Tasks Completed
- [Task 1 description]
- [Task 2 description]

### Files Changed
[List from git status]

### Key Decisions Made
- [Decision 1]
- [Decision 2]

### Prompts & Commands Used
- [Key prompts or slash commands]

## Next Steps

- [ ] [Next task 1]
- [ ] [Next task 2]

## Git Activity

### Recent Commits
[Last 5 commits with timestamps and messages]

### Branch Status
[Git status output summary]

## Notes

[Any additional context, blockers, or observations]

---

**Session saved**: [Timestamp]
**Serena checkpoint**: ✅ Completed
```

## Execution Instructions

1. First run `/sc:save` using SlashCommand tool
2. **IMPORTANT**: Use a SINGLE Bash tool call to gather all git information sequentially:
   ```bash
   echo "=== BRANCH ===" && \
   git branch --show-current && \
   echo -e "\n=== STATUS ===" && \
   git status --short && \
   echo -e "\n=== RECENT COMMITS ===" && \
   git log -5 --pretty=format:"%h - %ad - %s" --date=format:"%Y-%m-%d %H:%M" && \
   echo -e "\n=== JIRA TICKETS ===" && \
   git log -10 --all --grep="PR003946-" --pretty=format:"%s" && \
   echo -e "\n=== TIMESTAMP ===" && \
   date +"%Y-%m-%d_%Hh"
   ```
   **Note**: All commands must run in a single bash call using && to avoid concurrency errors
3. Create session history file with Write tool at:
   `/Users/keithstegbauer/repositories/CMZ-chatbots/history/kc.stegbauer_[timestamp].md`
4. Report back with:
   - Serena checkpoint status
   - Session history file path
   - Quick summary (tickets worked, files changed, duration estimate)

## Notes

- If exact start time unknown, estimate based on recent git activity or use "Xh" format
- Include ALL changed files, even uncommitted ones
- Extract Jira tickets from commits and context
- Keep summary concise but complete enough for velocity analysis later
- File should be immediately readable by jira-velocity-analyzer agent
