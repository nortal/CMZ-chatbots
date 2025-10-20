# /nextfive Command (Main Orchestrator)

## Purpose
Complete AI-first development workflow with comprehensive project health assessment, built-in planning, execution, and self-improving learning system.

## Execution Flow

### PHASE 0: SESSION RECOVERY CHECK

#### Check for Interrupted Sessions
```bash
# Check for existing .inprogress files at startup
EXISTING_JOBS=(*.inprogress)
if [[ -e "${EXISTING_JOBS[0]}" ]]; then
    echo "📋 FOUND INTERRUPTED SESSION(S)"
    echo "==============================="
    
    for job_file in "${EXISTING_JOBS[@]}"; do
        if [[ -f "$job_file" ]]; then
            JOB_ID=$(jq -r '.job_id' "$job_file")
            START_TIME=$(jq -r '.start_time' "$job_file")
            LAST_CHECKPOINT=$(jq -r '.interruption_recovery.last_checkpoint // "unknown"' "$job_file")
            TICKETS=$(jq -r '.tickets | join(", ")' "$job_file")
            
            echo "Job: $JOB_ID"
            echo "Started: $START_TIME"
            echo "Tickets: $TICKETS"
            echo "Last checkpoint: $LAST_CHECKPOINT"
            echo ""
        fi
    done
    
    echo "Options:"
    echo "1) Resume most recent interrupted session"
    echo "2) Start fresh session (archive existing)"
    echo "3) Review detailed job status"
    echo "4) Exit and handle manually"
    echo ""
    read -p "Choose option (1-4): " RECOVERY_CHOICE
    
    case "$RECOVERY_CHOICE" in
        1)
            # Resume most recent session
            MOST_RECENT=$(ls -t *.inprogress | head -1)
            echo "📋 Resuming session: $MOST_RECENT"
            
            # Load recovery information
            RESUME_COMMAND=$(jq -r '.interruption_recovery.resume_command // ""' "$MOST_RECENT")
            LAST_CHECKPOINT=$(jq -r '.interruption_recovery.last_checkpoint // "unknown"' "$MOST_RECENT")
            
            echo "🔄 Last checkpoint: $LAST_CHECKPOINT"
            if [[ -n "$RESUME_COMMAND" && "$RESUME_COMMAND" != "" ]]; then
                echo "🚀 Executing recovery command: $RESUME_COMMAND"
                eval "$RESUME_COMMAND"
                exit 0
            else
                echo "⚠️ No specific recovery command found. Continuing with full workflow..."
                # Continue with normal execution but using existing job file
            fi
            ;;
        2)
            # Archive existing jobs and start fresh
            ARCHIVE_DIR="jobs_archive_$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$ARCHIVE_DIR"
            mv *.inprogress "$ARCHIVE_DIR/" 2>/dev/null
            echo "✅ Archived existing jobs to $ARCHIVE_DIR"
            echo "🆕 Starting fresh session..."
            ;;
        3)
            # Review detailed status
            echo "📊 DETAILED JOB STATUS"
            echo "======================"
            for job_file in "${EXISTING_JOBS[@]}"; do
                if [[ -f "$job_file" ]]; then
                    echo ""
                    echo "Job: $(jq -r '.job_id' "$job_file")"
                    echo "Phase Status:"
                    jq -r '.plan | to_entries[] | "  \(.key | sub("phase_[0-9]_"; "")): \(.value.status)"' "$job_file"
                    echo "Lessons Captured: $(jq '.step_lessons | length' "$job_file") steps"
                fi
            done
            echo ""
            echo "Re-run /nextfive to choose recovery option."
            exit 0
            ;;
        4)
            echo "👋 Exiting for manual handling"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi
```

### PHASE 0.5: PROJECT HEALTH ASSESSMENT (AI-First Analysis)

