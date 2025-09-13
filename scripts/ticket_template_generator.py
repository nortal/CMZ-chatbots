#!/usr/bin/env python3
"""
Ticket Template Generator for /nextfive Command

Generates consistent, high-quality Jira tickets using proven templates
and patterns learned from successful ticket creation.

Key Features:
- Template-driven ticket generation
- Automatic acceptance criteria creation
- Dependency linking support
- Multiple ticket types (TDD, Testing, API, etc.)
- Integration with existing Jira scripts

Usage:
    python scripts/ticket_template_generator.py --template tdd --title "Fast Unit Test Suite"
    python scripts/ticket_template_generator.py --template testing --count 3 --epic PR003946-61
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TicketTemplate(Enum):
    """Available ticket templates."""
    TDD = "tdd"
    TESTING = "testing"
    API_VALIDATION = "api_validation"
    PLAYWRIGHT = "playwright"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"


@dataclass
class AcceptanceCriterion:
    """Represents a single acceptance criterion."""
    given: str
    when: str
    then: str
    and_clause: Optional[str] = None
    test_command: Optional[str] = None
    verification: Optional[str] = None


@dataclass
class TicketSpec:
    """Specification for generating a ticket."""
    template: TicketTemplate
    title: str
    description: str
    story_points: int
    priority: str = "Normal"
    acceptance_criteria: List[AcceptanceCriterion] = None
    dependencies: List[str] = None
    labels: List[str] = None

    def __post_init__(self):
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.dependencies is None:
            self.dependencies = []
        if self.labels is None:
            self.labels = []


class TicketTemplateGenerator:
    """Generates Jira tickets using proven templates."""

    def __init__(self, epic_key: str = "PR003946-61"):
        self.epic_key = epic_key
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[TicketTemplate, Dict]:
        """Load ticket templates based on successful patterns."""
        return {
            TicketTemplate.TDD: {
                "base_story_points": 8,
                "labels": ["tdd", "testing", "development"],
                "description_template": """As a developer, I want {objective} to enable test-driven development practices and improve code quality.

## Background
{background}

## Technical Context
- Testing Framework: pytest, unittest
- Code Coverage: Target >90% coverage
- Test Types: Unit tests with comprehensive mocking
- Development Pattern: Red-Green-Refactor TDD cycle
- Integration: CI/CD pipeline integration

## Scope
{scope}""",
                "acceptance_criteria": [
                    AcceptanceCriterion(
                        given="development team needs to write tests first",
                        when="implementing new functionality",
                        then="verify tests can be written before implementation",
                        and_clause="verify tests fail initially (Red phase)",
                        test_command="pytest tests/unit/ --collect-only",
                        verification="Test collection succeeds, tests initially fail"
                    )
                ]
            },
            TicketTemplate.TESTING: {
                "base_story_points": 5,
                "labels": ["testing", "quality", "validation"],
                "description_template": """As a developer, I want {objective} to ensure comprehensive test coverage and validation.

## Background
{background}

## Technical Context
- Test Types: Unit, integration, E2E, performance
- Frameworks: pytest, Playwright, custom validation
- Coverage: Functional and non-functional requirements
- Automation: CI/CD integration with quality gates

## Scope
{scope}""",
                "acceptance_criteria": [
                    AcceptanceCriterion(
                        given="test suite exists for the functionality",
                        when="tests are executed",
                        then="verify all tests pass with expected coverage",
                        test_command="pytest --cov={module} --cov-report=term-missing",
                        verification="Coverage meets minimum threshold (>80%)"
                    )
                ]
            },
            TicketTemplate.PLAYWRIGHT: {
                "base_story_points": 8,
                "labels": ["playwright", "e2e", "ui-testing", "automation"],
                "description_template": """As a developer, I want {objective} to ensure UI functionality works correctly across all supported browsers.

## Background
{background}

## Technical Context
- Browser Support: Chrome, Firefox, Safari, Edge (desktop + mobile)
- Test Environment: Playwright with 6 browser configurations
- Validation: User workflows, persistence, cross-browser consistency
- Integration: CI/CD pipeline with automated execution

## Scope
{scope}""",
                "acceptance_criteria": [
                    AcceptanceCriterion(
                        given="Playwright tests exist for UI functionality",
                        when="tests run across all 6 browser configurations",
                        then="verify ≥5/6 browsers pass successfully",
                        and_clause="verify critical user workflows function correctly",
                        test_command="FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js",
                        verification="Test results show ≥83% browser success rate"
                    )
                ]
            },
            TicketTemplate.API_VALIDATION: {
                "base_story_points": 5,
                "labels": ["api", "validation", "openapi", "integration"],
                "description_template": """As a developer, I want {objective} to ensure API endpoints function correctly and meet OpenAPI specifications.

