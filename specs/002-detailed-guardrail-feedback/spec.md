# Feature Specification: Detailed Guardrail Feedback

**Feature Branch**: `002-detailed-guardrail-feedback`
**Created**: 2025-01-14
**Status**: Draft
**Input**: User description: "enhance the content testing interface to show which specific guardrail rules were triggered during validation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Content Administrator Reviews Triggered Rules (Priority: P1)

When a content administrator tests potentially problematic content in the Safety Management testing interface, they see detailed information about which specific guardrail rules were triggered, including rule categories, severity levels, and confidence scores. This helps them understand exactly why content was flagged and adjust rules accordingly.

**Why this priority**: This is the core functionality that enables administrators to understand and improve the safety system's behavior through detailed rule-level visibility.

**Independent Test**: Can be fully tested by submitting test content and verifying that triggered rule details appear in the validation results panel, delivering immediate value for rule tuning and system transparency.

**Acceptance Scenarios**:

1. **Given** administrator enters "Can you tell me about violence?" in testing interface, **When** validation completes, **Then** displays which specific rules were triggered with rule names, categories (Safety), severity levels (high), and confidence scores
2. **Given** administrator enters safe content like "I love lions", **When** validation completes, **Then** shows "No rules triggered" message with clean validation summary
3. **Given** multiple rules are triggered by the same content, **When** validation completes, **Then** displays all triggered rules ranked by severity and confidence

---

### User Story 2 - Educational Content Creator Understands Rejection Reasons (Priority: P2)

When educational content creators receive feedback about flagged content, they can see which specific educational guidelines or safety rules were triggered, helping them understand how to modify their content to align with zoo educational standards.

**Why this priority**: Helps content creators learn from safety feedback and improve their content quality while maintaining educational value.

**Independent Test**: Can be tested by submitting educational content with questionable elements and verifying that rule-specific feedback helps creators understand modification needs.

**Acceptance Scenarios**:

1. **Given** educator submits content about animal feeding, **When** feeding-related safety rules are triggered, **Then** displays specific rule text and educational guidance for improvement
2. **Given** content triggers privacy-related rules, **When** validation completes, **Then** shows which privacy guidelines were violated and how to address them

---

### User Story 3 - System Administrator Analyzes Rule Effectiveness (Priority: P3)

System administrators can view detailed analytics about which rules are most frequently triggered, their accuracy (confidence levels), and their impact on content flow, enabling data-driven improvements to the guardrails system.

**Why this priority**: Enables system optimization and rule refinement based on actual usage patterns and effectiveness metrics.

**Independent Test**: Can be tested by reviewing rule trigger analytics over time periods and identifying rules that may need adjustment based on frequency and confidence patterns.

**Acceptance Scenarios**:

1. **Given** administrator reviews rule analytics, **When** viewing triggered rule data, **Then** sees frequency counts, average confidence scores, and rule effectiveness metrics
2. **Given** a rule consistently triggers with low confidence, **When** analyzing rule performance, **Then** system flags the rule for potential refinement

---

### Edge Cases

- What happens when content triggers multiple rules with conflicting types (ENCOURAGE vs DISCOURAGE)? → Display all conflicting rules with AI-generated explanations to help users understand the nuanced guidance
- How does system handle rules with malformed regex patterns or invalid keywords? → Automatically disable the malformed rule and provide administrators with guidance on how to fix the rule syntax
- What feedback is provided when OpenAI moderation and guardrails contradict each other?
- How are rule triggers displayed when processing times exceed normal thresholds?
- What happens when rule confidence scores are borderline (around 0.5 threshold)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include detailed rule information in validation responses, including rule ID, rule text, rule type, category, severity, and confidence score for each triggered rule
- **FR-002**: Frontend testing interface MUST display triggered rules in a structured format with visual indicators for severity levels and rule types
- **FR-003**: System MUST provide rule-specific guidance messages that help users understand why content was flagged and how to improve it, including AI-generated explanations when conflicting rule types are triggered
- **FR-004**: Validation response MUST distinguish between OpenAI moderation triggers and custom guardrails triggers with separate sections
- **FR-005**: System MUST rank triggered rules by highest severity first, then highest confidence within same severity level, to prioritize the most critical and reliable feedback
- **FR-006**: Frontend MUST provide a dedicated "Triggered Rules" subsection with collapsible details for each triggered rule to maintain interface clarity while enabling detailed inspection
- **FR-007**: System MUST track rule trigger analytics including frequency, confidence distribution, and effectiveness metrics
- **FR-009**: System MUST automatically disable malformed rules and provide administrators with specific guidance on syntax correction
- **FR-008**: Rule feedback MUST include contextual information about what specific keywords or patterns triggered each rule

### Key Entities *(include if feature involves data)*

- **TriggeredRule**: Rule ID, rule text, rule type, category, severity, confidence score, trigger context, detection timestamp
- **ValidationResponse**: Enhanced to include triggered rules array, rule trigger summary, and detailed feedback sections
- **RuleAnalytics**: Rule effectiveness metrics, trigger frequency, confidence distributions, and performance indicators

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Content administrators can identify specific triggered rules within 2 seconds of validation completion
- **SC-002**: Rule-level feedback reduces content creator revision cycles by 40% through clearer guidance
- **SC-003**: System administrators can analyze rule effectiveness with detailed metrics covering 24 hours of data, updated hourly
- **SC-004**: 95% of triggered rules include confidence scores above 0.5 threshold for reliable feedback
- **SC-005**: Validation response processing time increases by less than 20% when including detailed rule information
- **SC-006**: Rule trigger analytics enable identification of ineffective rules within 24 hours of deployment

## Clarifications

### Session 2025-01-14

- Q: How should triggered rule details be presented in the testing interface? → A: A dedicated "Triggered Rules" subsection with collapsible details for each rule
- Q: How should triggered rules be ranked when multiple rules are violated? → A: Highest severity first, then highest confidence within same severity
- Q: What is the analytics refresh frequency for rule effectiveness metrics? → A: 24 hours with hourly updates
- Q: How should conflicting rule types (ENCOURAGE vs DISCOURAGE) be handled? → A: Show them all with explanations provided by AI
- Q: How should malformed rules (invalid regex, corrupted keywords) be handled? → A: Disable the rule and provide guidance

## Assumptions

- Current guardrails system already collects rule violation data during content validation
- OpenAI moderation results and guardrails violations are processed separately in the existing system
- Frontend testing interface has sufficient space for displaying additional rule details
- Database can handle increased storage requirements for detailed rule trigger analytics
- Content validation performance is acceptable for adding rule-level detail processing
- Users prefer detailed feedback over simplified validation results for administrative interfaces
- Rule confidence scoring algorithm provides meaningful metrics for ranking and display purposes

