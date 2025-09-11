# update_nextfive_progress Command

## Purpose
Centralized command to update job status file with step completion and capture immediate lessons learned.

## Parameters
- `step_name`: Name of completed step (discover, implement, validate, submit, update-jira)
- `status`: Step status (completed, failed, in_progress)
- `--lessons`: Optional lessons learned text or file
- `--results-file`: Path to step results file
- `--notes`: Additional recovery notes

## Usage Examples
```bash
# Mark discovery step complete with lessons
update_nextfive_progress discover completed \
  --results-file /tmp/discover_correlation_20250911_1445.json \
  --lessons "Found 7 failing tests vs predicted 5. Need git log analysis in discovery."

# Mark implementation in progress for specific ticket
update_nextfive_progress implement in_progress \
  --current-ticket PR003946-71 \
  --completed-tickets PR003946-69 \
  --lessons "ID generation took 4h vs predicted 2h due to UUID pattern complexity"

# Mark step failed with recovery information
update_nextfive_progress validate failed \
  --lessons "Docker container connectivity issues affected validation" \
  --recovery-notes "Restart container and verify system health before retrying"
```

## Execution Steps

### Step 1: Locate or Create Job Status File
```bash
# Find current job file or create new one
CURRENT_JOB=$(ls *.inprogress 2>/dev/null | head -1)

if [[ -z "$CURRENT_JOB" ]]; then
    # Create new job file if none exists
    TIMESTAMP=$(date +%Y-%m-%d-%Hh%M)
    
    # Try to extract tickets from recent discovery results
    DISCOVERY_FILE=$(ls -t /tmp/discover_correlation_*.json 2>/dev/null | head -1)
    if [[ -n "$DISCOVERY_FILE" ]]; then
        TICKETS=$(jq -r '.final_unified_priorities[].ticket' "$DISCOVERY_FILE" | head -5 | tr '\n' '-' | sed 's/-$//')
    else
        TICKETS="unknown"
    fi
    
    CURRENT_JOB="tickets-${TICKETS}-${TIMESTAMP}.inprogress"
    echo "📋 Creating new job status file: $CURRENT_JOB"
    
    # Initialize job file with basic structure
    cat > "$CURRENT_JOB" << 'EOF'
{
  "job_id": "",
  "start_time": "",
  "tickets": [],
  "plan": {
    "phase_1_discovery": {"status": "pending"},
    "phase_2_scope": {"status": "pending"},
    "phase_3_implementation": {"status": "pending"}, 
    "phase_4_validation": {"status": "pending"},
    "phase_5_submission": {"status": "pending"},
    "phase_6_jira_update": {"status": "pending"}
  },
  "step_lessons": [],
  "interruption_recovery": {}
}
EOF
    
    # Update with actual job info
    TEMP_JOB=$(mktemp)
    jq --arg job_id "${CURRENT_JOB%.inprogress}" \
       --arg start_time "$(date -Iseconds)" \
       --argjson tickets "$(echo "$TICKETS" | tr '-' '\n' | jq -R . | jq -s .)" \
       '.job_id = $job_id | .start_time = $start_time | .tickets = $tickets' \
       "$CURRENT_JOB" > "$TEMP_JOB" && mv "$TEMP_JOB" "$CURRENT_JOB"
fi

echo "📊 Using job status file: $CURRENT_JOB"
```

### Step 2: Capture Immediate Step Lessons
```bash
# Capture lessons learned while details are fresh
echo "📝 Capturing lessons learned for step: $STEP_NAME"

# Create structured lessons object
STEP_TIMESTAMP=$(date -Iseconds)
LESSONS_DATA=$(cat << EOF
{
  "step": "$STEP_NAME",
  "timestamp": "$STEP_TIMESTAMP",
  "status": "$STATUS",
  "predicted_vs_actual": {},
  "unexpected_issues": [],
  "what_worked_well": [],
  "prompt_improvements_needed": [],
  "information_gaps": [],
  "time_analysis": {
    "predicted_duration": "",
    "actual_duration": "",
    "efficiency_factors": []
  },
  "tools_effectiveness": {
    "sequential_reasoning": "",
    "command_prompts": "",
    "error_handling": ""
  },
  "user_provided_lessons": "$LESSONS_TEXT"
}
EOF
)

# If this is a manual update, gather interactive lessons
if [[ "$INTERACTIVE" == "true" ]]; then
    echo "🤔 What was predicted vs what actually happened?"
    read -r PREDICTED_VS_ACTUAL
    
    echo "🚨 Any unexpected issues encountered?"
    read -r UNEXPECTED_ISSUES
    
    echo "✅ What worked better than expected?"
    read -r WORKED_WELL
    
    echo "🔧 What prompt improvements are needed?"
    read -r PROMPT_IMPROVEMENTS
    
    echo "❓ What information should have been gathered but wasn't?"
    read -r INFO_GAPS
    
    # Update lessons with interactive responses
    LESSONS_DATA=$(echo "$LESSONS_DATA" | jq \
        --arg pva "$PREDICTED_VS_ACTUAL" \
        --arg ui "$UNEXPECTED_ISSUES" \
        --arg ww "$WORKED_WELL" \
        --arg pi "$PROMPT_IMPROVEMENTS" \
        --arg ig "$INFO_GAPS" \
        '.predicted_vs_actual.summary = $pva |
         .unexpected_issues = [$ui] |
         .what_worked_well = [$ww] |
         .prompt_improvements_needed = [$pi] |
         .information_gaps = [$ig]')
fi
```