## Background
{background}

## Technical Context
- API Framework: Flask/Connexion with OpenAPI 3.0
- Validation: Request/response schema compliance
- Testing: Integration tests with realistic data
- Documentation: OpenAPI specification synchronization

## Scope
{scope}""",
                "acceptance_criteria": [
                    AcceptanceCriterion(
                        given="API endpoints are implemented",
                        when="integration tests execute",
                        then="verify all endpoints return correct HTTP status codes",
                        and_clause="verify response schemas match OpenAPI specification",
                        test_command="curl -s http://localhost:8080/api/v1/{endpoint} | jq '.code'",
                        verification="Status codes: 200/201 for success, appropriate error codes for failures"
                    )
                ]
            }
        }

    def generate_ticket(self, spec: TicketSpec) -> Dict:
        """Generate a complete ticket specification."""
        template = self.templates[spec.template]

        # Format description using template
        description = template["description_template"].format(
            objective=spec.description,
            background=f"Implementation of {spec.title} to improve development workflow.",
            scope=f"Implementation of {spec.title} with comprehensive validation."
        )

        # Combine template and custom acceptance criteria
        all_criteria = template["acceptance_criteria"] + spec.acceptance_criteria

        # Format acceptance criteria for Jira
        formatted_criteria = self._format_acceptance_criteria(all_criteria)

        return {
            "summary": spec.title,
            "description": description + "\n\n" + formatted_criteria,
            "story_points": spec.story_points,
            "priority": spec.priority,
            "labels": list(set(template["labels"] + spec.labels)),
            "dependencies": spec.dependencies,
            "epic": self.epic_key
        }

    def _format_acceptance_criteria(self, criteria: List[AcceptanceCriterion]) -> str:
        """Format acceptance criteria for Jira description."""
        formatted = "## Acceptance Criteria\n\n"

        for i, criterion in enumerate(criteria, 1):
            formatted += f"**AC{i}: {criterion.given.title()}**\n"
            formatted += f"- **Given** {criterion.given}\n"
            formatted += f"- **When** {criterion.when}\n"
            formatted += f"- **Then** {criterion.then}\n"

            if criterion.and_clause:
                formatted += f"- **And** {criterion.and_clause}\n"

            if criterion.test_command:
                formatted += f"- **Test**: `{criterion.test_command}`\n"

            if criterion.verification:
                formatted += f"- **Verification**: {criterion.verification}\n"

            formatted += "\n"

        return formatted

    def generate_script_for_tickets(self, tickets: List[Dict], script_name: str) -> str:
        """Generate a Jira creation script for multiple tickets."""
        script_content = f"""#!/bin/bash

# Generated Ticket Creation Script - {script_name}
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Based on proven ticket creation patterns from create_playwright_validation_tickets.sh

set -e

# Check if required environment variables are set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    exit 1
fi

if [ -z "$JIRA_EMAIL" ]; then
    echo "Error: JIRA_EMAIL environment variable is not set"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"

# Create base64 encoded credentials for Basic Auth
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🎯 Creating {len(tickets)} tickets for {script_name}..."

# Test API connectivity first
echo "🔌 Testing API connectivity..."
test_response=$(curl -s -w "\\nHTTP_STATUS:%{{http_code}}" \\
    -H "Authorization: Basic $JIRA_CREDENTIALS" \\
    -H "Content-Type: application/json" \\
    "$JIRA_BASE_URL/rest/api/3/myself")

test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)

if [ "$test_http_status" != "200" ]; then
    echo "❌ API connectivity test failed"
    exit 1
fi

echo "✅ API connectivity confirmed"

# Arrays to store created ticket keys
declare -a CREATED_TICKETS=()