#### Step 0.1: Comprehensive Project Analysis
```bash
echo ""
echo "🏗️ PHASE 0.5: PROJECT HEALTH ASSESSMENT"
echo "======================================="

# Mark project health assessment as starting
update_nextfive_progress health_assessment in_progress \
  --lessons "Beginning comprehensive project health assessment with AI-first approach"

echo "🔍 Running comprehensive codebase analysis..."
HEALTH_START=$(date +%s)

# Architecture Analysis
echo "  📐 Analyzing system architecture patterns..."
ARCHITECTURE_ANALYSIS_START=$(date +%s)
/analyze-architecture
ARCHITECTURE_ANALYSIS_END=$(date +%s)
ARCHITECTURE_TIME=$((ARCHITECTURE_ANALYSIS_END - ARCHITECTURE_ANALYSIS_START))

# Technical Debt Assessment  
echo "  🔧 Measuring technical debt and code quality..."
TECH_DEBT_START=$(date +%s)
/measure-technical-debt
TECH_DEBT_END=$(date +%s)
TECH_DEBT_TIME=$((TECH_DEBT_END - TECH_DEBT_START))

# Security Posture Assessment
echo "  🛡️ Assessing security posture..."
SECURITY_START=$(date +%s)
/assess-security-posture
SECURITY_END=$(date +%s)
SECURITY_TIME=$((SECURITY_END - SECURITY_START))

HEALTH_END=$(date +%s)
HEALTH_TOTAL_TIME=$((HEALTH_END - HEALTH_START))

# Load health assessment results
HEALTH_FILE=$(ls -t /tmp/project_health_*.json 2>/dev/null | head -1)
if [[ -n "$HEALTH_FILE" ]]; then
    ARCHITECTURE_SCORE=$(jq -r '.architecture_analysis.compliance_score // "unknown"' "$HEALTH_FILE")
    TECH_DEBT_LEVEL=$(jq -r '.technical_debt.overall_level // "unknown"' "$HEALTH_FILE")
    SECURITY_RATING=$(jq -r '.security_assessment.overall_rating // "unknown"' "$HEALTH_FILE")
    
    HEALTH_LESSONS="Project health assessment took ${HEALTH_TOTAL_TIME}s. "
    HEALTH_LESSONS+="Architecture compliance: $ARCHITECTURE_SCORE. "
    HEALTH_LESSONS+="Technical debt level: $TECH_DEBT_LEVEL. "
    HEALTH_LESSONS+="Security rating: $SECURITY_RATING. "
    
    # Set quality gates based on health assessment
    if [[ "$ARCHITECTURE_SCORE" != "unknown" ]] && (( $(echo "$ARCHITECTURE_SCORE < 0.8" | bc -l) )); then
        HEALTH_LESSONS+="⚠️ Architecture compliance below threshold - enhanced validation required. "
    fi
    
    if [[ "$TECH_DEBT_LEVEL" == "high" ]]; then
        HEALTH_LESSONS+="⚠️ High technical debt detected - refactoring opportunities identified. "
    fi
    
    update_nextfive_progress health_assessment completed \
      --results-file "$HEALTH_FILE" \
      --lessons "$HEALTH_LESSONS Project ready for comprehensive AI-first development approach."
else
    update_nextfive_progress health_assessment completed \
      --lessons "Health assessment completed but no consolidated results file generated. Individual analyses successful."
fi

echo "✅ Project health assessment complete"
echo "    📐 Architecture analysis: ${ARCHITECTURE_TIME}s"
echo "    🔧 Technical debt assessment: ${TECH_DEBT_TIME}s" 
echo "    🛡️ Security assessment: ${SECURITY_TIME}s"
echo "    📊 Overall health score available for downstream phases"
```

### PHASE 1: BUILT-IN PLANNING (AI-Enhanced Pre-execution Analysis)

#### Step 1: Load Previous Learning and Read Command Prompts
```bash
# Load any previous lessons learned from command improvement log
if [[ -f "history/command_improvements_log.md" ]]; then
    echo "📚 Loading previous lessons learned..."
    PREVIOUS_LESSONS=$(cat history/command_improvements_log.md)
    echo "Found $(grep -c "## 20" history/command_improvements_log.md) previous sessions with lessons"
else
    echo "📝 No previous lessons found - creating new improvement log"
    touch history/command_improvements_log.md
    PREVIOUS_LESSONS=""
fi

# Read actual command prompt templates
echo "🔍 Reading command prompt templates for prediction..."
DISCOVER_TESTS_PROMPT=$(cat scripts/commands/discover-tests.md)
DISCOVER_JIRA_PROMPT=$(cat scripts/commands/discover-jira.md) 
DISCOVER_PROMPT=$(cat scripts/commands/discover.md)
SCOPE_PROMPT=$(cat scripts/commands/scope.md)
IMPLEMENT_PROMPT=$(cat scripts/commands/implement.md)
VALIDATE_PROMPT=$(cat scripts/commands/validate.md)
SUBMIT_PROMPT=$(cat scripts/commands/submit.md)
UPDATE_JIRA_PROMPT=$(cat scripts/commands/update-jira.md)

echo "✅ All command prompts loaded for analysis"
```

#### Step 2: Sequential Reasoning Workflow Prediction

Use sequential reasoning MCP to simulate the entire workflow:

