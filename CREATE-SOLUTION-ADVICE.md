# Create Solution Meta-Prompt - Best Practices & Lessons Learned

## Overview
This advice file provides best practices, lessons learned, and troubleshooting guidance for the meta-prompt system that generates new command prompts for the CMZ project.

## When to Use Create-Solution

### ✅ EXCELLENT Use Cases:
- **Repetitive Multi-Step Processes**: Tasks that require 3+ systematic steps
- **Domain-Specific Workflows**: API testing, database operations, deployment procedures
- **Integration-Heavy Tasks**: Operations that touch multiple CMZ systems
- **Quality-Critical Processes**: Tasks requiring validation, error handling, and rollback
- **Knowledge Preservation**: Capturing complex procedures for team handoff
- **Standardization Needs**: Ensuring consistent approach across similar tasks

### ⚠️ CONSIDER Alternatives For:
- **Simple One-Off Tasks**: Single commands or trivial operations
- **Highly Variable Processes**: Tasks that change significantly each time
- **Exploration/Discovery**: Research tasks without defined outcomes
- **Personal Utilities**: Tools only one person will use

### ❌ DON'T Use For:
- **Documentation Only**: Pure reference material without executable steps
- **Debugging Specific Issues**: One-time problem solving
- **Brainstorming Sessions**: Open-ended ideation without clear deliverables

## Best Practices for Prompt Creation

### Description Writing
**Effective Descriptions:**
- `automated API endpoint validation with comprehensive error checking and performance metrics`
- `DynamoDB table migration with data consistency validation and rollback capabilities`
- `Docker container deployment with health monitoring and automated scaling`

**Poor Descriptions:**
- `fix the API` (too vague)
- `make everything work better` (no specific outcome)
- `do some database stuff` (unclear scope)

### Sequential Reasoning Integration
**Always Structure as:**
1. **Analysis Phase**: Understanding current state and requirements
2. **Planning Phase**: Designing systematic approach
3. **Implementation Phase**: Step-by-step execution
4. **Validation Phase**: Quality gates and success verification

**Key Principles:**
- Each phase should have clear inputs and outputs
- Sequential reasoning should predict potential issues
- Include decision trees for handling variations
- Build in checkpoints for course correction

### Documentation Standards
**Main Prompt Must Include:**
- Clear purpose statement with context
- Sequential reasoning phases with specific steps
- Implementation details with exact commands/code
- Integration points with existing CMZ systems
- Quality gates and success criteria
- Error handling for common failure scenarios

**Advice File Must Address:**
- When and how to use the prompt effectively
- Common pitfalls and their solutions
- Advanced usage scenarios and optimizations
- Troubleshooting procedures with diagnostic commands
- Integration guidelines with other CMZ tools

## Common Pitfalls & Solutions

### 1. Overly Generic Prompts
**Problem**: Description too broad, resulting in unfocused prompt

**Solution:**
- Break complex requests into specific, actionable components
- Focus on one primary objective with clear success criteria
- Use concrete examples in the description

**Example Fix:**
- Before: `improve the development workflow`
- After: `automated code quality validation with pre-commit hooks and CI integration`

### 2. Missing Integration Context
**Problem**: Generated prompt doesn't work well with existing CMZ patterns

**Solution:**
- Always reference existing CMZ documentation and patterns
- Include integration points with make commands, Docker workflow, git patterns
- Test generated prompts against actual CMZ development scenarios

### 3. Insufficient Error Handling
**Problem**: Generated prompts fail without clear guidance

**Solution:**
- Include comprehensive error scenarios in sequential reasoning
- Provide diagnostic commands and recovery procedures
- Address both technical failures and user errors

### 4. Poor File Naming
**Problem**: Inconsistent or unclear file naming patterns

**Solution:**
```bash
# Good naming pattern
description="automated API endpoint validation"
filename=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
# Results in: automated-api-endpoint-validation.md
```

### 5. Inadequate Quality Gates
**Problem**: Generated prompts lack proper validation steps

**Solution:**
- Always include comprehensive validation checklists
- Define clear success criteria that can be objectively measured
- Include both functional and integration testing requirements

## Advanced Usage Patterns

### Multi-Domain Solutions
For prompts that span multiple technical domains:
```markdown
### Domain Integration Strategy
- **API Layer**: OpenAPI specification compliance
- **Data Layer**: DynamoDB consistency patterns
- **Infrastructure**: Docker and AWS integration
- **Testing**: Playwright E2E and unit test validation
```

### Conditional Logic Handling
For prompts with multiple execution paths:
```markdown
### Execution Strategy Analysis
**Use Sequential Reasoning to determine:**
- Environment-specific requirements (dev/staging/prod)
- Dependency resolution order
- Rollback strategies for each decision point
```

### Template Reusability
Create reusable components for common patterns:
- AWS service integration templates
- Docker workflow templates
- Testing validation templates
- Git workflow templates

## Integration Guidelines

### CMZ Project Standards
**Always Reference:**
- OpenAPI-first development patterns
- Docker containerization workflows
- DynamoDB data access patterns
- Git feature branch workflows
- Quality gates and validation requirements