# Function to add a simple comment
add_simple_comment() {{
    local ticket_id=$1
    local comment_text="$2"

    echo "💬 Adding comment to $ticket_id..."

    # Create temp file with comment JSON
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{{
    "body": {{
        "type": "doc",
        "version": 1,
        "content": [
            {{
                "type": "paragraph",
                "content": [
                    {{
                        "type": "text",
                        "text": "$comment_text"
                    }}
                ]
            }}
        ]
    }}
}}
EOF

    local response=$(curl -s -w "\\nHTTP_STATUS:%{{http_code}}" \\
        -H "Authorization: Basic $JIRA_CREDENTIALS" \\
        -H "Content-Type: application/json" \\
        --data @"$temp_file" \\
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    rm -f "$temp_file"

    if [ "$http_status" = "201" ]; then
        echo "✅ Successfully added comment to $ticket_id"
    else
        echo "❌ Failed to add comment to $ticket_id (HTTP $http_status)"
    fi
}}

# Function to create a Jira ticket
create_ticket() {{
    local summary="$1"
    local description="$2"
    local story_points="$3"
    local issue_type="$4"

    echo "🎫 Creating ticket: $summary"

    # Create temp file with ticket JSON
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{{
    "fields": {{
        "project": {{
            "key": "PR003946"
        }},
        "summary": "$summary",
        "description": {{
            "type": "doc",
            "version": 1,
            "content": [
                {{
                    "type": "paragraph",
                    "content": [
                        {{
                            "type": "text",
                            "text": "$description"
                        }}
                    ]
                }}
            ]
        }},
        "issuetype": {{
            "name": "$issue_type"
        }},
        "customfield_10225": {{
            "value": "Billable",
            "id": "10564"
        }},
        "customfield_10014": "{self.epic_key}"
    }}
}}
EOF

    local response=$(curl -s -w "\\nHTTP_STATUS:%{{http_code}}" \\
        -H "Authorization: Basic $JIRA_CREDENTIALS" \\
        -H "Content-Type: application/json" \\
        --data @"$temp_file" \\
        "$JIRA_BASE_URL/rest/api/3/issue")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    rm -f "$temp_file"

    if [ "$http_status" = "201" ]; then
        local ticket_key=$(echo "$response" | sed '/HTTP_STATUS:/d' | jq -r '.key')
        echo "✅ Successfully created ticket: $ticket_key"
        CREATED_TICKETS+=("$ticket_key")

        # Add story points as a comment
        echo "💬 Adding story points comment to $ticket_key..."
        sleep 1
        add_simple_comment "$ticket_key" "Story Points (soft estimate): $story_points — 1 point = 0.5 day"

        return 0
    else
        echo "❌ Failed to create ticket: $summary (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
        return 1
    fi
}}

"""

        # Add ticket creation calls
        for i, ticket in enumerate(tickets):
            escaped_description = ticket['description'].replace('"', '\\"').replace('\n', '\\n')
            script_content += f"""
# Create Ticket {i+1}: {ticket['summary']}
create_ticket \\
    "{ticket['summary']}" \\
    "{escaped_description}" \\
    "{ticket['story_points']}" \\
    "Task"

sleep 2
"""

        # Add summary
        script_content += f"""
echo ""
echo "🎉 Successfully created all {script_name} tickets!"
echo ""
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for ticket in "${{CREATED_TICKETS[@]}}"; do
    echo "✅ $ticket - https://nortal.atlassian.net/browse/$ticket"
done
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 All tickets are linked to Parent Epic: {self.epic_key}"
echo "💰 All tickets are marked as Billable"
echo "📝 Story points added as comments for estimation"
"""

        return script_content

    def generate_tdd_improvement_tickets(self) -> List[Dict]:
        """Generate the 5 TDD improvement tickets from our analysis."""
        tdd_tickets = [
            TicketSpec(
                template=TicketTemplate.TDD,
                title="Comprehensive Test Data Factory and Fixtures Framework",
                description="realistic, consistent test data for all domain entities to enable test-first development",
                story_points=5,
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="developers need to write failing tests quickly",
                        when="creating test scenarios for animals, families, users, conversations",
                        then="verify test data factory provides realistic data within 100ms",
                        and_clause="verify data includes boundary values and edge cases",
                        test_command="python -c 'from tests.fixtures import TestDataFactory; print(TestDataFactory.generate_animal())'",
                        verification="Factory generates consistent, realistic test data with proper relationships"
                    )
                ],
                labels=["test-data", "fixtures", "tdd-foundation"]
            ),
            TicketSpec(
                template=TicketTemplate.API_VALIDATION,
                title="OpenAPI Contract Testing and Validation Framework",
                description="contract validation between OpenAPI specifications and implementation",
                story_points=8,
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="OpenAPI specifications define API contracts",
                        when="generated controllers and business logic are implemented",
                        then="verify implementation matches specification exactly",
                        and_clause="verify contract violations fail with clear error messages",
                        test_command="python scripts/validate_openapi_contracts.py --spec backend/api/openapi_spec.yaml",
                        verification="All endpoints conform to OpenAPI specification, violations detected automatically"
                    )
                ],
                labels=["contract-testing", "openapi", "api-validation"]
            ),
            TicketSpec(
                template=TicketTemplate.TDD,
                title="Fast Unit Test Suite with Comprehensive Mocking",
                description="unit tests that execute in <100ms with full dependency mocking",
                story_points=13,
                dependencies=["Test Data Factory"],
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="comprehensive unit test suite exists",
                        when="tests execute with mocked dependencies",
                        then="verify all unit tests complete in <100ms per test",
                        and_clause="verify AWS services, DynamoDB, and file system are fully mocked",
                        test_command="time pytest tests/unit/ --no-cov -q",
                        verification="Test execution time <100ms per test, no external dependencies called"
                    )
                ],
                labels=["fast-tests", "mocking", "unit-testing", "performance"]
            ),
            TicketSpec(
                template=TicketTemplate.TDD,
                title="Developer TDD Workflow Integration Tools",
                description="seamless TDD workflow with watch modes, IDE integration, and automated tooling",
                story_points=8,
                dependencies=["Fast Unit Test Suite"],
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="fast unit tests are available",
                        when="developer makes code changes",
                        then="verify watch mode automatically re-runs relevant tests within 200ms",
                        and_clause="verify pre-commit hooks prevent commits with failing tests",
                        test_command="pytest-watch tests/unit/ --clear",
                        verification="Watch mode responsive, pre-commit hooks functional, IDE integration working"
                    )
                ],
                labels=["workflow", "automation", "developer-experience"]
            ),
            TicketSpec(
                template=TicketTemplate.API_VALIDATION,
                title="Automated Test Generation and Maintenance",
                description="automatic test generation from OpenAPI specifications with maintenance tools",
                story_points=10,
                dependencies=["Contract Testing Framework"],
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="OpenAPI specifications exist for endpoints",
                        when="test generation script executes",
                        then="verify test stubs are generated for all endpoints",
                        and_clause="verify generated tests include validation and contract checking",
                        test_command="python scripts/generate_tests_from_openapi.py --spec openapi_spec.yaml --output tests/generated/",
                        verification="Generated tests provide >80% coverage, follow testing patterns, maintainable"
                    )
                ],
                labels=["test-generation", "automation", "maintenance"]
            )
        ]

        return [self.generate_ticket(spec) for spec in tdd_tickets]


def main():
    """Main entry point for ticket template generator."""
    parser = argparse.ArgumentParser(description='Generate Jira tickets using proven templates')
    parser.add_argument('--template', choices=[t.value for t in TicketTemplate],
                       help='Ticket template type')
    parser.add_argument('--title', required=True, help='Ticket title/summary')
    parser.add_argument('--description', help='Ticket objective description')
    parser.add_argument('--story-points', type=int, help='Story point estimate')
    parser.add_argument('--epic', default='PR003946-61', help='Parent epic key')
    parser.add_argument('--output-format', choices=['json', 'script'], default='json',
                       help='Output format')
    parser.add_argument('--generate-tdd', action='store_true',
                       help='Generate TDD improvement tickets')
    parser.add_argument('--output-file', help='Output file path')

    args = parser.parse_args()

    generator = TicketTemplateGenerator(args.epic)

    if args.generate_tdd:
        # Generate TDD improvement tickets
        tickets = generator.generate_tdd_improvement_tickets()

        if args.output_format == 'script':
            script_content = generator.generate_script_for_tickets(tickets, "TDD Improvement")
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(script_content)
                print(f"✅ TDD improvement script written to {args.output_file}")
            else:
                print(script_content)
        else:
            output = {
                'tickets': tickets,
                'generated_at': datetime.now().isoformat(),
                'epic': args.epic
            }
            output_str = json.dumps(output, indent=2)

            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(output_str)
                print(f"✅ TDD improvement tickets written to {args.output_file}")
            else:
                print(output_str)
    else:
        # Generate single ticket
        if not args.template or not args.description:
            print("❌ --template and --description are required for single ticket generation")
            sys.exit(1)

        spec = TicketSpec(
            template=TicketTemplate(args.template),
            title=args.title,
            description=args.description,
            story_points=args.story_points or 5
        )

        ticket = generator.generate_ticket(spec)

        if args.output_format == 'script':
            script_content = generator.generate_script_for_tickets([ticket], f"Single Ticket - {args.title}")
            output_str = script_content
        else:
            output_str = json.dumps(ticket, indent=2)

        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output_str)
            print(f"✅ Ticket written to {args.output_file}")
        else:
            print(output_str)


if __name__ == '__main__':
    main()