**Workflow Prediction Prompt:**
```
Based on actual command prompts and previous lessons, predict the complete /nextfive workflow execution:

**ACTUAL COMMAND PROMPTS:**
- discover-tests: {discover_tests_prompt}
- discover-jira: {discover_jira_prompt}  
- discover: {discover_prompt}
- scope: {scope_prompt}
- implement: {implement_prompt}
- validate: {validate_prompt}
- submit: {submit_prompt}
- update-jira: {update_jira_prompt}

**PREVIOUS LESSONS LEARNED:**
{previous_lessons}

**CURRENT PROJECT STATE:**
- Git branch: {current_branch}
- Container status: {docker_status}
- System health: {system_health}
- Last integration test results: {recent_test_status}

**PROJECT HEALTH ASSESSMENT:**
- Architecture compliance score: {architecture_score}
- Technical debt level: {tech_debt_level}
- Security rating: {security_rating}
- Quality gates status: {quality_gates_summary}

**COMPREHENSIVE WORKFLOW PREDICTION:**

1. **Enhanced Discovery Phase Prediction:**
   - How many failing tests will /discover-tests likely find?
   - What strategic priorities will /discover-jira identify?
   - How will /discover correlate technical vs strategic priorities with health assessment?
   - What architectural improvements will be identified from health assessment?
   - Will /scope expansion be needed or will we have 5+ tickets?
   - How will project health findings influence ticket prioritization?
   - Predicted total discovery time and potential issues?

2. **AI-First Implementation Phase Prediction:**
   - Which tickets will be most complex to implement?
   - What existing patterns can be leveraged for efficiency?
   - How will architectural compliance requirements affect implementation?
   - Where might implementation run into unexpected complexity?
   - What holistic impact analysis will reveal about system-wide effects?
   - Estimated time for each ticket based on prompt analysis and health assessment?
   - What dependency issues might arise during implementation?

3. **AI-Enhanced Validation Phase Prediction:**
   - Which implementations are most likely to have issues?
   - What integration test improvements can we expect?
   - How will GitHub pipeline quality gates (linting, SAST) perform?
   - Which error scenarios might not be properly handled?
   - What architectural compliance violations might be detected?
   - How will code quality metrics compare to baseline from health assessment?
   - How reliable will the validation testing be?

4. **Submission Phase Prediction:**
   - What aspects of the MR will reviewers focus on?
   - What additional documentation might be needed?
   - How long will the review process likely take?
   - What changes might reviewers request?

5. **Jira Update Phase Prediction:**
   - Which tickets will update successfully vs have issues?
   - What common Jira API problems might occur?
   - How reliable will the update script execution be?

6. **Overall Workflow Prediction:**
   - Total estimated time for complete workflow?
   - Most likely failure points and bottlenecks?
   - Required resources and dependencies?
   - Success probability and risk factors?

**LEARNING FROM PREVIOUS SESSIONS:**
- What patterns from previous sessions apply to this prediction?
- Which previous lessons should influence the current approach?
- What prompt improvements could be applied immediately?

**PREDICTION CONFIDENCE AND VALIDATION:**
- Rate confidence level (1-10) for each phase prediction
- Identify predictions with highest uncertainty
- Define success metrics for validating predictions
- Plan checkpoint validations throughout execution
```

#### Step 3: Plan Validation and User Approval

```bash
echo "🎯 WORKFLOW PREDICTION COMPLETE"
echo "==============================="
echo ""
echo "Based on analysis of actual command prompts and previous lessons:"
echo ""

# Display prediction summary (from sequential reasoning results)
echo "📋 PREDICTED DISCOVERY:"
echo "  - Failing tests: X tickets (confidence: Y/10)"
echo "  - Strategic priorities: Z foundation + W feature tickets"
echo "  - Scope expansion needed: Yes/No"
echo ""

echo "🔨 PREDICTED IMPLEMENTATION:"
echo "  - Total estimated time: X-Y hours"
echo "  - Most complex ticket: TICKET_ID (reason)"
echo "  - Pattern reuse opportunities: Z patterns"
echo ""

echo "🧪 PREDICTED VALIDATION:"
echo "  - Expected test improvement: +X passing tests"
echo "  - Likely validation issues: Y areas"
echo "  - Performance expectations: acceptable/concerning"
echo ""

echo "📤 PREDICTED SUBMISSION:"
echo "  - Review focus areas: X, Y, Z"
echo "  - Estimated approval time: X days"
echo "  - Iteration likelihood: low/medium/high"
echo ""

echo "🎫 PREDICTED JIRA UPDATES:"
echo "  - Success likelihood: X% (based on previous sessions)"
echo "  - Potential issues: API connectivity/token expiration/etc."
echo ""

echo "⏱️  TOTAL PREDICTED TIME: X-Y hours"
echo "🎯 SUCCESS PROBABILITY: Z% (confidence level)"
echo ""

# Save prediction for comparison
PREDICTION_FILE="/tmp/nextfive_prediction_$(date +%Y%m%d_%H%M%S).json"
# Sequential reasoning results saved to prediction file

echo "💾 Prediction saved to: $PREDICTION_FILE"
echo ""
echo "Do you want to proceed with execution based on this prediction? (y/n)"
read -r PROCEED_CONFIRMATION

if [[ "$PROCEED_CONFIRMATION" != "y" ]]; then
    echo "❌ Execution cancelled by user"
    echo "💡 Use individual commands for targeted execution: /discover, /implement [tickets], etc."
    exit 0
fi

echo "✅ User approved - proceeding with predicted workflow"
EXECUTION_START_TIME=$(date +%s)
```

### PHASE 2: SYSTEMATIC EXECUTION WITH TRACKING

