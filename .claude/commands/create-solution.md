# Create Solution Prompt Generator

**Purpose**: Meta-prompt system that generates comprehensive command prompts with sequential reasoning, advice documentation, and integrated project documentation.

**Usage**: `/create-solution <description of what the new prompt should do>`

## Context
This is a meta-prompt system that creates other prompts following CMZ project standards. It ensures consistency, completeness, and proper documentation integration across all custom commands.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically analyze requirements and generate the complete solution:

### Phase 1: Requirements Analysis (Required)
**Use Sequential Reasoning to:**
1. **Parse Request**: Analyze the description to understand the core functionality needed
2. **Identify Domain**: Determine if this is API development, testing, deployment, or infrastructure
3. **Assess Complexity**: Evaluate scope (simple utility vs complex multi-step process)
4. **Define Success Criteria**: What constitutes a successful implementation of this prompt
5. **Integration Points**: How this prompt will work with existing CMZ workflows

**Key Questions for Sequential Analysis:**
- What specific problem does this prompt solve?
- What inputs and outputs are required?
- What validation steps are needed?
- How does this integrate with existing CMZ development patterns?
- What are the potential failure scenarios and edge cases?

### Phase 2: Prompt Design (Systematic)
**Design Structure Following CMZ Standards:**

#### Step 1: Analyze Similar Patterns
```bash
# Examine existing prompts for patterns
ls .claude/commands/
grep -r "Sequential Reasoning" .claude/commands/
grep -r "Phase [0-9]" .claude/commands/
```

#### Step 2: Define Prompt Structure
Based on successful patterns like `create_tracking_version.md` and `/nextfive`:
- **Purpose Statement**: Clear objective and context
- **Sequential Reasoning Phases**: 3-4 systematic phases
- **Implementation Details**: Step-by-step execution instructions
- **Integration Points**: How it works with existing systems
- **Quality Gates**: Validation and success criteria
- **Error Handling**: Common failure scenarios and solutions

#### Step 3: Create Comprehensive Documentation
Generate the following files:
1. **Main Prompt**: `.claude/commands/{solution-name}.md`
2. **Advice File**: `{SOLUTION-NAME}-ADVICE.md`
3. **Update CLAUDE.md**: Add reference line

### Phase 3: Implementation (Automated)
**Implementation Order (Follow Exactly):**

#### Step 1: Generate Prompt File Name
```bash
# Convert description to kebab-case filename
SOLUTION_NAME=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
PROMPT_FILE=".claude/commands/${SOLUTION_NAME}.md"
ADVICE_FILE="${SOLUTION_NAME^^}-ADVICE.md"  # Convert to uppercase for advice file
```

#### Step 2: Create Main Prompt with Sequential Reasoning
Template structure:
```markdown
# [Solution Name]

**Purpose**: [Clear purpose statement]

## Context
[Problem this solves and how it fits into CMZ project]

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically [core objective]:

### Phase 1: [Analysis/Planning Phase]
**Use Sequential Reasoning to:**
1. **[Key analysis step 1]**
2. **[Key analysis step 2]**
3. **[Key analysis step 3]**

**Key Questions for Sequential Analysis:**
- [Domain-specific questions]

### Phase 2: [Implementation Phase]
**Implementation Order (Follow Exactly):**

#### Step 1: [First implementation step]
#### Step 2: [Second implementation step]
#### Step N: [Final implementation step]

### Phase 3: [Validation Phase]
**Validation Checklist:**
- [ ] [Success criteria 1]
- [ ] [Success criteria 2]

### Phase 4: [Documentation/Integration Phase] (if applicable)

## Implementation Details
[Specific technical details, commands, code patterns]

## Integration Points
[How this works with existing CMZ systems]

## Quality Gates
[Mandatory validation before completion]

## Success Criteria
[What constitutes successful execution]

## References
- `{SOLUTION-NAME}-ADVICE.md` - Best practices and troubleshooting
```

#### Step 3: Create Advice File
Template structure focusing on:
- **Best Practices**: When and how to use effectively
- **Common Pitfalls**: What typically goes wrong and solutions
- **Integration Guidelines**: How to work with other CMZ systems
- **Troubleshooting**: Diagnostic and recovery procedures
- **Advanced Usage**: Complex scenarios and optimizations

#### Step 4: Update CLAUDE.md
Add reference line in appropriate section with clear description of purpose.

### Phase 4: Validation & Documentation (Essential)
**Validation Checklist:**
1. **Prompt Structure**: Follows CMZ sequential reasoning pattern
2. **Documentation Complete**: All required files created
3. **CLAUDE.md Updated**: Reference added in logical location
4. **Advice Quality**: Comprehensive best practices and troubleshooting
5. **Integration Verified**: Works with existing CMZ workflows
6. **Error Handling**: Common failure scenarios addressed