**Integration Checkpoints:**
- Works with existing make commands
- Respects Docker container lifecycle
- Compatible with current CI/CD processes
- Follows established git workflow patterns

### MCP Server Utilization
**Recommend Appropriate MCP Servers:**
- **Sequential**: For complex analysis and planning phases
- **Context7**: For framework-specific implementation guidance
- **Magic**: For UI component generation needs
- **Morphllm**: For bulk code transformation requirements
- **Playwright**: For browser-based testing and validation

### Quality Standards Alignment
**Ensure Generated Prompts:**
- Include security scanning and validation steps
- Address GitHub Advanced Security requirements
- Follow professional code review processes
- Include comprehensive testing strategies

## Troubleshooting Common Issues

### Generated Prompt Doesn't Work
**Diagnostic Steps:**
1. Check if description was too vague or broad
2. Verify all required files were created
3. Test sequential reasoning phases individually
4. Validate integration with existing CMZ patterns

**Recovery Actions:**
```bash
# Regenerate with more specific description
/create-solution [more specific description]

# Check existing patterns for reference
ls .claude/commands/
grep -r "similar-functionality" .claude/commands/
```

### File Naming Conflicts
**Problem**: Generated filename conflicts with existing files

**Solution:**
```bash
# Check for existing files before generation
ls .claude/commands/ | grep -i "keyword-from-description"
ls | grep -i "KEYWORD-FROM-DESCRIPTION-ADVICE.md"

# Use more specific descriptions to avoid conflicts
```

### Incomplete Documentation
**Problem**: Generated advice file lacks sufficient detail

**Solution:**
- Review the description for missing context
- Add domain-specific requirements to the request
- Reference similar existing advice files for completeness patterns

## Performance Optimization

### Description Optimization
- **Specific Keywords**: Use domain-specific terms (API, DynamoDB, Docker, etc.)
- **Clear Scope**: Define boundaries and limitations explicitly
- **Concrete Outcomes**: Specify measurable success criteria

### Template Efficiency
- Reuse proven patterns from existing successful prompts
- Reference established CMZ documentation and workflows
- Leverage existing MCP server capabilities rather than recreating functionality

## Team Collaboration Guidelines

### Sharing Generated Prompts
1. **Test Thoroughly**: Always validate generated prompts work as intended
2. **Document Usage**: Add real-world examples to advice files
3. **Update CLAUDE.md**: Ensure references are clear and helpful
4. **Version Control**: Commit all generated files together

### Continuous Improvement
**After Each Usage:**
- Update this advice file with lessons learned
- Note patterns that worked well or needed improvement
- Document integration challenges and solutions
- Recommend improvements to the meta-prompt system

## Meta-Learning Integration

### Lessons Learned Updates
Each time you use `/create-solution`, add to this section:

#### 2025-01-14: Initial Meta-Prompt Creation
- **Challenge**: Balancing comprehensive structure with usability
- **Solution**: Used existing successful prompt patterns (create_tracking_version.md) as templates
- **Learning**: Sequential reasoning phases are critical for complex prompt reliability
- **Recommendation**: Always include 4 phases: Analysis → Planning → Implementation → Validation

#### 2025-01-14: Meta-Prompt System Implementation Complete
- **Challenge**: Creating a system that generates consistent, high-quality prompts
- **Solution**: Built comprehensive template system with file naming conventions, structured phases, and integration patterns
- **Learning**: Meta-prompt systems require extensive examples and clear usage patterns to be effective
- **Key Success Factors**:
  - Template-driven approach ensures consistency
  - Integration with existing CMZ patterns is critical
  - Comprehensive advice files are essential for adoption
  - Clear file naming conventions prevent conflicts
  - Quality gates ensure generated prompts actually work
- **Recommendation**: Always test generated prompts immediately after creation
- **Integration Pattern**: Meta-prompt → Sequential Reasoning → Implementation → Validation → Documentation

#### [Future entries will be added here as the system is used]

### Pattern Evolution
Track which prompt patterns prove most successful:
- Sequential reasoning with 4 phases: PROVEN effective
- Integration with existing CMZ workflows: CRITICAL for adoption
- Comprehensive error handling: ESSENTIAL for reliability
- Clear file naming conventions: IMPORTANT for maintainability

## Advanced Scenarios

### Multi-Prompt Integration
For complex systems requiring multiple related prompts:
```markdown
### Prompt Ecosystem Design
- **Core Prompt**: Main functionality
- **Setup Prompt**: Environment preparation
- **Validation Prompt**: Quality assurance
- **Cleanup Prompt**: Resource management
```

### Version Management
For prompts that evolve over time:
```markdown
### Prompt Versioning Strategy
- Include version indicators in documentation
- Maintain backward compatibility when possible
- Document breaking changes clearly
- Provide migration guidance between versions
```

## Related Documentation
- `.claude/commands/create-solution.md` - Meta-prompt implementation
- `.claude/commands/create_tracking_version.md` - Example of well-structured prompt
- CMZ project documentation for integration patterns