#### Step 4: Execute Enhanced Discovery Phase with Holistic Impact Analysis
```bash
echo ""
echo "🔍 PHASE 1: ENHANCED DISCOVERY WITH ARCHITECTURE AWARENESS"
echo "========================================================="

# Mark discovery as starting
update_nextfive_progress discover in_progress \
  --lessons "Beginning enhanced discovery phase with architectural awareness and health assessment integration"

# Execute discovery with result tracking
echo "📊 Running /discover-tests..."
DISCOVER_TESTS_START=$(date +%s)
/discover-tests
DISCOVER_TESTS_END=$(date +%s)
DISCOVER_TESTS_TIME=$((DISCOVER_TESTS_END - DISCOVER_TESTS_START))

echo "📋 Running /discover-jira..."
DISCOVER_JIRA_START=$(date +%s)
/discover-jira
DISCOVER_JIRA_END=$(date +%s)
DISCOVER_JIRA_TIME=$((DISCOVER_JIRA_END - DISCOVER_JIRA_START))

echo "🔗 Running /discover correlation with health assessment integration..."
DISCOVER_CORRELATION_START=$(date +%s)
/discover
DISCOVER_CORRELATION_END=$(date +%s)
DISCOVER_CORRELATION_TIME=$((DISCOVER_CORRELATION_START - DISCOVER_CORRELATION_END))

# NEW: Holistic Impact Analysis
echo "🕸️ Running holistic impact analysis..."
IMPACT_ANALYSIS_START=$(date +%s)
/analyze-holistic-impact
IMPACT_ANALYSIS_END=$(date +%s)
IMPACT_ANALYSIS_TIME=$((IMPACT_ANALYSIS_END - IMPACT_ANALYSIS_START))

# Load actual discovery results
DISCOVERY_FILE=$(ls -t /tmp/discover_correlation_*.json 2>/dev/null | head -1)
IMPACT_FILE=$(ls -t /tmp/holistic_impact_*.json 2>/dev/null | head -1)

if [[ -z "$DISCOVERY_FILE" ]]; then
    echo "❌ Discovery phase failed - no results generated"
    update_nextfive_progress discover failed \
      --lessons "Discovery phase failed to generate correlation results" \
      --recovery-notes "Check individual discover sub-commands for specific failures"
    exit 1
fi

ACTUAL_TICKETS=$(jq -r '.final_unified_priorities | length' "$DISCOVERY_FILE")
echo "✅ Discovery complete: $ACTUAL_TICKETS tickets identified"

# Load holistic impact analysis results
if [[ -n "$IMPACT_FILE" ]]; then
    ARCHITECTURE_IMPACT=$(jq -r '.architecture_impact.severity // "low"' "$IMPACT_FILE")
    CROSS_SERVICE_EFFECTS=$(jq -r '.cross_service_effects | length' "$IMPACT_FILE")
    INTEGRATION_SCOPE=$(jq -r '.integration_testing_scope.estimated_tests // 0' "$IMPACT_FILE")
    
    echo "🕸️ Holistic impact analysis complete:"
    echo "    📐 Architecture impact: $ARCHITECTURE_IMPACT severity"
    echo "    🔗 Cross-service effects: $CROSS_SERVICE_EFFECTS components"
    echo "    🧪 Integration test scope: $INTEGRATION_SCOPE additional tests"
fi

# Capture comprehensive discovery lessons
TOTAL_DISCOVERY_TIME=$((DISCOVER_CORRELATION_END - DISCOVER_TESTS_START + IMPACT_ANALYSIS_TIME))
DISCOVERY_LESSONS="Enhanced discovery took ${TOTAL_DISCOVERY_TIME}s total (including ${IMPACT_ANALYSIS_TIME}s impact analysis). "
DISCOVERY_LESSONS+="Found $ACTUAL_TICKETS tickets vs predicted X. "
if [[ -n "$IMPACT_FILE" ]]; then
    DISCOVERY_LESSONS+="Holistic impact: $ARCHITECTURE_IMPACT severity, $CROSS_SERVICE_EFFECTS components affected. "
fi

# Check if scope expansion needed
if [[ "$ACTUAL_TICKETS" -lt 5 ]]; then
    echo "📈 Running /scope expansion..."
    update_nextfive_progress scope in_progress \
      --lessons "Scope expansion needed - only $ACTUAL_TICKETS tickets found"
    
    SCOPE_START=$(date +%s)
    /scope
    SCOPE_END=$(date +%s)
    SCOPE_TIME=$((SCOPE_END - SCOPE_START))
    
    update_nextfive_progress scope completed \
      --lessons "Scope expansion took ${SCOPE_TIME}s. Expanded to 5 tickets total."
    echo "✅ Scope expansion complete"
else
    echo "✅ Sufficient tickets found - skipping scope expansion"
    update_nextfive_progress scope skipped \
      --lessons "Scope expansion not needed - $ACTUAL_TICKETS tickets sufficient"
    SCOPE_TIME=0
fi

# Mark discovery phase complete with comprehensive lessons
update_nextfive_progress discover completed \
  --results-file "$DISCOVERY_FILE" \
  --lessons "$DISCOVERY_LESSONS Strategic correlation successful. Ready for implementation."
```

#### Step 5: Execute Implementation Phase
```bash
echo ""
echo "🔨 PHASE 2: IMPLEMENTATION"  
echo "=========================="

# Extract ticket list from discovery results
TICKET_LIST=$(jq -r '.final_unified_priorities[].ticket' "$DISCOVERY_FILE" | tr '\n' ',' | sed 's/,$//')
echo "Implementing tickets: $TICKET_LIST"

# Mark implementation as starting
update_nextfive_progress implement in_progress \
  --lessons "Starting implementation of $TICKET_LIST. Predicted time: X hours based on sequential reasoning analysis."

IMPLEMENT_START=$(date +%s)
echo "🚀 Running /implement..."

/implement "$TICKET_LIST"

IMPLEMENT_END=$(date +%s)
IMPLEMENT_TIME=$((IMPLEMENT_END - IMPLEMENT_START))

# Load implementation results for lessons
IMPLEMENT_FILE=$(ls -t /tmp/implement_*.json 2>/dev/null | head -1)
if [[ -n "$IMPLEMENT_FILE" ]]; then
    IMPLEMENTED_COUNT=$(jq -r '.implementation_summary.tickets_completed | length' "$IMPLEMENT_FILE" 2>/dev/null || echo "0")
    ACTUAL_TIME_HOURS=$(echo "scale=1; $IMPLEMENT_TIME / 3600" | bc)
    
    IMPLEMENTATION_LESSONS="Implementation took ${ACTUAL_TIME_HOURS}h total vs predicted Xh. Completed $IMPLEMENTED_COUNT tickets. "
    
    # Check for specific implementation insights
    if [[ "$IMPLEMENT_TIME" -gt 7200 ]]; then  # > 2 hours
        IMPLEMENTATION_LESSONS+="Longer than expected - likely due to pattern establishment complexity. "
    fi
    
    update_nextfive_progress implement completed \
      --results-file "$IMPLEMENT_FILE" \
      --lessons "$IMPLEMENTATION_LESSONS Ready for validation phase."
else
    update_nextfive_progress implement failed \
      --lessons "Implementation completed but no results file generated. May indicate execution issues." \
      --recovery-notes "Check implementation logs and verify all tickets were processed"
fi

echo "✅ Implementation phase complete"
```