## Implementation Template

### Command Processing
When processing `/create-solution <description>`:

1. **Parse Description**: Extract core functionality requirements
2. **Use Sequential Reasoning**: Plan comprehensive solution
3. **Generate Files**: Create all required documentation files
4. **Validate Structure**: Ensure compliance with CMZ standards
5. **Update Project**: Add references to main documentation

### File Naming Convention
- **Prompt File**: `.claude/commands/{kebab-case-name}.md`
- **Advice File**: `{UPPERCASE-KEBAB-CASE-NAME}-ADVICE.md`
- **Reference Description**: Concise 1-line description for CLAUDE.md

### Content Standards
- **Sequential Reasoning**: Always use MCP Sequential Thinking for complex analysis
- **Phase Structure**: 3-4 systematic phases with clear objectives
- **CMZ Integration**: Reference existing patterns and workflows
- **Quality Gates**: Mandatory validation steps
- **Error Handling**: Proactive problem identification and solutions

## Examples

### Example Usage 1: API Testing
```
/create-solution automated API endpoint validation with comprehensive error checking and performance metrics
```

**Expected Output:**
- `.claude/commands/automated-api-endpoint-validation.md` (main prompt)
- `AUTOMATED-API-ENDPOINT-VALIDATION-ADVICE.md` (best practices)
- CLAUDE.md updated with reference to API validation automation

### Example Usage 2: Database Management
```
/create-solution DynamoDB table migration and data consistency validation
```

**Expected Output:**
- `.claude/commands/dynamodb-table-migration.md` (main prompt)
- `DYNAMODB-TABLE-MIGRATION-ADVICE.md` (best practices)
- CLAUDE.md updated with reference to database migration tools

### Example Usage 3: Deployment Automation
```
/create-solution Docker container health monitoring with automated rollback capabilities
```

**Expected Output:**
- `.claude/commands/docker-container-health-monitoring.md` (main prompt)
- `DOCKER-CONTAINER-HEALTH-MONITORING-ADVICE.md` (best practices)
- CLAUDE.md updated with reference to deployment automation

## Integration with CMZ Project

### Existing Pattern Compliance
- **OpenAPI-First Development**: Respect API specification patterns
- **Docker Workflow**: Integration with make commands and containers
- **Git Workflow**: Feature branch patterns and merge request processes
- **Quality Standards**: Security scanning, testing, and validation
- **MCP Server Usage**: Leverage appropriate MCP servers for functionality

### Quality Standards
- **Sequential Reasoning**: Always required for complex multi-step prompts
- **Comprehensive Documentation**: Both main prompt and advice file
- **Error Handling**: Proactive identification of failure scenarios
- **Integration Testing**: Validation with existing CMZ workflows
- **Professional Standards**: Business-grade documentation and implementation

## Success Criteria
1. **Functional Prompt**: Generated prompt works as intended for described purpose
2. **Complete Documentation**: Both main prompt and advice file comprehensive
3. **CMZ Integration**: Works seamlessly with existing project patterns
4. **Quality Compliance**: Meets all CMZ development and documentation standards
5. **Maintainable**: Clear structure that can be updated and improved over time

## Quality Gates

### Mandatory Validation Before Completion
- [ ] Prompt follows sequential reasoning pattern
- [ ] All required files created (prompt, advice, CLAUDE.md update)
- [ ] Documentation is comprehensive and actionable
- [ ] Integration points with CMZ project clearly defined
- [ ] Error handling and troubleshooting guidance included
- [ ] Examples provided for key usage scenarios
- [ ] File naming follows project conventions

### Testing the Generated Prompt
- [ ] Generated prompt can be executed successfully
- [ ] Sequential reasoning phases are logical and complete
- [ ] Implementation steps are clear and actionable
- [ ] Validation steps catch common errors
- [ ] Advice file addresses real-world usage scenarios

## Meta-Learning Integration
**IMPORTANT**: After using this meta-prompt to create a new solution, always update `CREATE-SOLUTION-ADVICE.md` with:
- Lessons learned from the prompt creation process
- Patterns that worked well or needed improvement
- Integration challenges and solutions discovered
- Recommendations for future prompt creation

This creates a continuous improvement loop for the meta-prompt system itself.

## References
- `CREATE-SOLUTION-ADVICE.md` - Meta-prompt best practices and lessons learned
- Existing CMZ command prompts for pattern reference
- CMZ project documentation for integration guidelines