### Step 3: Update Job Status File
```bash
# Update job status with step completion and lessons
echo "📊 Updating job status file..."

TEMP_JOB=$(mktemp)

# Map step name to plan phase
case "$STEP_NAME" in
    "discover")
        PHASE_KEY="phase_1_discovery"
        ;;
    "scope")
        PHASE_KEY="phase_2_scope"
        ;;
    "implement")
        PHASE_KEY="phase_3_implementation"
        ;;
    "validate")
        PHASE_KEY="phase_4_validation"
        ;;
    "submit")
        PHASE_KEY="phase_5_submission"
        ;;
    "update-jira")
        PHASE_KEY="phase_6_jira_update"
        ;;
    *)
        echo "❌ Unknown step name: $STEP_NAME"
        exit 1
        ;;
esac

# Update the job status file
jq --arg phase "$PHASE_KEY" \
   --arg status "$STATUS" \
   --arg timestamp "$STEP_TIMESTAMP" \
   --arg results_file "$RESULTS_FILE" \
   --argjson lessons "$LESSONS_DATA" \
   --arg current_ticket "$CURRENT_TICKET" \
   --arg completed_tickets "$COMPLETED_TICKETS" \
   --arg recovery_notes "$RECOVERY_NOTES" \
   "
   .plan[\$phase].status = \$status |
   .plan[\$phase].timestamp = \$timestamp |
   (if \$results_file != \"\" then .plan[\$phase].results_file = \$results_file else . end) |
   (if \$current_ticket != \"\" then .plan[\$phase].current_ticket = \$current_ticket else . end) |
   (if \$completed_tickets != \"\" then .plan[\$phase].completed_tickets = (\$completed_tickets | split(\",\")) else . end) |
   .step_lessons += [\$lessons] |
   (if \$recovery_notes != \"\" then .interruption_recovery.notes = \$recovery_notes else . end) |
   .interruption_recovery.last_checkpoint = \$phase |
   .interruption_recovery.last_update = \$timestamp
   " \
   "$CURRENT_JOB" > "$TEMP_JOB" && mv "$TEMP_JOB" "$CURRENT_JOB"

echo "✅ Job status updated: $PHASE_KEY = $STATUS"
```

### Step 4: Display Current Progress
```bash
# Show current job progress
echo ""
echo "📋 CURRENT JOB PROGRESS"
echo "======================="

JOB_ID=$(jq -r '.job_id' "$CURRENT_JOB")
START_TIME=$(jq -r '.start_time' "$CURRENT_JOB")
TICKETS=$(jq -r '.tickets | join(", ")' "$CURRENT_JOB")

echo "Job ID: $JOB_ID"
echo "Started: $START_TIME"
echo "Tickets: $TICKETS"
echo ""

# Show phase status
echo "Phase Status:"
jq -r '.plan | to_entries[] | "\(.key): \(.value.status)"' "$CURRENT_JOB" | \
    sed 's/phase_[0-9]_//g' | \
    sed 's/^/  /'

# Show lessons learned count
LESSONS_COUNT=$(jq '.step_lessons | length' "$CURRENT_JOB")
echo ""
echo "Lessons Captured: $LESSONS_COUNT steps"

# Show last checkpoint for recovery
LAST_CHECKPOINT=$(jq -r '.interruption_recovery.last_checkpoint // "none"' "$CURRENT_JOB")
echo "Last Checkpoint: $LAST_CHECKPOINT"
```