#### Step 6: Execute AI-Enhanced Validation Phase with GitHub Pipeline Integration
```bash
echo ""
echo "🧪 PHASE 3: AI-ENHANCED VALIDATION WITH GITHUB QUALITY GATES"
echo "==========================================================="

# Mark validation as starting
update_nextfive_progress validate in_progress \
  --lessons "Starting AI-enhanced validation phase with GitHub pipeline quality gates integration. Predicted outcome: X passing tests, GitHub pipeline validation."

echo "🛡️ GitHub Pipeline Quality Gates Integration:"
echo "  ✅ Leveraging existing linting rules"
echo "  ✅ Using configured SAST security scanning"
echo "  ✅ Code quality metrics from pipeline"
echo "  📊 Architecture compliance verification"
echo ""

VALIDATE_START=$(date +%s)

# Enhanced validation with quality gates
echo "🔍 Running enhanced /validate with pipeline integration..."
/validate

# Additional AI-first validation steps
echo "📐 Running architecture compliance validation..."
ARCH_VALIDATION_START=$(date +%s)
/validate-architecture-compliance
ARCH_VALIDATION_END=$(date +%s)
ARCH_VALIDATION_TIME=$((ARCH_VALIDATION_END - ARCH_VALIDATION_START))

echo "🔧 Running code quality gate validation..."
QUALITY_VALIDATION_START=$(date +%s)
/validate-code-quality-gates
QUALITY_VALIDATION_END=$(date +%s)
QUALITY_VALIDATION_TIME=$((QUALITY_VALIDATION_END - QUALITY_VALIDATION_START))

VALIDATE_END=$(date +%s)
VALIDATE_TIME=$((VALIDATE_END - VALIDATE_START))

# Check enhanced validation results and capture comprehensive lessons
VALIDATION_FILE=$(ls -t /tmp/validate_*.json 2>/dev/null | head -1)
ARCH_VALIDATION_FILE=$(ls -t /tmp/validate_architecture_*.json 2>/dev/null | head -1)
QUALITY_GATES_FILE=$(ls -t /tmp/validate_quality_gates_*.json 2>/dev/null | head -1)

if [[ -n "$VALIDATION_FILE" ]]; then
    VALIDATION_STATUS=$(jq -r '.validation_summary.overall_status // "unknown"' "$VALIDATION_FILE")
    PASSING_TESTS=$(jq -r '.integration_tests.after_implementation.passing // 0' "$VALIDATION_FILE")
    FAILING_TESTS=$(jq -r '.integration_tests.after_implementation.failing // 0' "$VALIDATION_FILE")
    
    VALIDATION_LESSONS="AI-enhanced validation took ${VALIDATE_TIME}s total. Status: $VALIDATION_STATUS. "
    VALIDATION_LESSONS+="Integration tests: $PASSING_TESTS passing, $FAILING_TESTS failing. "
    
    # Architecture compliance results
    if [[ -n "$ARCH_VALIDATION_FILE" ]]; then
        ARCH_COMPLIANCE=$(jq -r '.architecture_compliance.score // "unknown"' "$ARCH_VALIDATION_FILE")
        ARCH_VIOLATIONS=$(jq -r '.architecture_compliance.violations | length' "$ARCH_VALIDATION_FILE")
        VALIDATION_LESSONS+="Architecture compliance: $ARCH_COMPLIANCE score, $ARCH_VIOLATIONS violations. "
        
        echo "📐 Architecture validation: ${ARCH_VALIDATION_TIME}s"
        echo "    Score: $ARCH_COMPLIANCE, Violations: $ARCH_VIOLATIONS"
    fi
    
    # Quality gates results
    if [[ -n "$QUALITY_GATES_FILE" ]]; then
        QUALITY_SCORE=$(jq -r '.quality_gates.overall_score // "unknown"' "$QUALITY_GATES_FILE")
        LINT_STATUS=$(jq -r '.quality_gates.linting.status // "unknown"' "$QUALITY_GATES_FILE")
        SAST_STATUS=$(jq -r '.quality_gates.sast_scan.status // "unknown"' "$QUALITY_GATES_FILE")
        VALIDATION_LESSONS+="Quality gates: $QUALITY_SCORE score, linting: $LINT_STATUS, SAST: $SAST_STATUS. "
        
        echo "🔧 Quality gates validation: ${QUALITY_VALIDATION_TIME}s"
        echo "    Overall: $QUALITY_SCORE, Linting: $LINT_STATUS, SAST: $SAST_STATUS"
    fi
    
    # Overall assessment
    if [[ "$VALIDATION_STATUS" == "successful" ]] && [[ "$ARCH_COMPLIANCE" != "low" ]] && [[ "$QUALITY_SCORE" != "failing" ]]; then
        VALIDATION_LESSONS+="All AI-enhanced validations passed - ready for submission with high confidence."
        update_nextfive_progress validate completed \
          --results-file "$VALIDATION_FILE" \
          --lessons "$VALIDATION_LESSONS"
    else
        VALIDATION_LESSONS+="Some validation issues detected - review required before submission."
        update_nextfive_progress validate completed \
          --results-file "$VALIDATION_FILE" \
          --lessons "$VALIDATION_LESSONS" \
          --recovery-notes "Review validation issues: tests ($VALIDATION_STATUS), architecture ($ARCH_COMPLIANCE), quality gates ($QUALITY_SCORE)"
    fi
else
    update_nextfive_progress validate failed \
      --lessons "AI-enhanced validation phase failed to generate results file" \
      --recovery-notes "Check validation execution logs and system health"
fi

echo "✅ AI-enhanced validation complete: $VALIDATION_STATUS"
echo "    🧪 Integration tests: $PASSING_TESTS passing, $FAILING_TESTS failing"
if [[ -n "$ARCH_COMPLIANCE" ]]; then
    echo "    📐 Architecture compliance: $ARCH_COMPLIANCE"
fi
if [[ -n "$QUALITY_SCORE" ]]; then
    echo "    🛡️ Quality gates: $QUALITY_SCORE"
fi
```

#### Step 7: Execute Submission Phase
```bash
echo ""
echo "📤 PHASE 4: SUBMISSION"
echo "======================"

# Mark submission as starting
update_nextfive_progress submit in_progress \
  --lessons "Starting submission phase. Predicted MR review time: X days, iteration likelihood: Y%."

SUBMIT_START=$(date +%s)
echo "🚀 Running /submit..."
/submit
SUBMIT_END=$(date +%s)
SUBMIT_TIME=$((SUBMIT_END - SUBMIT_START))

# Capture submission lessons
SUBMIT_MINUTES=$(echo "scale=1; $SUBMIT_TIME / 60" | bc)
SUBMISSION_LESSONS="Submission took ${SUBMIT_MINUTES}m vs predicted Xm. "

# Try to extract MR URL from recent git commits or submission output
MR_URL=$(git log --oneline -1 --grep="Generated with" | grep -o 'https://[^ ]*' | head -1 || echo "MR_URL_not_found")
if [[ "$MR_URL" != "MR_URL_not_found" ]]; then
    SUBMISSION_LESSONS+="MR created: $MR_URL. "
else
    SUBMISSION_LESSONS+="MR creation may have had issues - no URL detected. "
fi

update_nextfive_progress submit completed \
  --lessons "$SUBMISSION_LESSONS Ready for Jira updates."

echo "✅ Submission phase complete"
```