### Step 5: Check for Job Completion
```bash
# Check if all phases are complete
INCOMPLETE_PHASES=$(jq -r '.plan | to_entries[] | select(.value.status != "completed" and .value.status != "skipped") | .key' "$CURRENT_JOB")

if [[ -z "$INCOMPLETE_PHASES" ]]; then
    echo ""
    echo "🎉 ALL PHASES COMPLETE!"
    echo "Moving job file to .finished status..."
    
    # Move to finished status
    FINISHED_FILE="${CURRENT_JOB%.inprogress}.finished"
    mv "$CURRENT_JOB" "$FINISHED_FILE"
    
    echo "✅ Job completed: $FINISHED_FILE"
    
    # Trigger final retrospective analysis
    echo "🔄 Triggering final retrospective analysis..."
    retrospective_analysis "$FINISHED_FILE"
else
    echo ""
    echo "⏳ Remaining phases:"
    echo "$INCOMPLETE_PHASES" | sed 's/phase_[0-9]_//g' | sed 's/^/  - /'
    
    # Update recovery information
    NEXT_PHASE=$(echo "$INCOMPLETE_PHASES" | head -1)
    TEMP_JOB=$(mktemp)
    jq --arg next_phase "$NEXT_PHASE" \
       '.interruption_recovery.next_phase = $next_phase' \
       "$CURRENT_JOB" > "$TEMP_JOB" && mv "$TEMP_JOB" "$CURRENT_JOB"
fi
```

### Step 6: Generate Recovery Instructions (if interrupted)
```bash
# Generate recovery instructions for potential interruption
RECOVERY_CMD=""
case "$LAST_CHECKPOINT" in
    "phase_1_discovery")
        if [[ "$STATUS" == "completed" ]]; then
            RECOVERY_CMD="/implement $(jq -r '.tickets | join(",")' "$CURRENT_JOB")"
        else
            RECOVERY_CMD="/discover"
        fi
        ;;
    "phase_3_implementation")
        if [[ -n "$CURRENT_TICKET" ]]; then
            REMAINING_TICKETS=$(jq -r '.tickets[] | select(. != "'$CURRENT_TICKET'")' "$CURRENT_JOB" | tr '\n' ',' | sed 's/,$//')
            RECOVERY_CMD="/implement $REMAINING_TICKETS --continue-from $CURRENT_TICKET"
        fi
        ;;
    "phase_4_validation")
        RECOVERY_CMD="/validate"
        ;;
    "phase_5_submission")
        RECOVERY_CMD="/submit"
        ;;
    "phase_6_jira_update")
        RECOVERY_CMD="/update-jira"
        ;;
esac

if [[ -n "$RECOVERY_CMD" ]]; then
    TEMP_JOB=$(mktemp)
    jq --arg recovery_cmd "$RECOVERY_CMD" \
       '.interruption_recovery.resume_command = $recovery_cmd' \
       "$CURRENT_JOB" > "$TEMP_JOB" && mv "$TEMP_JOB" "$CURRENT_JOB"
    
    echo ""
    echo "🔄 Recovery Command: $RECOVERY_CMD"
fi
```

## Final Retrospective Analysis Function

```bash
retrospective_analysis() {
    local FINISHED_FILE="$1"
    
    echo "🧠 RETROSPECTIVE ANALYSIS"
    echo "========================="
    
    # Extract all step lessons for synthesis
    ALL_LESSONS=$(jq '.step_lessons' "$FINISHED_FILE")
    
    # Use sequential reasoning to synthesize lessons across all steps
    echo "📊 Synthesizing lessons across all steps..."
    
    # Sequential Reasoning Prompt:
    # "Analyze all step lessons to identify:
    # 1. Cross-step patterns (same issue in multiple steps)
    # 2. Cascade effects (step A problem caused step B issue)
    # 3. Workflow optimization opportunities
    # 4. Systemic vs individual command improvements
    # 5. Success patterns to reinforce
    # 6. Specific prompt updates needed for each command"
    
    # Generate specific prompt improvements
    echo "🔧 Generating command prompt improvements..."
    
    # Update command_improvements_log.md with retrospective findings
    echo "## $(date '+%Y-%m-%d %H:%M:%S') - Retrospective Analysis from $(basename "$FINISHED_FILE")" >> history/command_improvements_log.md
    echo "### Cross-Step Pattern Analysis" >> history/command_improvements_log.md
    echo "### Cascade Effect Analysis" >> history/command_improvements_log.md  
    echo "### Workflow Optimizations Identified" >> history/command_improvements_log.md
    echo "### Command-Specific Prompt Updates" >> history/command_improvements_log.md
    echo "" >> history/command_improvements_log.md
    
    echo "✅ Retrospective analysis complete and logged"
}
```

## Success Criteria
- Job status file maintains accurate progress tracking
- Each step's lessons captured immediately while details are fresh
- Recovery information always up-to-date for interruption handling
- Final retrospective synthesizes patterns across all steps
- Specific prompt improvements generated for each command
- Complete audit trail from start to finish

## Error Handling
- Handle missing job files gracefully
- Validate step names and status values
- Backup job file before updates
- Recover from corrupted JSON files
- Preserve lessons even if status update fails

This centralized approach ensures consistent tracking and learning capture throughout the entire workflow.