#### Step 8: Execute Jira Update Phase with Mandatory Verification
```bash
echo ""
echo "🎫 PHASE 5: JIRA UPDATES WITH MR-TICKET ALIGNMENT VERIFICATION"
echo "=============================================================="

# Mark Jira update as starting with verification emphasis
update_nextfive_progress update-jira in_progress \
  --lessons "Starting Jira updates with MANDATORY MR-ticket alignment verification. New safety protocols active to prevent wrong ticket updates."

echo "⚠️  CRITICAL: Enhanced Jira Update Process Active"
echo "==============================================="
echo ""
echo "🛡️  NEW SAFETY FEATURES:"
echo "  ✅ Mandatory MR-ticket alignment verification"
echo "  ✅ AI-powered Sequential Reasoning validation"
echo "  ✅ Confidence scoring (minimum 4/5 required)"
echo "  ✅ Final confirmation gates before updates"
echo "  ✅ Enhanced lessons learned capture"
echo ""
echo "🚨 This process will STOP if misalignment is detected."
echo "   All verifications must pass to proceed with ticket updates."
echo ""

UPDATE_JIRA_START=$(date +%s)
echo "📝 Running enhanced /update-jira with verification..."
/update-jira  
UPDATE_JIRA_END=$(date +%s)
UPDATE_JIRA_TIME=$((UPDATE_JIRA_END - UPDATE_JIRA_START))

# Capture enhanced Jira update lessons with verification analytics
UPDATE_MINUTES=$(echo "scale=1; $UPDATE_JIRA_TIME / 60" | bc)
JIRA_LESSONS="Enhanced Jira updates took ${UPDATE_MINUTES}m vs predicted Xm. "

# Check if NORTAL-JIRA-ADVICE.md was updated (indicates success/failure patterns)
if [[ -f "NORTAL-JIRA-ADVICE.md" ]]; then
    RECENT_ENTRIES=$(tail -10 NORTAL-JIRA-ADVICE.md | grep -c "$(date '+%Y-%m-%d')" || echo "0")
    JIRA_LESSONS+="Added $RECENT_ENTRIES entries to JIRA advice log. "
    
    # Enhanced verification pattern analysis
    VERIFICATION_SUCCESS=$(tail -50 NORTAL-JIRA-ADVICE.md | grep -c "AI Validation Successful\|Verification complete" || echo "0")
    VERIFICATION_FAILURES=$(tail -50 NORTAL-JIRA-ADVICE.md | grep -c "AI Validation Failed\|REVIEW_REQUIRED" || echo "0")
    MR_ALIGNMENT_ISSUES=$(tail -50 NORTAL-JIRA-ADVICE.md | grep -c "misalignment\|wrong tickets" || echo "0")
    
    JIRA_LESSONS+="Verification analytics: $VERIFICATION_SUCCESS successful validations, $VERIFICATION_FAILURES validation failures, $MR_ALIGNMENT_ISSUES alignment issues detected. "
    
    # Check for overall success patterns including new verification steps
    if tail -20 NORTAL-JIRA-ADVICE.md | grep -q "SUCCESS\|Successful.*Connectivity\|AI Validation Successful"; then
        JIRA_LESSONS+="Jira operations completed successfully with enhanced verification protocols."
        
        # Capture specific verification insights
        if tail -20 NORTAL-JIRA-ADVICE.md | grep -q "AI Validation Successful"; then
            JIRA_LESSONS+=" Sequential Reasoning MCP successfully validated MR-ticket alignment."
        fi
        
        if tail -20 NORTAL-JIRA-ADVICE.md | grep -q "Verification complete"; then
            JIRA_LESSONS+=" Manual verification gates passed with high confidence."
        fi
    else
        JIRA_LESSONS+="Potential Jira issues detected - check NORTAL-JIRA-ADVICE.md for verification failures or alignment problems."
        
        # Capture specific failure patterns for learning
        if tail -20 NORTAL-JIRA-ADVICE.md | grep -q "AI Validation Failed"; then
            JIRA_LESSONS+=" AI detected MR-ticket misalignment - verification protocols prevented wrong updates."
        fi
        
        if tail -20 NORTAL-JIRA-ADVICE.md | grep -q "CONFIDENCE TOO LOW"; then
            JIRA_LESSONS+=" User confidence insufficient - manual review required for safety."
        fi
    fi
    
    # Capture learning about verification effectiveness
    echo "## $(date '+%Y-%m-%d %H:%M:%S') - /nextfive Verification Protocol Analysis" >> NORTAL-JIRA-ADVICE.md
    echo "**Enhanced Jira Process**: MR-ticket verification protocols active" >> NORTAL-JIRA-ADVICE.md
    echo "**Session Duration**: ${UPDATE_MINUTES}m" >> NORTAL-JIRA-ADVICE.md
    echo "**Verification Success Rate**: $VERIFICATION_SUCCESS successes vs $VERIFICATION_FAILURES failures" >> NORTAL-JIRA-ADVICE.md
    echo "**Alignment Issues Detected**: $MR_ALIGNMENT_ISSUES (prevented wrong updates)" >> NORTAL-JIRA-ADVICE.md
    echo "**Protocol Effectiveness**: Enhanced safety measures $(if [[ $MR_ALIGNMENT_ISSUES -eq 0 ]]; then echo "working correctly"; else echo "detected and prevented $MR_ALIGNMENT_ISSUES potential errors"; fi)" >> NORTAL-JIRA-ADVICE.md
    echo "" >> NORTAL-JIRA-ADVICE.md
fi

update_nextfive_progress update-jira completed \
  --lessons "$JIRA_LESSONS All phases complete - ready for retrospective analysis."

echo "✅ Jira update phase complete"
```

### PHASE 3: LEARNING AND IMPROVEMENT

#### Step 9: Compare Predictions vs Actual Results

```bash
echo ""
echo "🧠 PHASE 6: LEARNING ANALYSIS"
echo "============================="

EXECUTION_END_TIME=$(date +%s)
TOTAL_EXECUTION_TIME=$((EXECUTION_END_TIME - EXECUTION_START_TIME))

echo "📊 Analyzing prediction accuracy..."

# Use sequential reasoning to compare predicted vs actual outcomes
# Sequential Reasoning Analysis Prompt:
```
Compare predicted workflow outcomes with actual execution results and identify lessons learned:

**ORIGINAL PREDICTIONS:**
{prediction_file_contents}

**ACTUAL EXECUTION RESULTS:**
- Discovery phase: {actual_discovery_results}
- Implementation phase: {actual_implementation_results}  
- Validation phase: {actual_validation_results}
- Submission phase: {actual_submission_results}
- Jira update phase: {actual_jira_results}

**TIMING COMPARISON:**
- Predicted total time: {predicted_time}
- Actual total time: {total_execution_time} seconds
- Phase-by-phase comparison: {phase_timing_analysis}

**ACCURACY ANALYSIS:**

1. **Discovery Phase Analysis:**
   - Predicted vs actual failing tests found?
   - Strategic priority prediction accuracy?
   - Scope expansion prediction correct?
   - What factors affected discovery accuracy?

2. **Implementation Phase Analysis:**
   - Time estimate accuracy for each ticket?
   - Complexity predictions vs reality?
   - Pattern reuse effectiveness vs expectations?
   - Unexpected issues encountered?

3. **Validation Phase Analysis:**
   - Test improvement predictions vs actual results?
   - Validation issue predictions vs discovered problems?
   - Performance expectations vs measured results?
   - Testing reliability as expected?

4. **Submission Phase Analysis:**
   - MR creation process vs predictions?
   - Reviewer focus areas correctly anticipated?
   - Documentation completeness vs expectations?

5. **Jira Update Phase Analysis:**
   - API connectivity issues as predicted?
   - Ticket update success rate vs expectations?
   - Script reliability vs historical patterns?

**LEARNING INSIGHTS:**

1. **Command Prompt Improvements:**
   - Which command prompts need updates for better predictions?
   - What additional information should be gathered?
   - Which analysis steps were missing or insufficient?

2. **Prediction Model Refinements:**
   - What factors were not considered in predictions?
   - Which prediction methods were most/least accurate?
   - How can confidence levels be better calibrated?

3. **Workflow Optimization:**
   - Which phases took longer than expected and why?
   - What bottlenecks or inefficiencies were discovered?
   - Where can parallel execution be improved?

4. **Success Pattern Recognition:**
   - What worked better than expected?
   - Which approaches should be reinforced?
   - What successful patterns can be codified?

**SPECIFIC PROMPT IMPROVEMENTS:**

For each command that had prediction mismatches:
- Exact changes needed in the command prompt
- Additional information gathering steps
- Better analysis frameworks or questions
- Improved prediction methodologies

**DELIVERABLE:**
- Detailed accuracy assessment with specific prediction vs reality comparisons
- Concrete prompt improvement recommendations with exact text changes
- Updated prediction model incorporating new insights
- Success pattern documentation for future reference
```

#### Step 10: Apply Command Improvements

```bash
echo "🔧 Applying lessons learned to command improvements..."

# Sequential reasoning will provide specific prompt updates
# Apply approved changes to command files
echo "Updating command prompts based on lessons learned..."

# Log improvements to the improvement log
SESSION_DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "" >> history/command_improvements_log.md
echo "## $SESSION_DATE - /nextfive Learning Session" >> history/command_improvements_log.md
echo "" >> history/command_improvements_log.md
echo "### Prediction vs Reality Analysis" >> history/command_improvements_log.md

# Add specific lessons learned (from sequential reasoning analysis)
echo "**Discovery Phase**: " >> history/command_improvements_log.md
echo "**Implementation Phase**: " >> history/command_improvements_log.md  
echo "**Validation Phase**: " >> history/command_improvements_log.md
echo "**Submission Phase**: " >> history/command_improvements_log.md
echo "**Jira Update Phase**: " >> history/command_improvements_log.md
echo "" >> history/command_improvements_log.md
echo "### Command Prompt Improvements Applied" >> history/command_improvements_log.md
# List specific changes made to command files
echo "" >> history/command_improvements_log.md
echo "### Success Patterns Identified" >> history/command_improvements_log.md
# Document what worked well
echo "" >> history/command_improvements_log.md

echo "✅ Command improvements logged and applied"
```

#### Step 11: Generate Session Summary

```json
{
  "session_id": "nextfive_YYYYMMDD_HHMMSS",
  "execution_timestamp": "2025-09-11T17:00:00Z",
  
  "prediction_accuracy": {
    "discovery_phase": {
      "predicted_failing_tests": 5,
      "actual_failing_tests": 7, 
      "accuracy": "70%",
      "improvement_needed": "Better integration test analysis"
    },
    "implementation_phase": {
      "predicted_time": "18 hours",
      "actual_time": "22 hours",
      "accuracy": "82%", 
      "improvement_needed": "Account for infrastructure complexity"
    },
    "overall_accuracy": "78%"
  },

  "execution_performance": {
    "total_time": "24 hours",
    "phase_breakdown": {
      "discovery": "45 minutes",
      "implementation": "22 hours", 
      "validation": "30 minutes",
      "submission": "15 minutes",
      "jira_updates": "5 minutes"
    },
    "success_rate": "100%",
    "issues_encountered": 2
  },

  "learning_outcomes": {
    "command_improvements_made": 4,
    "prediction_model_updates": 3,
    "workflow_optimizations": 2,
    "success_patterns_documented": 5
  },

  "business_results": {
    "tickets_completed": 5,
    "integration_tests_improved": "+4 passing tests",
    "mr_created": "https://github.com/nortal/CMZ-chatbots/pull/24",
    "jira_tickets_updated": "All successful"
  },

  "next_iteration_improvements": [
    "Discovery phase should include git log analysis for recent test changes",
    "Implementation time estimates need infrastructure complexity factor",
    "Validation should include more comprehensive error scenario testing",
    "Submission MR descriptions can be further streamlined"
  ]
}
```

## Success Criteria

- **Complete Workflow Execution**: All phases (discovery → implementation → validation → submission → jira updates) completed successfully
- **Prediction Validation**: Predictions compared with reality, accuracy metrics calculated
- **Command Improvements**: Specific prompt updates applied based on lessons learned
- **Learning Documentation**: All insights logged to command_improvements_log.md
- **Business Value Delivered**: 5 tickets implemented, MR created, Jira updated
- **Self-Improvement**: Next execution should be more accurate and efficient

## Continuous Learning Benefits

1. **Increasing Accuracy**: Each session improves prediction quality
2. **Workflow Optimization**: Bottlenecks identified and resolved
3. **Pattern Recognition**: Successful approaches codified and reused
4. **Risk Mitigation**: Known failure modes predicted and avoided
5. **Efficiency Gains**: Time estimates become more reliable
6. **Quality Improvement**: Better validation and testing approaches

The system continuously learns from each execution, making every subsequent `/nextfive` run more accurate, efficient, and reliable.